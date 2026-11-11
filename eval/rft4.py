#!/usr/bin/env python3
"""Grounded rejection fine-tuning + factual benchmark for the concept-conditioned model (v4+).
  gen   : python3 rft4.py gen   --ckpt X --shard i --nshards n --per 500 --out DIR [--split train|val]   candidates passing verify + grounding gate -> DIR/cand_i.jsonl (+ raw gate stats)
  merge : python3 rft4.py merge --out DIR --dest stageR.txt --replay stage4_clean.txt
  bench : python3 rft4.py bench --ckpt X --out DIR --label v4a                                          (after gen --split val) summarises raw gate pass-rate, hallucinated-number rate, ...
The gate is engine/ground.py (numbers must come from the anchor, explanation grounded in the anchor, no second-correct distractor, key supported)."""
import argparse, collections, glob, json, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, "..", "engine"), os.path.join(HERE, "..", "data"), "/tmp/paperlm/engine", "/tmp/paperlm/data"]
ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("--ckpt"); ap.add_argument("--shard", type=int, default=0); ap.add_argument("--nshards", type=int, default=1)
ap.add_argument("--per", type=int, default=400); ap.add_argument("--out", required=True); ap.add_argument("--split", default="train"); ap.add_argument("--dest", default="/tmp/paperlm/gold4/stageR.txt")
ap.add_argument("--replay", default="/tmp/paperlm/gold4/stage4_clean.txt"); ap.add_argument("--bank", default="/tmp/paperlm/gold4/concept_bank.json"); ap.add_argument("--val", default="/tmp/paperlm/gold4/val.txt")
ap.add_argument("--tok", default="/tmp/paperlm/tok/paperlm_tokenizer.json"); ap.add_argument("--lex", default="/tmp/paperlm/gold2/lexicon.json"); ap.add_argument("--temp", type=float, default=0.75)
ap.add_argument("--label", default="v4"); ap.add_argument("--tries", type=int, default=6); ap.add_argument("--beta", type=float, default=2.5)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
H = re.compile(r"<\|board=(\w+)\|><\|level=(\w+)\|><\|subj=([^|]+)\|><\|unit\|>(.*?)<\|marks=(\d+)\|><\|type=(\w+)\|><\|book\|>(.*?)<\|q\|>")
if a.mode == "gen":
    import paper_setter as PS, ground as GR, verify as VF
    if a.split == "val": prompts = [H.search(l).groups() for l in open(a.val, encoding="utf-8") if H.search(l)]
    else:
        bank = json.load(open(a.bank, encoding="utf-8")); prompts = []; rr = random.Random(99)
        TYPES = [(1, "MCQ")] * 6 + [(2, "CONCEPTUAL"), (3, "CONCEPTUAL"), (4, "CONCEPTUAL"), (3, "SHORT"), (5, "SHORT"), (4, "NUMERICAL")]
        for key, units in bank["facts"].items():
            b, lv, sj = key.split("|")
            for u, fs in units.items():
                for f in fs:
                    m, t = rr.choice(TYPES); prompts.append((b, lv, sj, u, str(m), t, f))
        rr.shuffle(prompts)
    mine = prompts[a.shard::a.nshards][:a.per]; eng = PS.Engine(PS.TorchBackend(a.ckpt), a.tok, seed=700 + a.shard); eng.load_lexicon(a.lex)
    f = open(f"{a.out}/cand_{a.shard}.jsonl", "w"); raw = collections.Counter(); iss = collections.Counter(); ok_prompts = 0
    for i, (b, lv, sj, u, m, t, anc) in enumerate(mine):
        won = False
        for k in range(a.tries):
            raw["attempts"] += 1
            try: it = eng.generate_item(b, lv, sj, u, int(m), t, attempts=1, temperature=min(1.0, a.temp + 0.05 * k), anchor=anc, bias_beta=a.beta)
            except PS.ItemGenerationError: raw["dead_end_or_verify_reject"] += 1; continue
            raw["structurally_valid"] += 1; g = GR.gate(it, anc)
            for x in g["issues"]: iss[re.sub(r"[: ].*", "", x) if x.startswith("number") else x[:48]] += 1
            if g["ok"]:
                raw["gate_pass"] += 1
                if not won: raw["prompts_resolved"] += 1; won = True; raw["first_pass_at_%d" % (k + 1)] += 1
                txt = it["schema_text"].replace("<|q|>", f"<|book|>{anc}<|q|>", 1); f.write(json.dumps(dict(text=txt, p=g["p"], r=g["r"], tries=k + 1, kind=it["kind"], anchor=anc)) + "\n"); f.flush()
                if a.split != "val": break
        raw["prompts"] += 1
        if i % 50 == 0: print(a.shard, i, dict(raw), flush=True)
    json.dump(dict(raw=dict(raw), issues=dict(iss.most_common(12))), open(f"{a.out}/stats_{a.shard}.json", "w"))
elif a.mode == "merge":
    cands = [json.loads(l) for p in sorted(glob.glob(f"{a.out}/cand_*.jsonl")) for l in open(p)]; seen, sel = set(), []
    for c in sorted(cands, key=lambda c: (c["tries"], -c["p"])):
        k = re.sub(r"[^a-z0-9]", "", c["text"].split("<|q|>", 1)[1][:160].lower())
        if k in seen: continue
        seen.add(k); sel.append(c["text"])
    rep = [l.rstrip("\n") for l in open(a.replay, encoding="utf-8") if l.strip()]; random.Random(3).shuffle(rep); lines = sel + rep[:max(2000, len(sel))]; random.Random(4).shuffle(lines)
    open(a.dest, "w", encoding="utf-8").write("\n".join(lines) + "\n"); st = dict(candidates=len(cands), selected=len(sel), replay=len(lines) - len(sel)); json.dump(st, open(f"{a.out}/rft_stats.json", "w")); print(st)
else:
    tot = collections.Counter(); iss = collections.Counter()
    for p in glob.glob(f"{a.out}/stats_*.json"):
        d = json.load(open(p)); tot.update(d["raw"]); iss.update(d["issues"])
    ra = max(1, tot["attempts"]); r = dict(label=a.label, prompts=tot["prompts"], attempts=tot["attempts"], structurally_valid_rate=round(tot["structurally_valid"] / ra, 3), raw_gate_pass_rate=round(tot["gate_pass"] / ra, 3),
                                           prompts_resolved_rate=round(tot["prompts_resolved"] / max(1, tot["prompts"]), 3), numbers_invented_rate=round(sum(v for k, v in iss.items() if k.startswith("number")) / ra, 3), top_issues=dict(iss.most_common(8)))
    json.dump(r, open(f"{a.out}/bench_{a.label}.json", "w"), indent=1); print(json.dumps(r, indent=1))
