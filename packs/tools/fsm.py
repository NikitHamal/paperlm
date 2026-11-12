"""Grammar-constrained decoding (FSM logit masking) + symbolic grounding verifier for PaperLM specialist packs.
JS twin: docs/packlm.js (same states, caps, bracket/LaTeX rules).  Malformed tags, wrong option counts and unclosed $...$ / {...} are impossible."""
import math, re, numpy as np
SPEC = {  # (segment, closer, min_chars, max_chars)
    "mcq": [("ans", "<|q|>", 1, 160), ("q", "<|d|>", 15, 360), ("d1", "<|d|>", 1, 160), ("d2", "<|d|>", 1, 160), ("d3", "<|why|>", 1, 160), ("why", "<|end|>", 15, 300)],
    "short": [("ans", "<|q|>", 20, 650), ("q", "<|end|>", 15, 300)]}
STRUCT = ["<|pad|>", "<|bos|>", "<|end|>", "<|unit|>", "<|book|>", "<|ans|>", "<|q|>", "<|d|>", "<|why|>"]
def tok_tables(tok):
    V = tok.get_vocab_size(); strs = []
    for i in range(V):
        s = tok.decode([i], skip_special_tokens=False); strs.append(s)
    special = {s: i for s, i in tok.get_vocab().items() if s.startswith("<|") and s.endswith("|>")}
    isp = np.zeros(V, bool); [isp.__setitem__(i, True) for i in special.values()]
    ok = np.array([(not isp[i]) and "\ufffd" not in s and all(32 <= ord(c) < 127 or c in "°±×÷²³µΩ→≈≤≥−·λμπσΔ" for c in s) for i, s in enumerate(strs)])
    return dict(V=V, strs=strs, special=special, isp=isp, ok=ok, op=np.array([s.count("{") for s in strs]), cl=np.array([s.count("}") for s in strs]), dl=np.array([s.count("$") for s in strs]))
class State:
    def __init__(self, T, kind):
        self.T, self.spec, self.k, self.text, self.d, self.dol, self.done, self.ids = T, SPEC[kind], 0, "", 0, 0, False, []
    def mask(self):
        T = self.T; seg, closer, lo, hi = self.spec[self.k]; m = T["ok"].copy(); n = len(self.text)
        m &= (self.d + T["op"] - T["cl"]) >= 0
        if n == 0: m &= np.array([not s.startswith(" ") and s.strip() != "" for s in T["strs"]])  # no empty / space-led segments
        c = T["special"][closer]; balanced = self.d == 0 and self.dol % 2 == 0
        if n >= hi and balanced: m[:] = False; m[c] = True
        elif n >= lo and balanced: m[c] = True
        elif n >= hi + 80: m[:] = False; m[c] = True  # safety: cannot be stuck inside math forever
        return m
    def feed(self, i):
        T = self.T; s = T["strs"][i]; self.ids.append(i)
        if T["isp"][i]:
            self.k += 1; self.text = ""; self.d = 0; self.dol = 0
            if self.k >= len(self.spec): self.done = True
            return
        self.text += s; self.d += T["op"][i] - T["cl"][i]; self.dol += T["dl"][i]
    def segs(self, ids=None):
        T = self.T; out, cur = [], ""
        for i in (ids or self.ids):
            if T["isp"][i]: out.append(cur.strip()); cur = ""
            else: cur += T["strs"][i]
        return out
try:
    import torch; _ng = torch.no_grad()
except ImportError:  # CPU-only harness checks (eval/ort_pack_check.py) only need State / tok_tables
    torch = None; _ng = lambda f: f
