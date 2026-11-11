#!/usr/bin/env python3
"""Keep only statement-like concept anchors (definitions, laws, formulas with prose) in concept_bank.json facts; drop bare calculation fragments."""
import json, re, sys
sys.path[:0] = ["/tmp/paperlm/engine", "engine", "../engine"]
import ground as GR
p = sys.argv[1]; b = json.load(open(p, encoding="utf-8")); kept = dropped = 0
for key, units in b["facts"].items():
    for u in list(units):
        good = []
        for t in units[u]:
            prose = re.sub(r"\$[^$]*\$", " ", t); words = GR.cwords(prose)
            ok = len(words) >= 4 and len(re.sub(r"[^A-Za-z ]", "", prose)) >= 35 and not re.match(r"^\$.*\$\.?$", t.strip()) and not re.search(r"\b(students|mistake|forgot|forgotten|common error|trap|option|answer)\b", t, re.I)
            (good.append(t) if ok else None); kept += ok; dropped += not ok
        if good: units[u] = good
        else: del units[u]
b["facts"] = {k: v for k, v in b["facts"].items() if v}
json.dump(b, open(p, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":")); print("facts kept", kept, "dropped", dropped)
