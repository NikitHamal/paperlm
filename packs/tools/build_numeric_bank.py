#!/usr/bin/env python3
"""Pre-computed numeric bank per pack (docs/packs/<id>/numeric_bank.json): K distinct instances of every numeric template the pack owns,
computed by engine/parametric.py (key and distractors are derived from the formula, never written by a language model).
Android (TFLite app, no expression evaluator needed), the Python mock-paper planner and any offline client read this file directly.
usage: build_numeric_bank.py [pack_id ...] [--k 24]"""
import json, os, random, sys
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")); sys.path.insert(0, f"{R}/engine")
import parametric as P


def build(pid, k=24):
    ids = json.load(open(f"{R}/docs/packs/{pid}/numeric_templates.json")); out = []
    for tid in ids:
        t = P.TEMPLATES[tid]; seen = set()
        for seed in range(k * 12):
            if len(seen) >= k: break
            r = random.Random(f"{pid}:{tid}:{seed}"); inst = P.instantiate(t, r)
            if not inst: continue
            rd = P.render(inst, 1, r)
            if rd["stem"] in seen or "@" in json.dumps(rd) or len(set(rd["options"])) != 4: continue
            seen.add(rd["stem"]); ki = "abcd".index(rd["key"])
            out.append(dict(type="mcq", marks=1, unit=t["unit"], question=rd["stem"], answer=rd["options"][ki],
                            distractors=[o for i, o in enumerate(rd["options"]) if i != ki], anchor=rd["law"], why=rd["law"] + " " + " ".join(rd["steps"]),
                            src="computed", tpl=tid))
    json.dump(out, open(f"{R}/docs/packs/{pid}/numeric_bank.json", "w"), ensure_ascii=False, separators=(",", ":")); return len(out), len(ids)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]; k = int(sys.argv[sys.argv.index("--k") + 1]) if "--k" in sys.argv else 24
    a = [x for x in a if not x.isdigit()] or [p["pack_id"] for p in json.load(open(f"{R}/docs/packs/pack_registry.json"))["packs"]]
    for pid in a:
        n, m = build(pid, k); print(pid, "templates", m, "items", n, os.path.getsize(f"{R}/docs/packs/{pid}/numeric_bank.json") // 1024, "KB")
