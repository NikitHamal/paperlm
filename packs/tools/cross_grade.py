#!/usr/bin/env python3
"""v15 grade-boundary dedupe: for every subject, a question that is (near-)identical (token Jaccard >= 0.7) in the class-11 and class-12 bank is kept ONLY in the pack
whose own syllabus graph (unit names, terms, fact text) explains its anchor better; the other copy is dropped.  usage: cross_grade.py [--dry]"""
import json, os, re, sys, glob
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
W = lambda s: set(re.findall(r"[a-z0-9]{3,}", s.lower()))
def vocab(pid):
    g = json.load(open(f"{R}/docs/packs/{pid}/syllabus_graph.json")); v = {}
    for u in g["units"]:
        for w in W(u["name"] + " " + " ".join(u.get("terms", []))): v[w] = v.get(w, 0) + 3
        for f in u.get("facts", []):
            for w in W(f["text"]): v[w] = v.get(w, 0) + 1
    return v
def score(it, v): return sum(1 for w in W(it["anchor"] + " " + it["question"]) if w in v) / max(1, len(W(it["anchor"] + " " + it["question"])))
subs = {}
for p in sorted(glob.glob(f"{R}/docs/packs/*/bank.json")): pid = p.split("/")[-2]; subs.setdefault(re.sub(r"\d+$", "", pid), []).append(pid)
tot = {}
for sub, pids in subs.items():
    if len(pids) < 2: continue
    a, b = pids[0], pids[1]; A = json.load(open(f"{R}/docs/packs/{a}/bank.json")); B = json.load(open(f"{R}/docs/packs/{b}/bank.json")); va, vb = vocab(a), vocab(b)
    wb = [(W(x["question"]), i) for i, x in enumerate(B)]; da, db = set(), set()
    for i, x in enumerate(A):
        w = W(x["question"])
        for v, j in wb:
            if j in db: continue
            if len(w & v) / max(1, len(w | v)) >= 0.7:
                if score(x, va) >= score(B[j], vb): db.add(j)
                else: da.add(i)
                break
    tot[sub] = {a: len(da), b: len(db)}
    if "--dry" not in sys.argv:
        json.dump([x for i, x in enumerate(A) if i not in da], open(f"{R}/docs/packs/{a}/bank.json", "w"), ensure_ascii=False, separators=(",", ":"))
        json.dump([x for i, x in enumerate(B) if i not in db], open(f"{R}/docs/packs/{b}/bank.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("cross_grade dropped", json.dumps(tot))
