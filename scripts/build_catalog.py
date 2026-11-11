"""Build docs/model/catalog.json (board/level -> subject -> units, types, marks) from engine/syllabus_index.json."""
import json, collections, os
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, "..")
s = json.load(open(os.path.join(R, "engine/syllabus_index.json")))
LABEL = {("NEB","C12"):"NEB Class 12",("NEB","C11"):"NEB Class 11",("SEE","C10"):"SEE Class 10",("BLE","C8"):"BLE Class 8",("IOE","IOE"):"IOE entrance",("CEE","CEE"):"CEE entrance",("TU","BCA"):"BCA entrance",("CTEVT","BSN"):"BSc Nursing",("IOE","BE"):"BE (engineering)"}
cat = collections.OrderedDict()
for (b, l), lab in LABEL.items():
    cat[f"{b}|{l}"] = dict(label=lab, board=b, level=l, subjects=collections.OrderedDict())
for k, n in s["combos"].items():
    b, l, sub, t, m = k.split("|"); e = cat.get(f"{b}|{l}")
    if not e: continue
    d = e["subjects"].setdefault(sub, dict(units=[], types={}))
    d["types"].setdefault(t, {})[m] = d["types"].get(t, {}).get(m, 0) + n
for k, e in cat.items():
    for sub, d in e["subjects"].items():
        d["units"] = s["units"].get(f"{e['board']}|{e['level']}|{sub}", []) or ["General"]
        d["types"] = {t: sorted(m, key=int) for t, m in d["types"].items()}
json.dump(cat, open(os.path.join(R, "docs/model/catalog.json"), "w"), separators=(",", ":"))
print({k: len(v["subjects"]) for k, v in cat.items()})
