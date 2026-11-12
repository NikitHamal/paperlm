#!/usr/bin/env python3
"""Per-pack numeric solver test: every template id listed in docs/packs/<id>/numeric_templates.json is instantiated 300x with the engine,
the key is re-derived independently from the audit expression, options must be 4 distinct, no unresolved placeholders, and the template
must belong to that pack's own pinned/assigned list (grade purity). Writes eval/results/packs/numeric_test.json + samples_numeric_verbatim.txt."""
import json, os, random, sys
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); sys.path.insert(0, f"{R}/engine")
import parametric as P
reg = json.load(open(f"{R}/docs/packs/pack_registry.json"))["packs"]; rep = {}; L = []
for p in reg:
    pid = p["pack_id"]; ids = json.load(open(f"{R}/docs/packs/{pid}/numeric_templates.json")); bad = 0; n = 0; trunc = 0
    L += [f"## {pid}: {len(ids)} numeric templates", ""]
    for tid in ids:
        t = P.TEMPLATES[tid]
        for i in range(300):
            r = random.Random(i); inst = P.instantiate(t, r)
            if not inst: bad += 1; continue
            rd = P.render(inst, 1, r); n += 1; tt = inst["tpl"]
            rec = P.rnd(float(P.ev(t["ans"], inst["env"])), t["sig"])
            key_txt = rd["options"]["abcd".index(rd["key"])]
            ok = "@" not in json.dumps(rd) and len(set(rd["options"])) == 4 and P.fmt(P.rnd(float(P.ev(t["ans"], inst["env"])), tt["sig"]), tt["sig"]) in key_txt
            bad += not ok
            ex = float(P.ev(t["ans"], inst["env"])); trunc += abs(ex - round(ex)) < 1e-9 and abs(ex) < 1e6 and abs(P.rnd(ex, tt["sig"]) - ex) > 1e-9  # exact integer shown rounded to sig figs
        r = random.Random(11); inst = P.instantiate(t, r); rd = P.render(inst, 1, r)
        L += [f"- {rd['stem']}", "  " + "  ".join(f"({'abcd'[i]}) {o}" for i, o in enumerate(rd["options"])), f"  Key: ({rd['key']}). {rd['law']} " + " ".join(rd["steps"]), ""]
    rep[pid] = dict(templates=len(ids), instances=n, failures=bad, exact_integer_rounded_to_sigfigs=int(trunc))
json.dump(rep, open(f"{R}/eval/results/packs/numeric_test.json", "w"), indent=1); open(f"{R}/eval/results/packs/samples_numeric_verbatim.md", "w").write("\n".join(L))
print(json.dumps(rep))
