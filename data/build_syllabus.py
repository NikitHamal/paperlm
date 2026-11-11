#!/usr/bin/env python3
"""Derive engine/syllabus_index.json (level|subject -> unit names ranked by frequency, plus supported types/marks) from gold.jsonl.
Contains only unit/chapter NAMES (no question text)."""
import collections, json, sys
gold, out = sys.argv[1], sys.argv[2]
units = collections.defaultdict(collections.Counter); combos = collections.Counter()
for l in open(gold, encoding="utf-8"):
    g = json.loads(l)
    if g["unit"] != "General" and not g["unit"].lower().startswith("paper"): units[f'{g["board"]}|{g["level"]}|{g["subj"]}'][g["unit"]] += 1
    combos[f'{g["board"]}|{g["level"]}|{g["subj"]}|{g["type"]}|{g["marks"]}'] += 1
idx = {k: [u for u, c in v.most_common(40) if c >= 2] for k, v in units.items()}
idx = {k: v for k, v in idx.items() if v}
json.dump(dict(units=idx, combos={k: v for k, v in combos.items() if v >= 3}), open(out, "w"), indent=0, ensure_ascii=False)
print(len(idx), "subject keys;", sum(map(len, idx.values())), "units;", len(combos), "combos")
