"""Side-by-side samples (previous vs current checkpoint) for the live dashboard + the report.  usage: sample_compare.py PREV.pt CUR.pt PREV_LABEL CUR_LABEL out.json"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, "..", "engine"), "/tmp/paperlm/engine", "/tmp/paperlm/data", "/tmp/paperlm"]
import paper_setter as PS
prev, cur, pl, cl, out = sys.argv[1:6]
P = [("NEB", "C12", "physics", "Magnetic field", 1, "MCQ"), ("SEE", "C10", "science", "Heredity", 1, "MCQ"), ("IOE", "IOE", "mathematics", "Calculus", 1, "MCQ"),
     ("NEB", "C11", "chemistry", "Chemical bonding", 5, "CONCEPTUAL"), ("NEB", "C12", "mathematics", "Derivatives", 5, "NUMERICAL"), ("CEE", "CEE", "physics", "Waves and Sound", 1, "MCQ")]
def fmt(it):
    if it["kind"] == "mcq": return f"[{it['board']} {it['level']} {it['subject']} / {it['unit']}] {it['question']}\n" + "\n".join(f"  ({l}) {o}" for l, o in zip("abcd", it["options"])) + f"\n  Answer: {it['key']}  {it['explanation']}"
    return f"[{it['board']} {it['level']} {it['subject']} / {it['unit']} / {it['marks']}M] {it['question']}\n" + "\n".join(f"  ({p['label']}) {p['text']} [{p['marks']}]" for p in it["parts"]) + f"\n  Rubric: {it['rubric']}"
def run(ck, unverified):
    e = PS.Engine(PS.TorchBackend(ck), "/tmp/paperlm/tok/paperlm_tokenizer.json", seed=21)
    if os.path.exists("/tmp/paperlm/gold2/lexicon.json"): e.load_lexicon("/tmp/paperlm/gold2/lexicon.json")
    e.verify_on = not unverified; res = []
    for (b, l, s, u, m, t) in P:
        try: res.append(fmt(e.generate_item(b, l, s, u, m, t, attempts=1 if unverified else 12)))
        except PS.ItemGenerationError: res.append(f"[{b} {l} {s} / {u}] (constraint dead-end on the first sample)")
    return res
r = dict(prev_label=pl, label=cl, prev_items=run(prev, True), items=run(cur, True), prev_items_full=run(prev, False), items_full=run(cur, False)); json.dump(r, open(out, "w"), indent=1)
try:
    import live_status as LS; LS.update("samples", step=-1, items=r["items"], prev_items=r["prev_items"], prev_label=pl, valid_rate=1.0, run=cl)
except Exception as ex: print("live", ex)
print("ok")
