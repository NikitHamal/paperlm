#!/usr/bin/env python3
"""PaperLM v4 data: CONCEPT-GROUNDED conditional training set + the shipped concept_bank.json.

Every training sequence is   header + <|book|> CONCEPT ANCHOR + <|q|> question ... <|ans|> key <|why|> explanation   (MCQ)
                             header + <|book|> CONCEPT ANCHOR + <|q|> stem <|part|>... <|sol|> rubric            (written)
so the 10M model learns to *translate a verified syllabus statement into a board-style item* instead of recalling facts from its weights.
Anchors: (a) the item's own verified explanation / model-answer sentence (copy-style grounding, 50%) and (b) a *retrieved* textbook definition/law
sentence from the same subject (TF-IDF over the textbook concept sentences, 50%) so inference-time anchors (textbook sentences) are in-distribution.
usage: build_v4.py <gold_dir> <out_dir> <tokenizer.json> [repo_dir]"""
import collections, hashlib, json, math, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, "..", "engine"), "/tmp/paperlm/engine", "/tmp/paperlm/data"]
import validator as V, verify as VF, ground as GR
import parametric as PM
gold_dir, out, tokp = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(out, exist_ok=True); rng = random.Random(4)
from tokenizers import Tokenizer
vocab = Tokenizer.from_file(tokp).get_vocab()
DEF = re.compile(r"(\bis defined as\b|\bis called\b|\bare called\b|\bis known as\b|\bis the (?:ratio|product|sum|rate|number|force|process|study|measure|property)\b|\bstates that\b|\bSI unit\b|\bunit of\b|\bformula\b|\bis given by\b|\bwhere \$|=\s*\\frac|\bequals\b|\bproportional\b|\bobeys\b|\blaw\b|\btheorem\b)", re.I)
NOSHUF = re.compile(r"\b(both|all of|none of|above|neither|either|only|a and b|a, b|a & b)\b|^\(?[a-d]\)?$", re.I)


def header(g):
    s = f"<|subj={g['subj']}|>" if f"<|subj={g['subj']}|>" in vocab else "<|subj=general|>"
    return f"<|bos|><|board={g['board']}|><|level={g['level']}|>{s}<|unit|>{g['unit']}<|marks={g['marks']}|><|type={g['type']}|>"


def sents(s): return [x.strip() for x in re.split(r"(?<=[.?!])\s+(?=[A-Z$\\(])", s or "") if x.strip()]


def own_anchor(g):
    src = g.get("why") if g["qtype"] == "MCQ" else g.get("sol")
    if not src: return None
    out = ""
    for s in sents(src):
        if re.search(r"\b(option|options|answer|key)\b|^\(?[a-d]\)", s, re.I): continue
        if len(out) + len(s) > 240: break
        out += (" " if out else "") + s
        if len(out) >= 60: break
    if len(out) < 28 or V.check_text(out) is not None: return None
    return out


def as_item(g):
    if g["qtype"] == "MCQ": return dict(kind="mcq", question=g["q"], options=g["opts"], key=g["key"], explanation=g.get("why") or "")
    mk = lambda ps: [dict(label=l, text=t, marks=m) for l, t, m in ps]
    return dict(kind="written", question=g["stem"], parts=mk(g["parts"]), or_parts=mk(g.get("alt") or []), rubric=g.get("sol") or "")


G = [json.loads(l) for l in open(f"{gold_dir}/gold.jsonl", encoding="utf-8")]; keep = []
for g in G:
    if g["qtype"] != "MCQ": g["parts"] = [tuple(p) for p in g["parts"]]; g["alt"] = [tuple(p) for p in (g.get("alt") or [])]
    if VF.verify_item(as_item(g))["ok"]: keep.append(g)
print("verified gold", len(keep), "of", len(G), flush=True)

