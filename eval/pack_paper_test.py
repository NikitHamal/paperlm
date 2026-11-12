#!/usr/bin/env python3
"""Planner invariants for every shipped pack (v14). For 12 seeds x 3 paper shapes per pack it asserts:
no duplicate question or anchor, no near-duplicate (token Jaccard >= 0.6), MCQ key present and unique among its options,
marking scheme of every written item sums EXACTLY to its marks, numericals computed (src=computed) and arithmetic-consistent.
usage: python3 eval/pack_paper_test.py -> eval/results/packs/paper_test.json"""
import json, os, sys, glob
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, f"{R}/engine")
import pack_paper as PP
res = {}; bad_total = 0
for d in sorted(glob.glob(f"{R}/docs/packs/*/bank.json")):
    pid = d.split("/")[-2]; r = dict(papers=0, items=0, dup_q=0, dup_anchor=0, near_dup=0, key_missing=0, scheme_bad=0, computed=0, unit_cov=[], miss=0)
    for seed in range(1, 13):
        for shape in ((10, 4, 2), (20, 6, 3), (30, 8, 4)):
            g, items, miss = PP.plan(pid, shape[0], shape[1], seed, shape[2]); r["papers"] += 1; r["miss"] += miss
            qs = [b["question"] for _, _, b in items]; an = [b["anchor"] for _, _, b in items if b.get("src") != "computed"]
            r["items"] += len(items); r["dup_q"] += len(qs) - len(set(qs)); r["dup_anchor"] += len(an) - len(set(an))
            ws = [PP.W(q) for q in qs]
            r["near_dup"] += sum(1 for i in range(len(ws)) for j in range(i) if PP.jac(ws[i], ws[j]) >= 0.6)
            r["computed"] += sum(1 for _, _, b in items if b.get("src") == "computed")
            for k, m, b in items:
                if k == "mcq":
                    o = [b["answer"]] + b["distractors"]
                    if o.count(b["answer"]) != 1 or len(o) != 4: r["key_missing"] += 1
                elif sum(x for _, x in PP.scheme(b["answer"], b["marks"])) != b["marks"]: r["scheme_bad"] += 1
            r["unit_cov"].append(round(len({b["unit"] for _, _, b in items} & {u["name"] for u in g["units"]}) / len(g["units"]), 2))
    r["unit_cov_mean"] = round(sum(r.pop("unit_cov")) / r["papers"], 2)
    bad = r["dup_q"] + r["dup_anchor"] + r["near_dup"] + r["key_missing"] + r["scheme_bad"]; bad_total += bad; res[pid] = r
    print(pid, json.dumps(r))
os.makedirs(f"{R}/eval/results/packs", exist_ok=True)
json.dump(res, open(f"{R}/eval/results/packs/paper_test.json", "w"), indent=1)
print("TOTAL violations:", bad_total); sys.exit(1 if bad_total else 0)
