"""PaperLM Composer (Python twin of engine/web/composer.js): parametric -> concept-grounded LM (strict gate) -> verified bank. Never emits an unverified item."""
import json, random
import ground as GR, parametric as PM
import re
NOSHUF = re.compile(r"\b(both|all of|none of|above|neither|either|only|a and b|a, b|a & b)\b|^\(?[a-d]\)?$", re.I)


class Composer:
    def __init__(self, engine, bank_path, seed=0):
        self.e = engine; self.bank = json.load(open(bank_path, encoding="utf-8")); self.rng = random.Random(seed)
        self.beta = 2.5; self.stats = dict(param=0, lm=0, bank=0, lm_tries=0, lm_gate_pass=0, gate_rejects={})

    def facts(self, key, unit):
        f = self.bank["facts"].get(key, {}); l = f.get(unit, [])
        if not l:
            lu = next((u for u in f if u.lower() in unit.lower() or unit.lower() in u.lower()), None)
            if lu: l = f[lu]
        return l

    def seeds(self, key, unit, marks, mcq):
        s = self.bank["seeds"].get(key, {}); want = "mcq" if mcq else f"w{marks}"; u = unit; l = [x for x in s.get(u, []) if x["c"] == want]
        if not l:
            lu = next((k for k in s if k.lower() in unit.lower() or unit.lower() in k.lower()), None)
            if lu: u = lu; l = [x for x in s[lu] if x["c"] == want]
        if not l:
            allx = [(k, x) for k, v in s.items() for x in v if x["c"] == want]
            if allx: k, x = self.rng.choice(allx); return k, [x]
        return u, l

    def from_seed(self, s, unit, board, level, subject, typ):
        base = dict(board=board, level=level, subject=subject, unit=unit, marks=s["m"], type="MCQ" if typ == "MCQ" else s.get("t", typ), source="bank", verified=True, provenance=dict(tier="bank"))
        if s["c"] == "mcq":
            o, k = s["o"][:], s["k"]
            if not any(NOSHUF.search(x) for x in o):
                perm = list(range(4)); self.rng.shuffle(perm); o = [s["o"][i] for i in perm]; k = "abcd"[perm.index("abcd".index(s["k"]))]
            return dict(base, kind="mcq", question=s["q"], options=o, key=k, explanation=s.get("w", ""), marks=1)
        mk = lambda ps: [dict(label=l or chr(97 + i), text=t, marks=m) for i, (l, t, m) in enumerate(ps)]
        return dict(base, kind="written", question=s["q"], parts=mk(s.get("p", [])), or_parts=mk(s.get("a", [])), rubric=s.get("r", ""))

    def item(self, board, level, subject, unit, marks, typ, use_lm=False):
        key = f"{board}|{level}|{subject}"; mcq = typ == "MCQ" or marks <= 1; r = self.rng.random()
        canp = bool(PM.domains_for(subject)) and any(PM.level_ok(t, level) and set(t["dom"].split()) & set(PM.domains_for(subject)) for t in PM.LIB["templates"])
        if typ == "NUMERICAL": order = ["param", "lm", "bank"] if canp else ["lm", "bank"]
        elif mcq: order = ["param", "lm", "bank"] if canp and r < 0.45 else ["lm", "bank", "param"]
        elif typ == "OR": order = ["param", "lm", "bank"] if canp and r < 0.5 else ["lm", "bank", "param"]
        else: order = ["param", "lm", "bank"] if canp and r < 0.15 else ["lm", "bank", "param"]
        for tier in order:
            if tier == "param" and canp:
                it = PM.make_item(subject, level, unit, marks, "MCQ" if mcq else typ, self.rng)
                if it and (it["unit_matched"] or tier == order[0] or not self.facts(key, unit)):
                    self.stats["param"] += 1; it.update(board=board, level=level, subject=subject, unit=unit if it["unit_matched"] else it["unit_label"], marks=marks, type=typ, provenance=dict(tier="param", law=it["concept"])); return it
            elif tier == "lm" and use_lm and self.e:
                fs = self.facts(key, unit)
                for _ in range(3 if fs else 0):
                    anc = self.rng.choice(fs)
                    for k in range(4):
                        self.stats["lm_tries"] += 1
                        try: it = self.e.generate_item(board, level, subject, unit, marks, typ, attempts=1, temperature=min(1.0, 0.7 + 0.05 * k), anchor=anc, bias_beta=self.beta)
                        except Exception: continue
                        g = GR.gate(it, anc)
                        if g["ok"]:
                            self.stats["lm_gate_pass"] += 1; self.stats["lm"] += 1; it.update(provenance=dict(tier="lm", anchor=anc, gate=dict(p=g["p"], r=g["r"])), verified=False, experimental=True, source="lm"); return it
                        for x in g["issues"]: kx = re.sub(r":.*", "", x); self.stats["gate_rejects"][kx] = self.stats["gate_rejects"].get(kx, 0) + 1
            elif tier == "bank":
                u, l = self.seeds(key, unit, marks, mcq)
                if l: self.stats["bank"] += 1; return self.from_seed(self.rng.choice(l), u, board, level, subject, typ)
        raise RuntimeError(f"no verified item for {key}/{unit}/{marks}/{typ}")
