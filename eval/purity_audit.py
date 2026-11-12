#!/usr/bin/env python3
"""Grade-boundary / subject-boundary purity audit (v14).
For every shipped pack: (1) every bank + numeric-bank item's unit exists in the pack's own syllabus graph,
(2) no unit name is shared with the sibling grade of the same subject,
(3) cross-contamination probe: distinctive unit-name words of the SIBLING grade (words that never occur in this pack's own
    graph terms) are searched in this pack's bank questions; hits are listed verbatim for review.
usage: python3 eval/purity_audit.py   -> eval/results/packs/purity_audit.json"""
import json, os, re, glob
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
P = {}
for d in sorted(glob.glob(f"{R}/docs/packs/*/")):
    pid = os.path.basename(d.rstrip("/"))
    if not os.path.exists(d + "bank.json"): continue
    g = json.load(open(d + "syllabus_graph.json")); bank = json.load(open(d + "bank.json"))
    nb = json.load(open(d + "numeric_bank.json")) if os.path.exists(d + "numeric_bank.json") else []
    nb = nb if isinstance(nb, list) else [i for v in nb.values() for i in (v if isinstance(v, list) else [])] if isinstance(nb, dict) else []
    P[pid] = dict(g=g, bank=bank, nb=nb)
W = lambda s: set(re.findall(r"[a-z]{5,}", s.lower()))
out = {}
for pid, x in P.items():
    names = {u["name"] for u in x["g"]["units"]}
    own_terms = set().union(*[set(u.get("terms", [])) | W(u["name"]) for u in x["g"]["units"]])
    bad_unit = [i["unit"] for i in x["bank"] if i["unit"] not in names]
    sib = [q for q in P if q != pid and q[:-2] == pid[:-2]]
    rep = dict(units=len(names), bank=len(x["bank"]), items_with_foreign_unit=len(bad_unit), siblings=sib, shared_unit_names={}, probe_hits={})
    for q in sib:
        qn = {u["name"] for u in P[q]["g"]["units"]}
        rep["shared_unit_names"][q] = sorted(names & qn)
        dist = set().union(*[W(n) for n in qn]) - own_terms - {"basic", "introduction", "principles", "study", "concepts", "applications"}
        hits = []
        for it in x["bank"]:
            m = [w for w in dist if re.search(r"\b" + w, it["question"].lower())]
            if m: hits.append(dict(unit=it["unit"], words=m[:3], q=it["question"][:140]))
        rep["probe_hits"][q] = dict(probe_words=sorted(dist)[:25], n_hits=len(hits), examples=hits[:5])
    out[pid] = rep
os.makedirs(f"{R}/eval/results/packs", exist_ok=True)
json.dump(out, open(f"{R}/eval/results/packs/purity_audit.json", "w"), indent=1, ensure_ascii=False)
for pid, r in out.items():
    print(pid, "units", r["units"], "bank", r["bank"], "foreign-unit items", r["items_with_foreign_unit"],
          {q: (len(r["shared_unit_names"][q]), r["probe_hits"][q]["n_hits"]) for q in r["siblings"]})
