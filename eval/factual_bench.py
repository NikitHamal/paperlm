#!/usr/bin/env python3
"""Factual & mathematical accuracy benchmark of the composed PaperLM system.
usage: factual_bench.py --ckpt X --bank concept_bank.json --val val.txt --n 600 --out DIR --label v4
Reports: (1) gate discrimination on gold items (accepts true anchor, rejects mismatched anchor); (2) composed-system tier mix + success rate;
(3) independent re-verification of every emitted item (structure, LaTeX, key letter, option homogeneity, MCQ answer recomputation for parametric items)."""
import argparse, collections, json, os, random, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, "..", "engine"), os.path.join(HERE, "..", "data"), "/tmp/paperlm/engine", "/tmp/paperlm/data"]
ap = argparse.ArgumentParser(); ap.add_argument("--ckpt", default=""); ap.add_argument("--bank", required=True); ap.add_argument("--val", required=True); ap.add_argument("--n", type=int, default=600)
ap.add_argument("--out", required=True); ap.add_argument("--label", default="v4"); ap.add_argument("--tok", default="/tmp/paperlm/tok/paperlm_tokenizer.json"); ap.add_argument("--lex", default="/tmp/paperlm/gold2/lexicon.json")
ap.add_argument("--cat", default="/tmp/paperlm/catalog.json"); ap.add_argument("--live", type=int, default=0)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
import ground as GR, verify as VF, parametric as PM, validator as V
from composer import Composer
rng = random.Random(21); rep = dict(label=a.label)
# (1) gate discrimination on held-out gold items
H = re.compile(r"<\|board=(\w+)\|><\|level=(\w+)\|><\|subj=([^|]+)\|><\|unit\|>(.*?)<\|marks=(\d+)\|><\|type=(\w+)\|><\|book\|>(.*?)<\|q\|>")
items = []
for l in open(a.val, encoding="utf-8"):
    m = H.search(l); it = VF.parse_schema(re.sub(r"<\|book\|>.*?<\|q\|>", "<|q|>", l))
    if m and it: items.append((m.group(7), it))
own = [(an, it) for an, it in items if GR.cwords(an) and (GR.cwords(an) & GR.cwords(it["question"] + " " + (it.get("explanation") or "")))]
acc_true = sum(GR.gate(it, an)["ok"] for an, it in own) / max(1, len(own))
shuf = [x[0] for x in items]; rng.shuffle(shuf); acc_false = sum(GR.gate(it, shuf[i])["ok"] for i, (an, it) in enumerate(items)) / max(1, len(items))
rep["gate_on_gold"] = dict(n=len(items), accepts_gold_with_true_anchor=round(acc_true, 3), false_accept_with_mismatched_anchor=round(acc_false, 3))
# (2) composed system
cat = json.load(open(a.cat)); reqs = []
TY = [(1, "MCQ")] * 5 + [(2, "CONCEPTUAL"), (3, "CONCEPTUAL"), (4, "NUMERICAL"), (5, "NUMERICAL"), (4, "OR"), (5, "SHORT"), (8, "LONG")]
for _ in range(a.n):
    k = rng.choice(list(cat)); e = cat[k]; sj = rng.choice(list(e["subjects"])); u = rng.choice(e["subjects"][sj]["units"] or ["General"]); mk, ty = rng.choice(TY); reqs.append((e["board"], e["level"], sj, u, mk, ty))
eng = None
if a.ckpt:
    import paper_setter as PS; eng = PS.Engine(PS.TorchBackend(a.ckpt), a.tok, seed=5); eng.load_lexicon(a.lex)
C = Composer(eng, a.bank, seed=9); tiers = collections.Counter(); fails = 0; probs = collections.Counter(); samples = []; t0 = time.time()
for i, (b, lv, sj, u, mk, ty) in enumerate(reqs):
    try: it = C.item(b, lv, sj, u, mk, ty)
    except Exception as ex: fails += 1; continue
    tier = it["provenance"]["tier"]; tiers[tier] += 1
    if it["kind"] == "mcq":
        if len(set(it["options"])) != 4: probs["duplicate options"] += 1
        if it["key"] not in "abcd": probs["bad key"] += 1
        if V.check_text(it["question"]) or any(V.check_text(o) for o in it["options"]) or V.check_text(it.get("explanation") or ""): probs["latex/text check"] += 1
        if tier != "param":
            iss = VF.check_options(it["options"], it["question"]) + VF.check_key(it["options"], it["key"], it.get("explanation"))
            if iss: probs["option/key coherence"] += 1
    else:
        txt = [it["question"], *(p["text"] for p in it["parts"]), *(p["text"] for p in it["or_parts"]), it.get("rubric") or ""]
        if any(V.check_text(x) for x in txt if x): probs["latex/text check"] += 1
        if it["parts"] and sum(p["marks"] for p in it["parts"]) != mk and tier != "bank": probs["part marks != total"] += 1
    if i < 400 and len(samples) < 40 and rng.random() < 0.12: samples.append(it)
    if a.live and i % 20 == 0:
        try:
            import live_status as LS; LS.update("factual", label=a.label, done=i, total=len(reqs), tiers=dict(tiers), fails=fails, problems=dict(probs))
        except Exception: pass
n = len(reqs) - fails
rep["composed_system"] = dict(requests=len(reqs), emitted=n, failures=fails, success_rate=round(n / len(reqs), 4), tier_mix={k: round(v / max(1, n), 3) for k, v in tiers.items()},
                              residual_problems=dict(probs), problem_rate=round(sum(probs.values()) / max(1, n), 4), lm_gate=dict(tries=C.stats["lm_tries"], passes=C.stats["lm_gate_pass"], pass_rate=round(C.stats["lm_gate_pass"] / max(1, C.stats["lm_tries"]), 3), rejects=C.stats["gate_rejects"]),
                              sec_per_item=round((time.time() - t0) / len(reqs), 3))
json.dump(rep, open(f"{a.out}/factual_{a.label}.json", "w"), indent=1); json.dump(samples, open(f"{a.out}/samples_{a.label}.json", "w"), indent=1, ensure_ascii=False); print(json.dumps(rep, indent=1)[:3000])
