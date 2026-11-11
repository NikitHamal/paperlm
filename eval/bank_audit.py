#!/usr/bin/env python3
"""Strict semantic coherence audit of the verified bank (Breakthrough 3 applied to the bank itself).
Every MCQ seed must: have 4 homogeneous distinct options, a key that agrees with its explanation (named option / computed value), balanced LaTeX, and correct plain arithmetic chains.
Every written seed must: have valid LaTeX in stem/parts/rubric and correct arithmetic chains. Failing seeds are dropped. usage: bank_audit.py IN OUT REPORT"""
import json, sys, collections, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, "..", "engine"), os.path.join(HERE, "..", "data")]
import verify as VF, validator as V
src, dst, rep = sys.argv[1:4]; B = json.load(open(src, encoding="utf-8")); why = collections.Counter(); n = kept = 0
def bad_tex(*ts): return any(t and V.check_text(t, True) for t in ts)
for k, per in list(B["seeds"].items()):
    for u, lst in list(per.items()):
        keep = []
        for x in lst:
            n += 1; iss = []
            if x["c"] == "mcq":
                iss += VF.check_options(x["o"], x["q"]); iss += VF.check_key(x["o"], x["k"], x.get("w", ""))
                if bad_tex(x["q"], *x["o"], x.get("w", "")): iss.append("latex")
                if VF.check_arith(" ".join([x["q"], x.get("w", "")])): iss.append("arithmetic")
            else:
                txt = " ".join([x["q"], *(p[1] for p in x.get("p", [])), *(p[1] for p in x.get("a", [])), x.get("r", "")])
                if bad_tex(x["q"], x.get("r", ""), *(p[1] for p in x.get("p", [])), *(p[1] for p in x.get("a", []))): iss.append("latex")
                if VF.check_arith(txt): iss.append("arithmetic")
                if len(x["q"]) < 8 and not x.get("p"): iss.append("short")
            if iss:
                for i in iss: why[i.split(" (")[0][:60]] += 1
            else: keep.append(x)
        kept += len(keep)
        if keep: per[u] = keep
        else: del per[u]
    if not per: del B["seeds"][k]
B["version"] = "v5-audited"; json.dump(B, open(dst, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
r = dict(seeds_in=n, seeds_kept=kept, dropped=n - kept, drop_rate=round((n - kept) / n, 4), reasons=dict(why.most_common(12)))
json.dump(r, open(rep, "w"), indent=1); print(json.dumps(r, indent=1))
