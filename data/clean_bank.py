#!/usr/bin/env python3
"""Cleans the concept bank: drops exam-meta items (paper pattern / marking grids), exam-tip 'facts', and figure-dependent seeds. usage: clean_bank.py IN OUT"""
import json, re, sys
src, dst = sys.argv[1], sys.argv[2]
B = json.load(open(src, encoding="utf-8"))
JUNK_Q = re.compile(r"(group [abc] question|\d+-mark (group|question)|exam(ination)? (pattern|grid|paper pattern)|time per question|marks? per (question|minute)|minutes should|answer the question number|blueprint|\bgrid\b)", re.I)
JUNK_U = re.compile(r"(examination:? pattern|\bgrid\b|syllabus (and|overview)|how to use|about this)", re.I)
TIP = re.compile(r"(worth (one|two|three|\d+) marks?|examiners?\b|every year|exam tip|common mistake in exam|frequently asked|asked (almost )?every|high[- ]yield for the exam)", re.I)
FIG = re.compile(r"\b(figure|diagram|shown (above|below|in the)|given (below|above) (figure|diagram|graph)|following (figure|diagram|graph|picture)|circuit shown)\b", re.I)
n0 = sum(len(l) for v in B["seeds"].values() for l in v.values()); f0 = sum(len(l) for v in B["facts"].values() for l in v.values())
for k, v in list(B["seeds"].items()):
    for u, l in list(v.items()):
        if JUNK_U.search(u): del v[u]; continue
        keep = []
        for x in l:
            txt = x["q"] + " " + " ".join(x.get("o", []))
            if JUNK_Q.search(x["q"]) or FIG.search(txt): continue
            if x["c"] == "mcq" and (len(set(x["o"])) != 4 or x["k"] not in "abcd"): continue
            keep.append(x)
        if keep: v[u] = keep
        else: del v[u]
    if not v: del B["seeds"][k]
for k, v in list(B["facts"].items()):
    for u, l in list(v.items()):
        if JUNK_U.search(u): del v[u]; continue
        keep = [f for f in l if not TIP.search(f) and 25 <= len(f) <= 400]
        if keep: v[u] = keep
        else: del v[u]
    if not v: del B["facts"][k]
n1 = sum(len(l) for v in B["seeds"].values() for l in v.values()); f1 = sum(len(l) for v in B["facts"].values() for l in v.values())
B["version"] = "v5-clean"; json.dump(B, open(dst, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"seeds {n0}->{n1}  facts {f0}->{f1}")
