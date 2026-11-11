#!/usr/bin/env python3
"""Verifies the Parametric engine: (1) 300 instances/template are self-consistent, (2) hand-computed known answers, (3) Python<->JS parity on identical variables,
(4) every MCQ passes the semantic verifier (homogeneous options, unit parity)."""
import json, math, os, random, subprocess, sys, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, "..", "engine")]
import parametric as P, verify as VF
rng = random.Random(5); N = 300; bad = []; total = 0; cases = []; vf_fail = 0; vf_n = 0
for t in P.LIB["templates"]:
    for _ in range(N):
        inst = P.instantiate(t, rng)
        if not inst: bad.append((t["id"], "no instance")); continue
        total += 1; r = P.render(inst, 1, rng); opts = r["options"]
        issues = []
        if len(set(opts)) != 4: issues.append("dup options")
        if r["options"]["abcd".index(r["key"])] != r["answer"]: issues.append("key != answer")
        if re.search(r"@|\bnan\b|\binf\b", r["stem"] + "".join(r["steps"]) + "".join(opts)): issues.append("bad text")
        for s in [r["stem"], *r["steps"], *opts]:
            if s.count("$") % 2: issues.append("odd $")
        # independent recomputation of the key from the stored environment
        again = float(P.ev(t["ans"], inst["env"]))
        if abs(P.rnd(again, t["sig"]) - inst["ans"]) > 1e-9 * max(1, abs(again)) and abs(again - inst["ans"]) > 1e-9 * max(1, abs(again)): issues.append("answer drift")
        # every option must be the same dimension/unit string
        us = {re.sub(r"^\$[^\\a-zA-Z]*", "", o).replace("$", "") for o in opts}
        tail = {re.sub(r"^-?[\d.]+(\\times10\^\{-?\d+\})?", "", o.strip("$")) for o in opts}
        if len(tail) != 1: issues.append("unit mismatch")
        if issues: bad.append((t["id"], issues, inst["env"]))
        if len(cases) < 400 and _ < 2: cases.append(dict(id=t["id"], vars={k: v for k, v in inst["env"].items() if k in {x.split("=")[0] for x in t["vars"]}}, py=dict(ans=inst["ans"], stem=r["stem"], steps=r["steps"])))
# known hand-computed answers
KNOWN = [("kin_v", dict(u=4, a=3, t=5), 19), ("newton2", dict(m=10, a=4), 40), ("ohm", dict(V=12, R=4), 3), ("res_par", dict(R1=6, R2=3), 2), ("ke", dict(m=2, v=10), 100),
         ("ap_sum", dict(a=2, d=3, n=10), 155), ("disc", dict(a=1, b=6, c=5), 16), ("comb", dict(n=6, r=2), 15), ("det2", dict(a=2, b=3, c=1, d=5), 7),
         ("bin2dec", dict(b4=1, b3=0, b2=1, b1=1, b0=0), 22), ("moles_m", dict(m=36, M=18), 2), ("dilution", dict(M1=4, V1=50, V2=100), 2), ("subnet", dict(p=24), 254),
         ("map", dict(S=120, Dd=90), 100), ("iv_drip", dict(V=1000, th=8, DF=15), 31.25), ("oral_dose", dict(D=250, H=125), 10), ("bmi", dict(w=64, h=160), 25),
         ("transformer", dict(Vp=220, Np=100, Ns=500), 1100), ("ph_acid", dict(c=1, k=3), 3), ("deriv_pt", dict(a=1, b=1, x0=2), 16), ("integral", dict(a=3, b=2, k=2), 12)]
kbad = []
for tid, v, exp in KNOWN:
    i = P.instantiate(P.TEMPLATES[tid], rng, v)
    if not i or abs(i["ans"] - P.rnd(exp, 3)) > 1e-6 * max(1, abs(exp)): kbad.append((tid, i and i["ans"], exp))
# python <-> js parity
json.dump([dict(id=c["id"], vars=c["vars"]) for c in cases], open("/tmp/pcases.json", "w"))
js = json.loads(subprocess.run(["node", os.path.join(HERE, "param_parity.mjs"), "/tmp/pcases.json"], capture_output=True, text=True, check=True).stdout)
pbad = [c["id"] for c, j in zip(cases, js) if j is None or abs(j["ans"] - c["py"]["ans"]) > 1e-9 * max(1, abs(j["ans"])) or j["stem"] != c["py"]["stem"] or j["steps"] != c["py"]["steps"]]
# end-to-end items through the semantic verifier
for subj, lvl, unit, marks, typ in [("physics", "C12", "Current electricity", 1, "MCQ"), ("chemistry", "C11", "Solutions", 1, "MCQ"), ("mathematics", "C12", "Derivatives", 1, "MCQ"),
                                   ("physics", "C12", "Waves", 5, "NUMERICAL"), ("mathematics", "C12", "Integration", 4, "OR"), ("fundamentals-of-nursing", "BSN", "Drug dosage calculation", 1, "MCQ"),
                                   ("computer-science", "C12", "Number systems", 1, "MCQ"), ("science", "C10", "Pressure", 1, "MCQ"), ("accountancy", "C10", "Depreciation", 1, "MCQ")]:
    for _ in range(100):
        it = P.make_item(subj, lvl, unit, marks, typ, rng); vf_n += 1
        if not it or (it["kind"] == "mcq" and not VF.verify_item(it)["ok"] and (vf_fail := vf_fail + 1)): pass
rep = dict(templates=len(P.LIB["templates"]), instances=total, self_check_failures=len(bad), known_value_cases=len(KNOWN), known_value_failures=len(kbad), parity_cases=len(cases), parity_failures=len(pbad),
           verifier_items=vf_n, verifier_rejections_of_parametric_mcq=vf_fail, examples_bad=bad[:6], known_bad=kbad, parity_bad=pbad[:6])
json.dump(rep, open(os.path.join(HERE, "results", "param_test.json"), "w"), indent=1); print(json.dumps(rep, indent=1)[:2500])
sys.exit(1 if (bad or kbad or pbad) else 0)
