#!/usr/bin/env python3
"""Publish trained packs: /tmp/packs/<id>/out -> docs/packs/<id>/ (web+Android assets) and packs/<id>/ (reports); rebuild pack_registry.json.  usage: publish.py <pack_id...>"""
import json, os, shutil, sys
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")); SP = json.load(open(f"{R}/packs/pack_specs.json"))
for pid in sys.argv[1:]:
    o = f"/tmp/packs/{pid}/out"; d = f"{R}/docs/packs/{pid}"; r = f"{R}/packs/{pid}"; os.makedirs(d, exist_ok=True); os.makedirs(r, exist_ok=True)
    for f in ["model.onnx", "tokenizer.json", "pack.json", "syllabus_graph.json"]: shutil.copy(f"{o}/{f}", f"{d}/{f}")
    json.dump(SP[pid].get("numeric", []), open(f"{d}/numeric_templates.json", "w"))
    # verified bank: gold NEB items + teacher items that passed blind multi-order solve / entailment / per-distractor probes (all stored with provenance)
    import glob, re
    bank, seen = [], set(); rd = lambda f: [json.loads(l) for l in open(f)] if os.path.exists(f) else []
    for src, files in (("gold", [f"/tmp/packs/{pid}/gold_items.jsonl"]), ("teacher", sorted(glob.glob(f"/tmp/packs/{pid}/verified*.jsonl")))):
        for it in sum([rd(f) for f in files], []):
            k = re.sub(r"\W+", " ", it["question"].lower()).strip()
            if k in seen: continue
            seen.add(k); b = {x: it[x] for x in ("type", "marks", "unit", "question", "answer", "anchor") if x in it}; b["src"] = src
            if it["type"] == "mcq": b["distractors"] = it["distractors"]; b["why"] = it.get("why", "")
            if "scores" in it: b["scores"] = it["scores"]
            bank.append(b)
    json.dump(bank, open(f"{d}/bank.json", "w"), ensure_ascii=False, separators=(",", ":"))
    for f in ["model.tflite", "tflite_report.json"]:
        if os.path.exists(f"{o}/{f}"): shutil.copy(f"{o}/{f}", f"{d}/{f}")
    for f in ["train_report.json", "samples.json"]: shutil.copy(f"{o}/{f}", f"{r}/{f}")
    shutil.copy(f"/tmp/packs/{pid}/syllabus_graph.json", f"{r}/syllabus_graph.json")
reg = []
for pid in SP:
    p = f"{R}/docs/packs/{pid}/pack.json"
    if os.path.exists(p): m = json.load(open(p)); reg.append({k: m[k] for k in ["pack_id", "title", "level", "subject", "params", "onnx_mb", "val_loss"]} | {"numeric": len(SP[pid].get("numeric", []))})
json.dump(dict(version=2, packs=reg), open(f"{R}/docs/packs/pack_registry.json", "w"), indent=1); shutil.copy(f"{R}/docs/packs/pack_registry.json", f"{R}/packs/pack_registry.json"); print("registry", [x["pack_id"] for x in reg])
