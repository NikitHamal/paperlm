#!/usr/bin/env python3
"""Apply the 32B judge audit + teacher-verified items to docs/model/bank.json.
usage: apply_judge.py JUDGE_DIR [TEACHER_JSONL] ; writes docs/model/bank.json, eval/results/v7/{judge_report.json,flagged_mcq.json,flagged_written.json}"""
import json, sys, os, collections
J = sys.argv[1]; T = sys.argv[2] if len(sys.argv) > 2 else None
BANK = "docs/model/bank.json"; OUT = "eval/results/v7"; os.makedirs(OUT, exist_ok=True)
bank = json.load(open(BANK))
if os.path.exists(OUT + "/bank_before_v7.json.gz") is False:
    import gzip; gzip.open(OUT + "/bank_before_v7.json.gz", "wt").write(json.dumps(bank))
s1 = {}
for l in open(f"{J}/judge_stage1.jsonl"):
    d = json.loads(l); s1[d["id"]] = d
s2 = {}
for l in open(f"{J}/judge_stage2.jsonl"):
    d = json.loads(l); s2[d["id"]] = d
DROP = os.environ.get("DROP") == "1"  # default OFF: the 32B judge is wrong on ~all sampled disagreements (see PAPERLM_STATUS.md)
rep = collections.Counter(); flag_m = []; flag_w = []
for sk, units in bank["seeds"].items():
    for un, lst in units.items():
        keep = []
        for i, it in enumerate(lst):
            id_ = f"{sk}#{un}#{i}"; d = s1.get(id_)
            if d is None: keep.append(it); rep["not_judged"] += 1; continue
            if d["kind"] == "mcq":
                rep["mcq_judged"] += 1
                c = s2.get(id_)
                if d["agree"] and d["p_key"] >= 0.5: it["j"] = 1; rep["mcq_confirmed_blind"] += 1
                elif c and c["agree"]: it["j"] = 1; rep["mcq_confirmed_cot"] += 1
                elif c and c["cot_pred"] and not c["agree"]:
                    flag_m.append(dict(id=id_, q=it["q"], o=it["o"], key=it["k"], blind=d["pred"], p_key=round(d["p_key"], 3), cot=c["cot_pred"], tail=c["tail"][-160:])); rep["mcq_flagged_for_review"] += 1
                    if DROP: continue
                else: rep["mcq_unconfirmed_kept"] += 1
            else:
                rep["written_judged"] += 1
                if d["p_yes"] < float(os.environ.get("W_DROP", 0.05)):
                    flag_w.append(dict(id=id_, q=it["q"][:200], p_yes=round(d["p_yes"], 3))); rep["written_flagged_for_review"] += 1
                    if DROP: continue
                if d["p_yes"] >= 0.8: it["j"] = 1; rep["written_confirmed"] += 1
                else: rep["written_unconfirmed_kept"] += 1
            keep.append(it)
        units[un] = keep
added = collections.Counter()
if T and os.path.exists(T):
    for l in open(T):
        r = json.loads(l); bank["seeds"].setdefault(r["sk"], {}).setdefault(r["unit"], []).append(r["item"]); added[r["sk"].split("|")[2]] += 1; rep["teacher_added"] += 1
bank["version"] = str(bank.get("version", "8")) + "+v7"
json.dump(bank, open(BANK, "w"), ensure_ascii=False, separators=(",", ":"))
rep["total_after"] = sum(len(l) for u in bank["seeds"].values() for l in u.values())
json.dump(dict(rep), open(OUT + "/judge_report.json", "w"), indent=1)
json.dump(flag_m, open(OUT + "/flagged_mcq.json", "w"), ensure_ascii=False, indent=1); json.dump(flag_w, open(OUT + "/flagged_written.json", "w"), ensure_ascii=False, indent=1)
json.dump(dict(added), open(OUT + "/teacher_added_by_subject.json", "w"), indent=1)
print(json.dumps(dict(rep), indent=1))
