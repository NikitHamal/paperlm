#!/usr/bin/env python3
"""Verbatim per-pack sample report (v14): one mini mock paper per shipped pack straight from the planner
(verified bank + computed numericals), with answer key, rationale and step marking scheme. No hand editing.
usage: python3 eval/verbatim_report.py [seed=11] -> eval/results/packs/samples_final_verbatim.md"""
import json, os, sys, glob, random
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, f"{R}/engine")
import pack_paper as PP
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 11
reg = {p["pack_id"]: p for p in json.load(open(f"{R}/docs/packs/pack_registry.json"))["packs"]}
L = [f"# Verbatim samples from the shipped specialist packs (planner seed {seed})", "",
     "Each paper is planned by the blueprint planner (syllabus-share quotas, anti-duplication tracker) from the pack's verified bank "
     "plus computed numericals. Source tags: gold = real NEB-style item, teacher = Qwen-32B draft that passed blind multi-order solve + entailment + distractor probes, computed = parametric solver.", ""]
for pid, p in reg.items():
    g, items, miss = PP.plan(pid, 4, 2, seed, 1); rnd = random.Random(seed + 1)
    L += [f"## {p['title']}  (`{pid}`, {p['params']:,} params, INT8 ONNX {p['onnx_mb']} MB, held-out loss {p['val_loss']})", ""]
    for n, (k, m, b) in enumerate(items, 1):
        if k == "mcq":
            o = [b["answer"]] + b["distractors"]; rnd.shuffle(o)
            L += [f"**Q{n}. [{b['unit']}; 1 mark; {b.get('src', '')}]** {b['question']}", ""] + [f"- ({'abcd'[i]}) {t}" for i, t in enumerate(o)]
            L += ["", f"Key: ({'abcd'[o.index(b['answer'])]}) {b['answer']}. Why: {b.get('why', '')}", ""]
        else:
            L += [f"**Q{n}. [{b['unit']}; {b['marks']} marks; {b.get('src', '')}]** {b['question']}", "", "Marking scheme:", ""]
            L += [f"- {s}  **[{x}]**" for s, x in PP.scheme(b["answer"], b["marks"])] + [""]
open(f"{R}/eval/results/packs/samples_final_verbatim.md", "w").write("\n".join(L))
print("wrote", len(L), "lines for", len(reg), "packs")