@_ng
def sample(model, T, prompt_ids, kind, K=6, temp=0.75, top_p=0.92, anchor_ids=(), beta=1.0, dev="cuda", maxlen=420):
    model.eval(); model.return_cache = True; sts = [State(T, kind) for _ in range(K)]
    x = torch.tensor([prompt_ids] * K, device=dev); lg, pk, pv = model(x); lg = lg[:, -1].float(); lp = [0.0] * K
    bias = torch.zeros(T["V"], device=dev); bias[list(set(anchor_ids))] = beta; seen = [dict() for _ in range(K)]
    for step in range(maxlen):
        nxt = []
        for b in range(K):
            if sts[b].done: nxt.append(0); continue
            m = torch.from_numpy(sts[b].mask()).to(dev); l = lg[b] + bias; ids = sts[b].ids
            if len(ids) > 6:  # no-repeat 5-gram
                tail = tuple(ids[-4:]); ban = [g[-1] for g in seen[b].get(tail, [])]
                if ban: l = l.clone(); l[ban] = -1e9
            l = l.masked_fill(~m, -1e9) / temp; p = torch.softmax(l, -1); sp, si = torch.sort(p, descending=True); cs = torch.cumsum(sp, 0); sp[cs - sp > top_p] = 0
            t = int(si[torch.multinomial(sp / sp.sum(), 1)]); lp[b] += float(torch.log_softmax(lg[b], -1)[t])
            if len(ids) >= 4: seen[b].setdefault(tuple(ids[-4:]), []).append(tuple(ids[-4:]) + (t,))
            sts[b].feed(t); nxt.append(t)
        if all(s.done for s in sts): break
        lg, pk2, pv2 = model(torch.tensor(nxt, device=dev)[:, None], pk, pv); pk, pv = pk2, pv2; lg = lg[:, -1].float()
    return [(s.segs(), lp[i] / max(1, len(s.ids)), s.done) for i, s in enumerate(sts)]
# ------------------------------------------------------------------ symbolic grounding verifier (best-of-K entailment reranker)
STOP = set("the of and a an to in is are was were be by for with on as at from that this which it its or their these those can has have into than then also not one two more most each other such when where what who how why".split())
cw = lambda s: [w for w in re.findall(r"[a-z][a-z0-9]{2,}", s.lower()) if w not in STOP]
def grounding(segs, kind, anchor, unit_terms=()):
    """returns score in [0,1] and flags.  MCQ: answer must be extractive from the anchor, question on the unit's vocabulary, distractors distinct and NOT stated in the anchor."""
    A = set(cw(anchor)); f = {}
    if kind == "mcq":
        if len(segs) < 6: return 0.0, {"bad": "shape"}
        ans, q, d1, d2, d3, why = segs[:6]; ds = [d1, d2, d3]; aw = cw(ans) or ["_"]
        f["ans_ground"] = sum(w in A for w in aw) / len(aw); qw = cw(q); f["q_ground"] = sum(w in A or w in unit_terms for w in qw) / max(1, len(qw))
        f["distinct"] = float(len({x.lower() for x in ds + [ans]}) == 4 and all(x.lower() not in anchor.lower() or len(x) < 4 for x in ds))
        f["why_ground"] = sum(w in A for w in cw(why)) / max(1, len(cw(why))); f["no_copy_q"] = float(q.lower() not in anchor.lower())
        f["homog"] = float(all(0.3 <= (len(x) + 3) / (len(ans) + 3) <= 3.5 for x in ds))
        sc = 0.35 * f["ans_ground"] + 0.2 * f["q_ground"] + 0.2 * f["distinct"] + 0.1 * f["why_ground"] + 0.05 * f["no_copy_q"] + 0.1 * f["homog"]
    else:
        if len(segs) < 2: return 0.0, {"bad": "shape"}
        ans, q = segs[:2]; aw = cw(ans) or ["_"]; qw = cw(q)
        f["ans_ground"] = sum(w in A for w in aw) / len(aw); f["q_ground"] = sum(w in A or w in unit_terms for w in qw) / max(1, len(qw)); sc = 0.6 * f["ans_ground"] + 0.4 * f["q_ground"]
    return sc, f
