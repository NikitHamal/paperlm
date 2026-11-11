"""PaperSetterEngine — grammar/schema-constrained mock-test & model-paper generator on top of PaperLM-Tiny.

Guarantees (enforced token by token, then re-verified):
  * strict item schema (MCQ: q -> 4 options -> key -> why ;  written: q -> parts(+marks) -> [OR twin] -> [rubric])
  * balanced $...$ / $$...$$ math, balanced braces, whitelisted LaTeX commands only, no TeX outside math
  * answer key in {a,b,c,d}; 4 distinct options; part marks add up to the item marks
  * no n-gram loops / repeated tokens; allowed character set only (no mojibake)
  * if every retry fails the engine raises ItemGenerationError — it NEVER emits unvalidated text.
Backends: TorchBackend (checkpoint) and OrtBackend (ONNX, same KV-cache interface as the Web/Android SDK).
"""
import json, math, os, random, re, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "data")); sys.path.insert(0, "/tmp/paperlm/data"); sys.path.insert(0, HERE); sys.path.insert(0, "/tmp/paperlm/engine")
import validator as V
import verify as VF
from tokenizers import Tokenizer

class ItemGenerationError(Exception): pass

# ------------------------------------------------------------------ backends
class TorchBackend:
    def __init__(self, ckpt, device="cuda"):
        import torch
        sys.path.insert(0, os.path.join(HERE, "..", "model")); sys.path.insert(0, "/tmp/paperlm/model")
        from architecture import PaperLM, PaperLMConfig
        d = torch.load(ckpt, map_location=device)
        self.cfg = PaperLMConfig(**d["cfg"]); self.m = PaperLM(self.cfg).to(device).eval(); self.m.load_state_dict(d["model"]); self.m.return_cache = True
        self.torch, self.dev = torch, device
    def start(self):
        c = self.cfg; z = self.torch.zeros(c.n_layers, 1, c.n_heads, 0, c.d_model // c.n_heads, device=self.dev); return (z, z.clone())
    @property
    def max_seq(self): return self.cfg.max_seq
    def step(self, ids, st):
        with self.torch.no_grad():
            lg, k, v = self.m(self.torch.tensor([ids], device=self.dev), st[0], st[1])
        return lg[0, -1].float().cpu().numpy(), (k, v)

class OrtBackend:
    def __init__(self, path):
        import onnxruntime as ort
        self.s = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
        sh = self.s.get_inputs()[1].shape; self.L, self.H, self.D = sh[0], sh[2], sh[4]; self.max_seq = 1024
    def start(self):
        z = np.zeros((self.L, 1, self.H, 0, self.D), np.float32); return (z, z)
    def step(self, ids, st):
        lg, k, v = self.s.run(None, {"ids": np.array([ids], np.int64), "past_k": st[0], "past_v": st[1]})
        return lg[0, -1], (k, v)

# ------------------------------------------------------------------ token table
BYTE_DEC = None
def _byte_decoder():
    bs = list(range(33, 127)) + list(range(161, 173)) + list(range(174, 256)); cs = bs[:]; n = 0
    for b in range(256):
        if b not in bs: bs.append(b); cs.append(256 + n); n += 1
    return {chr(c): b for b, c in zip(bs, cs)}

class TokTable:
    def __init__(self, tok):
        global BYTE_DEC
        BYTE_DEC = BYTE_DEC or _byte_decoder()
        self.tok = tok; vocab = tok.get_vocab(); self.n = len(vocab)
        self.id = vocab; self.strs = [None] * self.n; self.special = [False] * self.n
        for t, i in vocab.items():
            if t.startswith("<|") and t.endswith("|>"): self.special[i] = True; continue
            try: s = bytes(BYTE_DEC[c] for c in t).decode("utf-8")
            except Exception: s = None
            if s is not None and not all(V.char_ok(c) for c in s): s = None
            self.strs[i] = s
        self.letters = {c: vocab[c] for c in "abcd" if c in vocab}
        self.digits = {str(d): vocab[str(d)] for d in range(10)}
    def decode(self, ids):
        return "".join(self.strs[i] if self.strs[i] is not None else "" for i in ids if not self.special[i])

STRUCT_NEXT_MCQ = {"q": "<|oa|>", "oa": "<|ob|>", "ob": "<|oc|>", "oc": "<|od|>", "od": "<|ans|>"}
CAPS = dict(q=420, oa=120, ob=120, oc=120, od=120, part=320, why=320, sol=700)
KNOWN = sorted(c for c in V.KNOWN_CMDS if c not in ("begin", "end", "hline"))
TWO_ARGS = {"frac", "dfrac", "tfrac", "binom"}
ONE_ARG = {"sqrt", "text", "textbf", "textit", "mathrm", "mathbf", "mathbb", "mathcal", "mathit", "vec", "hat", "bar", "overline", "underline", "dot", "ddot", "tilde", "operatorname", "boxed", "cancel", "ce", "underbrace", "overbrace"}

class TextSt:
    """incremental text/LaTeX state for one free-text segment"""
    __slots__ = ("mode", "depth", "cmd", "bs", "lr", "mlen", "last", "text", "raw", "exp", "frames")
    def __init__(self): self.mode = ""; self.depth = 0; self.cmd = None; self.bs = False; self.lr = 0; self.mlen = 0; self.last = ""; self.text = ""; self.raw = ""; self.exp = 0; self.frames = []
    def copy(self):
        c = TextSt(); c.mode, c.depth, c.cmd, c.bs, c.lr, c.mlen, c.last, c.text, c.raw, c.exp, c.frames = self.mode, self.depth, self.cmd, self.bs, self.lr, self.mlen, self.last, self.text, self.raw, self.exp, list(self.frames); return c
    def closed(self): return self.mode == "" and self.depth == 0 and self.cmd is None and not self.bs and self.exp == 0
    def feed(self, s):
        """return False if s makes the segment invalid"""
        i, n = 0, len(s)
        while i < n:
            ch = s[i]
            if self.cmd is not None:
                if ch.isalpha() and ch.isascii():
                    self.cmd += ch
                    if not any(k.startswith(self.cmd) for k in KNOWN): return False
                    i += 1; continue
                if self.cmd not in KNOWN: return False
                if self.cmd == "left": self.lr += 1
                elif self.cmd == "right": self.lr -= 1
                self.exp = 2 if self.cmd in TWO_ARGS else 1 if self.cmd in ONE_ARG else 0
                self.cmd = None
            if self.bs:
                self.bs = False
                if ch.isalpha() and ch.isascii():
                    self.cmd = ch
                    if not any(k.startswith(ch) for k in KNOWN): return False
                    i += 1; continue
                if self.mode == "" or ch not in "\\{}%&_#,;:! |$": return False
                i += 1; self.mlen += 1; continue
            if self.exp > 0 and ch != " " and ch != "{": return False
            if ch == "$":
                dbl = s.startswith("$$", i)
                if self.mode == "":
                    self.mode = "$$" if dbl else "$"; self.depth = 0; self.mlen = 0; self.lr = 0; self.last = ""; i += 2 if dbl else 1
                else:
                    if self.depth != 0 or self.lr != 0 or self.mlen == 0 or self.last in ("^", "_"): return False
                    if self.mode == "$$":
                        if not dbl: return False
                        i += 2
                    else:
                        if dbl: return False
                        i += 1
                    self.mode = ""
                self.last = "$"; self.text += "$"; continue
            if self.mode:
                if ch == "\\": self.bs = True; i += 1; continue
                if ch == "{":
                    if self.exp > 0: self.frames.append((self.exp - 1, self.depth)); self.exp = 0
                    self.depth += 1
                elif ch == "}":
                    self.depth -= 1
                    if self.depth < 0: return False
                    if self.frames and self.frames[-1][1] == self.depth: self.exp = self.frames.pop()[0]
                elif ch in "^_" and self.last in ("^", "_"): return False
                if ch != " ": self.mlen += 1; self.last = ch
                if ch == " " and self.last == "": i += 1; continue
            else:
                if ch in "\\{}^": return False
                prev = s[i - 1] if i > 0 else self.raw[-1:]
                if ch == " " and prev == " ": return False
            self.text += ch; i += 1
        return True

class ItemSt:
    def __init__(self, typ, marks, want_sol):
        self.typ, self.marks, self.want_sol = typ, marks, want_sol
        self.mcq = typ == "MCQ"; self.sec = "q"; self.t = TextSt(); self.opts = []; self.key = ""; self.why = ""; self.q = ""
        self.parts, self.alt, self.in_alt, self.pm_digits = [], [], False, ""; self.sol = ""; self.done = False; self.fails = 0
        self.has_or = False; self.seen4 = set(); self.recent = []
    def cur_parts(self): return self.alt if self.in_alt else self.parts

class Engine:
    def __init__(self, backend, tokenizer_path, syllabus_path=None, seed=0):
        self.b = backend; self.tok = Tokenizer.from_file(tokenizer_path); self.T = TokTable(self.tok); self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)
        sid = self.T.id
        self.S = {k: sid[f"<|{k}|>"] for k in ["pad", "bos", "end", "unit", "q", "oa", "ob", "oc", "od", "ans", "why", "part", "pm", "or", "sol"]}
        self.struct_ids = set(self.S.values())
        self.syl = json.load(open(syllabus_path or os.path.join(HERE, "syllabus_index.json"))) if (syllabus_path or os.path.exists(os.path.join(HERE, "syllabus_index.json"))) else {"units": {}}
        self.free_ids = [i for i in range(self.T.n) if self.T.strs[i] is not None]
        self.lexicon = {}; self.stats = dict(attempts=0, items=0, rejects={}, dead_ends=0)
    def load_lexicon(self, path):
        self.lexicon = {k: set(v) for k, v in json.load(open(path)).items()}

    # ---- grammar ----
    def allowed_struct(self, st):
        """structural tokens allowed after a closed text segment of sufficient length"""
        sec = st.sec; out = []
        if st.mcq:
            if sec in STRUCT_NEXT_MCQ: out = [STRUCT_NEXT_MCQ[sec]]
            elif sec == "why": out = ["<|end|>"]
        else:
            if sec in ("q", "part"):
                ps = st.cur_parts()
                if sec == "part" and (len(ps) == 1 or all(p[2] for p in ps[:-1])): out.append("<|pm|>")
                out.append("<|part|>")
                first_or = st.typ == "OR" and not st.in_alt
                if first_or: out.append("<|or|>")
                elif st.want_sol: out.append("<|sol|>")
                else: out.append("<|end|>")
            elif sec == "sol": out = ["<|end|>"]
        return out

    def marks_ok(self, st):
        for ps in (st.parts, st.alt):
            if ps and any(p[2] for p in ps) and (not all(p[2] for p in ps) or sum(p[2] for p in ps) != st.marks): return False
        return True

    def minlen(self, st):
        return {"q": 12, "oa": 1, "ob": 1, "oc": 1, "od": 1, "part": 6, "why": 8, "sol": 12}.get(st.sec, 1)

    def valid_mask_fn(self, st):
        """returns f(token_id)->bool for current state"""
        sec = st.sec; T = self.T
        if sec == "ans": return lambda i: i in T.letters.values()
        if sec == "pm":
            if len(st.pm_digits) >= 2: return lambda i: False
            return lambda i: i in T.digits.values() and not (st.pm_digits == "" and i == T.digits["0"]) and int(st.pm_digits + [d for d, v in T.digits.items() if v == i][0]) <= st.marks
        if sec == "pmdone":
            return lambda i: False
        if sec == "or": return lambda i: i == T.id["<|part|>"]
        cap = CAPS.get(sec, 300)
        segtext = st.t.raw
        can_close = st.t.closed() and len(segtext.strip()) >= self.minlen(st)
        allowed = []
        if can_close:
            for name in self.allowed_struct(st):
                nm = name[2:-2]
                if nm in ("part", "or", "sol", "end") and not st.mcq and not self.marks_ok(st): continue
                if nm == "pm" and sec != "part": continue
                if nm == "part" and st.in_alt is False and st.typ == "OR" and False: continue
                if st.mcq and name in ("<|ob|>", "<|oc|>", "<|od|>", "<|ans|>"):
                    norm = re.sub(r"\W+", "", st.t.raw.lower())
                    if not norm or norm in [re.sub(r"\W+", "", o.lower()) for o in st.opts]: continue
                allowed.append(self.T.id[name])
        aset = set(allowed)
        over = len(segtext) >= cap
        def f(i):
            if i in aset: return True
            if T.special[i] or T.strs[i] is None: return False
            if over: return False
            if len(segtext) + len(T.strs[i]) > cap + 12: return False
            c = st.t.copy()
            if not c.feed(T.strs[i]): return False
            return True
        return f

    def apply(self, st, tid):
        """advance state with chosen token"""
        T = self.T; sec = st.sec
        if sec == "ans":
            st.key = [k for k, v in T.letters.items() if v == tid][0]; st.sec = "ans_done"; return
        if sec == "pm" and tid in T.digits.values():
            st.pm_digits += [d for d, v in T.digits.items() if v == tid][0]; return
        if tid in self.struct_ids:
            name = [k for k, v in self.S.items() if v == tid][0]
            self.close_segment(st)
            if name == "end": st.done = True; return
            st.t = TextSt()
            if name in ("oa", "ob", "oc", "od", "ans", "why", "sol"): st.sec = name
            elif name == "part": st.sec = "part"; st.pm_digits = ""; st.cur_parts().append(["", "", 0])
            elif name == "pm": st.sec = "pm"; st.pm_digits = ""
            elif name == "or": st.sec = "or"; st.in_alt = True; st.has_or = True
            return
        st.t.feed(T.strs[tid]); st.t.raw += T.strs[tid]

    def close_segment(self, st):
        sec, txt = st.sec, st.t.raw.strip()
        if sec == "q": st.q = txt
        elif sec in ("oa", "ob", "oc", "od"): st.opts.append(txt)
        elif sec == "why": st.why = txt
        elif sec == "sol": st.sol = txt
        elif sec == "part":
            st.cur_parts()[-1][1] = txt
        elif sec == "pm":
            if st.pm_digits: st.cur_parts()[-1][2] = int(st.pm_digits)
            st.pm_digits = ""

    def after_key(self, st):
        """called when ans chosen: next must be why (if want_sol) or end"""
        pass

    # ---- sampling ----
    def sample(self, logits, valid, temperature, top_p, st):
        lg = logits.astype(np.float64) / max(temperature, 1e-4)
        idx = np.argsort(-lg)
        cand = []
        for rank, i in enumerate(idx[:96]):
            if valid(int(i)): cand.append(int(i))
        if not cand:
            for i in idx[96:]:
                if valid(int(i)):
                    cand.append(int(i))
                    if len(cand) >= 8: break
        if not cand: return None
        # repetition control: forbid completing an already-seen 4-gram
        keep = []
        for c in cand:
            g = tuple(st.recent[-3:] + [c])
            if len(g) == 4 and g in st.seen4: continue
            keep.append(c)
        cand = keep or cand
        p = np.exp(lg[cand] - lg[cand].max()); p /= p.sum()
        o = np.argsort(-p); cs = np.cumsum(p[o]); cut = int(np.searchsorted(cs, top_p)) + 1
        sel = [cand[j] for j in o[:cut]]; pp = p[o[:cut]]; pp /= pp.sum()
        return int(self.np_rng.choice(sel, p=pp))

    def _try_once(self, header_ids, typ, marks, want_sol, temperature, top_p, max_tokens):
        st = ItemSt(typ, marks, want_sol); b = self.b
        prompt = header_ids + [self.S["q"]]
        state = b.start(); lg, state = b.step(prompt, state)
        n = 0
        while not st.done and n < max_tokens and len(prompt) + n < b.max_seq - 2:
            if st.sec == "ans_done":
                nxt = "<|why|>" if want_sol else "<|end|>"
                tid = self.T.id[nxt]
            elif st.sec == "pm" and st.pm_digits:
                valid = self.valid_mask_fn(st)
                cur = int(st.pm_digits); ps = st.cur_parts(); tot = sum(p[2] for p in ps[:-1]) + cur
                names = []
                if tot < st.marks: names = ["<|part|>"]
                elif tot == st.marks:
                    if st.typ == "OR" and not st.in_alt: names = ["<|or|>"]
                    else: names = ["<|sol|>"] if want_sol else ["<|end|>"]
                opts = {self.T.id[x] for x in names}
                tid = self.sample(lg, lambda i, v=valid, o=opts: (i in o) or v(i), temperature, top_p, st)
            else:
                tid = self.sample(lg, self.valid_mask_fn(st), temperature, top_p, st)
            if tid is None: return None
            if st.sec == "pm" and st.pm_digits == "" and False: pass
            self.apply(st, tid)
            st.recent.append(tid)
            if len(st.recent) >= 4: st.seen4.add(tuple(st.recent[-4:]))
            n += 1
            if st.done: break
            lg, state = b.step([tid], state)
        if not st.done: return None
        return st

    def marks_ok_partial(self, st, cur):
        ps = st.cur_parts()
        tot = sum(p[2] for p in ps[:-1]) + cur
        return all(p[2] for p in ps[:-1]) and tot <= st.marks and (tot == st.marks or True)

    # ---- public API ----
    def header(self, board, level, subj, unit, marks, typ):
        sid = f"<|subj={subj}|>" if f"<|subj={subj}|>" in self.T.id else "<|subj=general|>"
        return f"<|bos|><|board={board}|><|level={level}|>{sid}<|unit|>{unit}<|marks={marks}|><|type={typ}|>"

    def generate_item(self, board, level, subj, unit, marks, typ, want_rubric=True, attempts=8, temperature=0.75, top_p=0.92, anchor=None):
        h = self.header(board, level, subj, unit, marks, typ) + (f"<|book|>{anchor}" if anchor else "")
        hid = self.tok.encode(h).ids
        last = "no valid sample"
        for a in range(attempts):
            temp = min(1.1, temperature + 0.04 * a)
            self.stats["attempts"] += 1; st = self._try_once(hid, typ, marks, want_rubric, temp, top_p, 520)
            if st is None: last = "constraint dead-end / length"; self.stats["dead_ends"] += 1; continue
            item = self.finalize(st, board, level, subj, unit, marks, typ)
            if item is None: last = "final validation"; continue
            item["attempts"] = a + 1; self.stats["items"] += 1
            return item
        raise ItemGenerationError(f"{board}/{level}/{subj}/{unit}/{marks}/{typ}: {last}")

    def finalize(self, st, board, level, subj, unit, marks, typ):
        h = self.header(board, level, subj, unit, marks, typ)
        if st.mcq:
            if len(st.opts) != 4 or st.key not in "abcd": return None
            txt = f"{h}<|q|>{st.q}<|oa|>{st.opts[0]}<|ob|>{st.opts[1]}<|oc|>{st.opts[2]}<|od|>{st.opts[3]}<|ans|>{st.key}" + (f"<|why|>{st.why}" if st.why else "") + "<|end|>"
            if V.check_mcq(st.q, st.opts, st.key, st.why): return None
            item = dict(kind="mcq", question=st.q, options=st.opts, key=st.key, explanation=st.why)
        else:
            if not self.marks_ok(st): return None
            if typ == "OR" and not st.alt: return None
            parts = [(chr(97 + i), p[1], p[2]) for i, p in enumerate(st.parts)]; alt = [(chr(97 + i), p[1], p[2]) for i, p in enumerate(st.alt)]
            if any(not p[1] for p in parts + alt): return None
            stem = st.q
            if V.check_written(stem, parts, alt, marks, st.sol): return None
            def rp(ps): return "".join(f"<|part|>({l}) {t}" + (f"<|pm|>{m}" if m else "") for l, t, m in ps)
            txt = f"{h}<|q|>{stem}{rp(parts)}" + (f"<|or|>{rp(alt)}" if alt else "") + (f"<|sol|>{st.sol}" if st.sol else "") + "<|end|>"
            item = dict(kind="written", question=stem, parts=[dict(label=l, text=t, marks=m) for l, t, m in parts],
                        or_parts=[dict(label=l, text=t, marks=m) for l, t, m in alt], rubric=st.sol)
        if V.validate_item_text(txt): return None
        cl = VF.clean_symbols
        if item["kind"] == "mcq": item.update(question=cl(item["question"]), options=[cl(o) for o in item["options"]], explanation=cl(item["explanation"]))
        else:
            item["question"] = cl(item["question"]); item["rubric"] = cl(item["rubric"])
            for k in ("parts", "or_parts"):
                for p_ in item[k]: p_["text"] = cl(p_["text"])
        item.update(board=board, level=level, subject=subj, unit=unit, marks=marks, type=typ)
        if not getattr(self, "verify_on", True): item["schema_text"] = txt; return item
        v = VF.verify_item(item, unit=unit, lexicon=self.lexicon.get(subj) or self.lexicon.get("*"), strict_anchor=bool(self.lexicon))
        if not v["ok"]:
            for r in v["issues"]: k = re.sub(r"\(.*|: .*", "", r)[:40]; self.stats["rejects"][k] = self.stats["rejects"].get(k, 0) + 1
            return None
        item["verify"] = dict(score=v["score"], anchor_hits=v["anchor"]["hits"], concept_hits=v["anchor"]["lex"]); item["schema_text"] = txt
        return item

    # ---- papers ----
    def units_for(self, board, level, subj):
        u = self.syl.get("units", {}).get(f"{board}|{level}|{subj}")
        if u: return u
        for k, v in self.syl.get("units", {}).items():
            if k.endswith(f"|{level}|{subj}") or k.split("|")[1] == level and v: return v
        return ["General"]

    # official full marks: NEB 11/12 = 75, SEE = 75, IOE = 100, BLE 8 = 48
    BLUEPRINTS = {
        "C8": [("A", "MCQ", 1, 10), ("B", "SHORT", 2, 6), ("C", "CONCEPTUAL", 4, 4), ("D", "LONG", 5, 2)],
        "C10": [("A", "MCQ", 1, 10), ("B", "SHORT", 2, 8), ("C", "CONCEPTUAL", 4, 6), ("D", "LONG", 5, 5)],
        "C11": [("A", "MCQ", 1, 11), ("B", "SHORT", 5, 8), ("C", "OR", 8, 3)],
        "C12": [("A", "MCQ", 1, 11), ("B", "SHORT", 5, 8), ("C", "OR", 8, 3)],
        "IOE": [("A", "MCQ", 1, 100)], "CEE": [("A", "MCQ", 1, 100)], "BCA": [("A", "MCQ", 1, 100)], "BSN": [("A", "MCQ", 1, 100)],
        "BE": [("A", "OR", 10, 8)],
    }
    def model_paper(self, board, level, subj, blueprint=None, rubric=True, seed=None, on_item=None):
        if seed is not None: self.rng = random.Random(seed); self.np_rng = np.random.default_rng(seed)
        bp = blueprint or self.BLUEPRINTS[level]; units = self.units_for(board, level, subj)
        self.rng.shuffle(units); k = 0; seen = set(); sections = []
        for g, typ, marks, count in bp:
            items = []; fails = 0
            while len(items) < count:
                unit = units[k % len(units)]; k += 1
                t = typ
                if typ == "SHORT":
                    t = ["CONCEPTUAL", "NUMERICAL", "DERIVATION", "SHORT"][len(items) % 4]
                try: it = self.generate_item(board, level, subj, unit, marks, t, want_rubric=rubric, attempts=12)
                except ItemGenerationError:
                    fails += 1
                    if fails > 8 * count + 12: raise
                    continue  # resample another unit; an invalid item is never emitted
                key = re.sub(r"[^a-z0-9]", "", (it["question"] + "".join(it.get("options", []))).lower())[:90]
                if key in seen: continue
                seen.add(key); it["no"] = len(items) + 1; items.append(it)
                if on_item: on_item(g, it)
            sections.append(dict(group=g, type=typ, marks_each=marks, count=count, items=items))
        total = sum(s["marks_each"] * s["count"] for s in sections)
        return dict(board=board, level=level, subject=subj, total_marks=total, sections=sections, generator="PaperLM-Tiny")

    def mock_test(self, board, level, subj, n=20, marks=1, typ="MCQ", **kw):
        return self.model_paper(board, level, subj, blueprint=[("A", typ, marks, n)], **kw)

