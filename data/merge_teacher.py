#!/usr/bin/env python3
"""Merge stage-2-verified teacher MCQs (v="T32v") into docs/model/bank.json. Idempotent: removes previous T32v items first.
usage: merge_teacher.py teacher_verified.jsonl [bank.json]"""
import json, sys, re
src = sys.argv[1]; bp = sys.argv[2] if len(sys.argv) > 2 else "docs/model/bank.json"
bank = json.load(open(bp)); n0 = sum(len(v) for s in bank["seeds"].values() for v in s.values())
for s in bank["seeds"].values():
    for u in list(s):
        s[u] = [x for x in s[u] if x.get("v") != "T32v"]
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()
def jac(a, b):
    A, B = set(norm(a).split()), set(norm(b).split()); return len(A & B) / max(1, len(A | B))
added = 0
for l in open(src):
    r = json.loads(l); it = r["item"]; it["v"] = "T32v"; it["o"] = [re.sub(r"^\(?[A-Da-d][\).:]\s+", "", o) for o in it["o"]]
    pool = bank["seeds"].setdefault(r["sk"], {}).setdefault(r["unit"], [])
    if any(jac(x["q"], it["q"]) > 0.7 for x in pool): continue
    pool.append(it); added += 1
json.dump(bank, open(bp, "w"), ensure_ascii=False, separators=(",", ":"))
print("added", added, "bank items before", n0)
