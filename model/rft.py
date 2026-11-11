#!/usr/bin/env python3
"""Stage C: verifier-guided rejection sampling (expert iteration).  The current model generates candidates under the constrained engine,
the verifier (homogeneous options, key supported by explanation, arithmetic, concept anchors) accepts only coherent items, and the accepted
items (plus a replay slice of verified gold) become the fine-tuning set  -> the model is pulled toward its own *verified-correct* mode.
  gen   : rft.py gen --ckpt X --shard i --nshards n --per 400 --out /tmp/paperlm/rft/<tag>      (run n copies in parallel)
  merge : rft.py merge --out DIR --gold stageB.txt --dest stageC.txt --replay 0.5"""
import argparse, collections, glob, json, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, "..", "engine"), os.path.join(HERE, "..", "data"), "/tmp/paperlm/engine", "/tmp/paperlm/data"]
ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("--ckpt"); ap.add_argument("--shard", type=int, default=0); ap.add_argument("--nshards", type=int, default=1); ap.add_argument("--per", type=int, default=400)
ap.add_argument("--out", required=True); ap.add_argument("--gold", default="/tmp/paperlm/gold2/stageB.txt"); ap.add_argument("--dest", default="/tmp/paperlm/gold2/stageC.txt"); ap.add_argument("--replay", type=float, default=0.5)
ap.add_argument("--tok", default="/tmp/paperlm/tok/paperlm_tokenizer.json"); ap.add_argument("--lex", default="/tmp/paperlm/gold2/lexicon.json"); ap.add_argument("--temp", type=float, default=0.8)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
H = re.compile(r"<\|board=(\w+)\|><\|level=(\w+)\|><\|subj=([^|]+)\|><\|unit\|>(.*?)<\|marks=(\d+)\|><\|type=(\w+)\|>")
norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
if a.mode == "gen":
    import paper_setter as PS
    lines = [l for l in open(a.gold, encoding="utf-8") if H.search(l)]; random.Random(1234).shuffle(lines)
    mine = lines[a.shard::a.nshards][:a.per]; eng = PS.Engine(PS.TorchBackend(a.ckpt), a.tok, seed=100 + a.shard); eng.load_lexicon(a.lex)
    f = open(f"{a.out}/cand_{a.shard}.jsonl", "w"); n_ok = 0
    for i, l in enumerate(mine):
        b, lv, s, u, m, t = H.search(l).groups(); s = s.replace("<|subj=", "")
        try: it = eng.generate_item(b, lv, s, u, int(m), t, attempts=4, temperature=a.temp)
        except PS.ItemGenerationError: continue
        n_ok += 1; f.write(json.dumps(dict(text=it["schema_text"], score=it["verify"]["score"], attempts=it["attempts"], level=lv, type=t)) + "\n"); f.flush()
        if i % 50 == 0: print(a.shard, i, n_ok, flush=True)
else:
    cands = [json.loads(l) for p in sorted(glob.glob(f"{a.out}/cand_*.jsonl")) for l in open(p)]
    gold = [l.rstrip("\n") for l in open(a.gold, encoding="utf-8") if l.strip()]; gold_stems = set(norm(re.search(r"<\|q\|>(.*?)(?:<\|oa\||<\|part\||<\|end\|)", g).group(1))[:120] for g in gold if "<|q|>" in g)
    seen, keep = set(), []
    for c in sorted(cands, key=lambda c: (-c["score"], c["attempts"])):
        m = re.search(r"<\|q\|>(.*?)(?:<\|oa\||<\|part\||<\|end\|)", c["text"]); k = norm(m.group(1))[:120] if m else ""
        if not k or k in seen: continue
        seen.add(k); c["novel"] = k not in gold_stems; keep.append(c)
    novel = [c for c in keep if c["novel"]]; sel = [c["text"] for c in (novel if len(novel) > 200 else keep)]
    random.Random(7).shuffle(gold); nrep = int(len(sel) * a.replay / max(1e-6, 1 - a.replay)) if sel else len(gold); lines = sel + gold[:max(nrep, 1000)]; random.Random(8).shuffle(lines)
    open(a.dest, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    st = dict(candidates=len(cands), unique=len(keep), novel=len(novel), selected=len(sel), replay=len(lines) - len(sel), mean_score=round(sum(c["score"] for c in keep) / max(1, len(keep)), 3))
    json.dump(st, open(f"{a.out}/rft_stats.json", "w")); print(st)
