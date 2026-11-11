#!/usr/bin/env python3
"""Does concept retrieval land on the right unit?  For every gold MCQ with a unit, query the bank by (board, level, subject, unit)
and check that >=1 retrieved anchor belongs to that unit and subject (coverage), plus overall index statistics."""
import json, sys, collections
sys.path.insert(0, "engine"); from concept_bank import ConceptBank
cb = ConceptBank(); bank = json.load(open("docs/model/bank.json")); n = hit = 0; cov = collections.Counter(); tot = collections.Counter()
for sk, us in bank["seeds"].items():
    b, l, s = sk.split("|")
    for u in us:
        n += 1; r = cb.retrieve(b, l, s, u, 3); ok = any(x["u"].lower() == u.lower() for x in r); hit += ok; tot[b] += 1; cov[b] += ok
rep = dict(units=n, units_with_anchor=hit, coverage=round(hit / n, 4), by_board={k: f"{cov[k]}/{tot[k]}" for k in tot}, concepts=len(cb.c))
print(json.dumps(rep)); json.dump(rep, open("eval/results/v9/concept_eval.json", "w"), indent=1)
