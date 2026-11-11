#!/usr/bin/env python3
"""Apply the cross-family verdicts (eval/cross_verify.py) to a bank, then run the coherence gate v2.
  gold items          : x:1 when the second family confirms (P+E+D); never deleted (judges are not ground truth) -> disputed ones go to a review queue
  teacher items (T32v): kept ONLY if the second family also confirms (two independent families must agree), otherwise dropped
usage: merge_cross.py bank_in.json cross_checked.jsonl out_bank.json report_dir"""
import json, sys, re, os, collections
sys.path.insert(0, os.path.dirname(__file__)); import coherence_gate as G

bp, cp, out, rd = sys.argv[1:5]; os.makedirs(rd, exist_ok=True)
bank = json.load(open(bp)); norm = lambda s: re.sub(r"[^a-z0-9]+", "", (s or "").lower())
res = {}
for l in open(cp):
    r = json.loads(l); res[(r["sk"], r["unit"], norm(r["item"]["q"]))] = r
st = collections.Counter(); disputed = []; dropped = []
for sk, us in bank["seeds"].items():
    for u in list(us):
        keep = []
        for it in us[u]:
            r = res.get((sk, u, norm(it.get("q"))))
            teacher = it.get("v") in ("T32", "T32v")
            if r is None:
                if teacher: st["teacher_unchecked_dropped"] += 1; dropped.append(dict(sk=sk, unit=u, q=it.get("q"), why="not cross-checked")); continue
                keep.append(it); continue
            ok = r["xpass"]; it.pop("x", None)
            if teacher:
                if ok: it["x"] = 1; st["teacher_kept_x"] += 1; keep.append(it)
                else: st["teacher_dropped_disagree"] += 1; dropped.append(dict(sk=sk, unit=u, q=it.get("q"), chk=r["chk"], why="second family disagrees"))
            else:
                if ok: it["x"] = 1; st["gold_confirmed"] += 1
                else: st["gold_disputed"] += 1; disputed.append(dict(sk=sk, unit=u, item=it, chk=r["chk"]))
                keep.append(it)
        us[u] = keep
nb = 0; flagged = []
for sk, us in bank["seeds"].items():
    for u in list(us):
        good = []
        for it in us[u]:
            iss = G.check(it)
            if iss: flagged.append(dict(sk=sk, unit=u, issues=iss, q=(it.get("q") or "")[:200])); st["coherence_dropped"] += 1
            else: good.append(it)
        us[u] = good; nb += len(good)
json.dump(bank, open(out, "w"), ensure_ascii=False, separators=(",", ":"))
json.dump(dict(summary=dict(st, bank_items=nb), disputed_gold=disputed), open(os.path.join(rd, "cross_gold_disputed.json"), "w"), ensure_ascii=False, indent=1)
json.dump(dict(dropped_teacher=dropped, coherence=flagged), open(os.path.join(rd, "cross_dropped.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(dict(st, bank_items=nb)))