def render_paper(p):
    out = [f"{p['board']} · {p['level']} · {p['subject'].upper()} — Model Paper  (Full marks: {p['total_marks']})", ""]
    for s in p["sections"]:
        out.append(f"Group '{s['group']}'  [{s['count']} × {s['marks_each']} = {s['count'] * s['marks_each']}]")
        for it in s["items"]:
            out.append(f"{it['no']}. {it['question']}")
            if it["kind"] == "mcq":
                for l, o in zip("abcd", it["options"]): out.append(f"   ({l}) {o}")
                out.append(f"   Ans: ({it['key']})  {it['explanation']}".rstrip())
            else:
                for q in it["parts"]: out.append(f"   ({q['label']}) {q['text']}" + (f" [{q['marks']}]" if q["marks"] else ""))
                if it["or_parts"]:
                    out.append("   OR")
                    for q in it["or_parts"]: out.append(f"   ({q['label']}) {q['text']}" + (f" [{q['marks']}]" if q["marks"] else ""))
                if it["rubric"]: out.append(f"   Marking rubric: {it['rubric']}")
        out.append("")
    return "\n".join(out)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--ckpt"); ap.add_argument("--onnx"); ap.add_argument("--tok", default=os.path.join(HERE, "..", "tokenizer", "paperlm_tokenizer.json"))
    ap.add_argument("--board", default="NEB"); ap.add_argument("--level", default="C12"); ap.add_argument("--subject", default="physics"); ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    be = OrtBackend(a.onnx) if a.onnx else TorchBackend(a.ckpt)
    e = Engine(be, a.tok, seed=a.seed); print(render_paper(e.model_paper(a.board, a.level, a.subject, seed=a.seed)))