# ---- textbook concept sentences (definitions / laws / formulas)
book, seen = [], set()
for l in open(f"{gold_dir}/book.txt", encoding="utf-8"):
    m = re.match(r"<\|bos\|><\|board=(\w+)\|><\|level=(\w+)\|><\|subj=([^|]+)\|><\|unit\|>(.*?)<\|book\|>(.*)<\|end\|>", l.strip())
    if not m: continue
    board, level, subj, unit, body = m.groups()
    for s in sents(body):
        if not (40 <= len(s) <= 240) or not DEF.search(s) or s.endswith("?") or V.check_text(s) is not None: continue
        if re.search(r"\b(question|marks?|exam|paper|chapter|section|practice|group [A-D]|you|your|we|figure|table|example|exercise)\b", s, re.I): continue
        k = hashlib.md5(s.lower().encode()).hexdigest()
        if k in seen: continue
        seen.add(k); book.append(dict(board=board, level=level, subj=subj, unit=re.sub(r"[^A-Za-z0-9 ,:()\-]", "", unit)[:60].strip() or "General", t=s))
print("textbook concept sentences", len(book), flush=True)

# ---- retrieval index (same-subject TF-IDF over concept sentences)
df = collections.Counter(); idx = collections.defaultdict(lambda: collections.defaultdict(list)); bw = []
for i, b in enumerate(book):
    w = GR.cwords(b["t"]); bw.append(w); df.update(w)
    for x in w: idx[b["subj"]][x].append(i)
N = len(book); idf = {w: math.log((N + 1) / (c + 1)) + 1 for w, c in df.items()}


def retrieve(g, qwords, ban=()):
    sc = collections.Counter()
    for x in qwords:
        for i in idx[g["subj"]].get(x, ()): sc[i] += idf[x] ** 2
    best, bs = None, 0
    for i, s in sc.most_common(8):
        if book[i]["t"] in ban: continue
        n = s / math.sqrt(sum(idf.get(x, 0) ** 2 for x in qwords) * sum(idf[x] ** 2 for x in bw[i]) + 1e-9)
        if n > bs: best, bs = i, n
    return (book[best]["t"], bs) if best is not None and bs >= 0.20 else (None, bs)


def qwords(g):
    return GR.cwords(g["q"] + " " + g["opts"]["abcd".index(g["key"])]) if g["qtype"] == "MCQ" else GR.cwords(g["stem"] + " " + " ".join(p[1] for p in g["parts"]))


def render_mcq(h, anc, q, o, k, w): return f"{h}<|book|>{anc}<|q|>{q}<|oa|>{o[0]}<|ob|>{o[1]}<|oc|>{o[2]}<|od|>{o[3]}<|ans|>{k}" + (f"<|why|>{w}" if w else "") + "<|end|>"


def render_written(h, anc, stem, parts, alt, sol):
    r = lambda ps: "".join(f"<|part|>{'(' + l + ') ' if l else ''}{t}" + (f"<|pm|>{m}" if m else "") for l, t, m in ps)
    return f"{h}<|book|>{anc}<|q|>{stem}{r(parts)}" + (f"<|or|>{r(alt)}" if alt else "") + (f"<|sol|>{sol}" if sol else "") + "<|end|>"


def is_val(g): return int(hashlib.md5(g["src"].encode()).hexdigest(), 16) % 100 < 4


def lines_for(gs, aug):
    L, stats = [], collections.Counter()
    for g in gs:
        h = header(g); anchors = []
        oa = own_anchor(g)
        if oa: anchors.append(("own", oa))
        ra, sc = retrieve(g, qwords(g), ban=(oa,) if oa else ())
        if ra: anchors.append(("book", ra))
        if not anchors: stats["no_anchor"] += 1; continue
        for kind, anc in anchors:
            stats[kind] += 1
            if g["qtype"] == "MCQ":
                L.append(render_mcq(h, anc, g["q"], g["opts"], g["key"], g.get("why")))
                if aug and not any(NOSHUF.search(o) for o in g["opts"]):
                    perm = list(range(4)); rng.shuffle(perm)
                    if perm != [0, 1, 2, 3]:
                        o2 = [g["opts"][i] for i in perm]; k2 = "abcd"[perm.index("abcd".index(g["key"]))]
                        L.append(render_mcq(h, anc, g["q"], o2, k2, g.get("why")))
            else: L.append(render_written(h, anc, g["stem"], g["parts"], g["alt"], g.get("sol")))
    return L, stats


