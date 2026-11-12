#!/usr/bin/env python3
"""Grade-pure numerical-template assignment: a parametric law template is attached to a pack only if its unit/keywords occur in THAT pack's own
syllabus_graph (unit names or term lists).  usage: assign_templates.py <pack_id...>  -> /tmp/packs/<id>/out/numeric_templates.json"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); lib = json.load(open(os.path.join(HERE, "..", "..", "engine", "param_templates.json")))
SPECS = json.load(open(os.path.join(HERE, "..", "pack_specs.json")))
W = lambda s: {w.rstrip("s") for w in re.findall(r"[a-z]{4,}", s.lower())}
for pid in sys.argv[1:]:
    S = SPECS[pid]; G = json.load(open(f"/tmp/packs/{pid}/syllabus_graph.json")); dom = {"mathematics": "maths", "computer-science": "cs"}.get(S["subject"], S["subject"])
    names = set().union(*[W(u["name"]) for u in G["units"]]); terms = set().union(*[{w.rstrip("s") for w in u["terms"]} for u in G["units"]]); facts = W(" ".join(f["text"] for u in G["units"] for f in u["facts"]))
    out = []
    for t in lib["templates"]:
        if dom not in t["dom"].split() or t["lv"] == "S" or t["id"].endswith("_s") and t["lv"] == "S": continue
        uw = W(t["unit"]); kw = set().union(*[W(k) for k in t["kw"]]) if t["kw"] else set()
        a = len(uw & names) > 0 or len(uw & terms) > 0; b = len(kw & terms) >= 2 or len(kw & facts) >= 3 and len(uw & facts) > 0
        if (a or b): out.append(t["id"])
    os.makedirs(f"/tmp/packs/{pid}/out", exist_ok=True); json.dump(out, open(f"/tmp/packs/{pid}/out/numeric_templates.json", "w")); print(pid, len(out), out)
    if os.environ.get("WRITE_SPEC"):
        sp = os.path.join(HERE, "..", "pack_specs.json"); cur = json.load(open(sp)); cur[pid]["numeric"] = out; json.dump(cur, open(sp, "w"), indent=1)
    print("   units:", [u["name"] for u in G["units"]])