train, st_tr = lines_for([g for g in keep if not is_val(g)], 1); val, st_va = lines_for([g for g in keep if is_val(g)], 0)
# parametric items as extra grounded training lines (anchor = the law the numbers come from)
pl = []; subs = [("physics", "C12"), ("physics", "C11"), ("chemistry", "C12"), ("mathematics", "C12"), ("mathematics", "C10"), ("science", "C10"), ("computer-science", "C12"), ("fundamentals-of-nursing", "BSN")]
for _ in range(7000):
    sj, lv = subs[rng.randrange(len(subs))]; mk = rng.choice([1, 1, 1, 3, 4, 5]); ty = "MCQ" if mk == 1 else "NUMERICAL"
    it = PM.make_item(sj, lv, "", mk, ty, rng)
    if not it: continue
    bd = {"C12": "NEB", "C11": "NEB", "C10": "SEE", "BSN": "CTEVT"}[lv]; g = dict(board=bd, level=lv, subj=sj, unit=it["unit_label"], marks=mk, type=ty); h = header(g)
    if it["kind"] == "mcq": pl.append(render_mcq(h, it["concept"], it["question"], it["options"], it["key"], it["explanation"]))
    else: pl.append(render_written(h, it["concept"], it["question"], [(p["label"], p["text"], p["marks"]) for p in it["parts"]], [], it["rubric"]))
bad = {i for i, t in enumerate(train) if V.validate_item_text(re.sub(r"<\|book\|>.*?<\|q\|>", "<|q|>", t)) is not None}
train = [t for i, t in enumerate(train) if i not in bad]; allt = train + pl; rng.shuffle(allt)
w = lambda n, L: open(f"{out}/{n}", "w", encoding="utf-8").write("\n".join(L) + "\n")
w("stage4.txt", allt); w("stage4_clean.txt", train); w("val.txt", val); w("val_clean.txt", val)

# ---- shipped concept bank (all verified gold, not only train) -> facts + gold seeds
facts = collections.defaultdict(lambda: collections.defaultdict(list)); seeds = collections.defaultdict(lambda: collections.defaultdict(list)); fseen = set()
def add_fact(key, unit, t):
    h = hashlib.md5(t.lower().encode()).hexdigest()
    if h in fseen or len(facts[key][unit]) >= 80: return
    fseen.add(h); facts[key][unit].append(t)
for g in keep:
    key = f"{g['board']}|{g['level']}|{g['subj']}"; oa = own_anchor(g)
    if oa: add_fact(key, g["unit"], oa)
    cls = "mcq" if g["qtype"] == "MCQ" else f"w{g['marks']}"
    if len(seeds[key][g["unit"]]) < 40 and sum(1 for s in seeds[key][g["unit"]] if s["c"] == cls) < 14:
        s = dict(c=cls, m=g["marks"], t=g["type"])
        if g["qtype"] == "MCQ": s.update(q=g["q"], o=g["opts"], k=g["key"], w=g.get("why") or "")
        else: s.update(q=g["stem"], p=[list(p) for p in g["parts"]], a=[list(p) for p in g["alt"]], r=g.get("sol") or "")
        seeds[key][g["unit"]].append(s)
for b in book: add_fact(f"{b['board']}|{b['level']}|{b['subj']}", b["unit"], b["t"])
bank = dict(version="v1", facts={k: dict(v) for k, v in facts.items()}, seeds={k: dict(v) for k, v in seeds.items()})
json.dump(bank, open(f"{out}/concept_bank.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
nf = sum(len(x) for v in facts.values() for x in v.values()); ns = sum(len(x) for v in seeds.values() for x in v.values())
stats = dict(gold_verified=len(keep), textbook_concepts=len(book), train_lines=len(allt), grounded_exam_lines=len(train), parametric_lines=len(pl), val_lines=len(val), anchors_train=dict(st_tr), anchors_val=dict(st_va),
             bank_facts=nf, bank_seeds=ns, bank_keys=len(facts), bank_bytes=os.path.getsize(f"{out}/concept_bank.json"))
json.dump(stats, open(f"{out}/dataset_v4_stats.json", "w"), indent=1); print(json.dumps(stats))
