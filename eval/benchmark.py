#!/usr/bin/env python3
"""PaperLM factual-coherence benchmark.  One number per failure mode a student would notice.
RAW  = constrained decoding only (syntax/schema guaranteed), verifier OFF, first sample  -> measures the *model*.
FULL = constrained decoding + verifier + resampling (what ships in the app)                -> measures the *engine*.
usage: benchmark.py --ckpt best.pt --label v2 [--n 200] [--prev eval/results/benchmark_v1.json]"""
import argparse, collections, json, os, random, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, "..", "engine"), os.path.join(HERE, "..", "data"), "/tmp/paperlm/engine", "/tmp/paperlm/data", "/tmp/paperlm"]
import paper_setter as PS, verify as VF
ap = argparse.ArgumentParser(); ap.add_argument("--ckpt"); ap.add_argument("--onnx"); ap.add_argument("--label", required=True); ap.add_argument("--n", type=int, default=200)
ap.add_argument("--val", default="/tmp/paperlm/gold2/val.txt"); ap.add_argument("--train", default="/tmp/paperlm/gold2/stageB.txt"); ap.add_argument("--lex", default="/tmp/paperlm/gold2/lexicon.json")
ap.add_argument("--tok", default="/tmp/paperlm/tok/paperlm_tokenizer.json"); ap.add_argument("--prev", default=""); ap.add_argument("--out", default="/tmp/paperlm/evalout"); ap.add_argument("--seed", type=int, default=5)
ap.add_argument("--full_n", type=int, default=60); ap.add_argument("--live", type=int, default=0); ap.add_argument("--temp", type=float, default=0.75)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
be = PS.OrtBackend(a.onnx) if a.onnx else PS.TorchBackend(a.ckpt); eng = PS.Engine(be, a.tok, seed=a.seed)
if os.path.exists(a.lex): eng.load_lexicon(a.lex)
H = re.compile(r"<\|board=(\w+)\|><\|level=(\w+)\|><\|subj=([^|]+)\|><\|unit\|>(.*?)<\|marks=(\d+)\|><\|type=(\w+)\|>")
prompts = [H.search(l).groups() for l in open(a.val, encoding="utf-8") if H.search(l)]
prompts = [(b, l, s.replace("<|subj=", ""), u, int(m), t) for b, l, s, u, m, t in prompts]; random.Random(a.seed).shuffle(prompts)
by = collections.defaultdict(list)
for p in prompts: by[(p[1], p[5] == "MCQ")].append(p)
sel = []; 
while len(sel) < a.n and any(by.values()):
    for k in list(by):
        if by[k] and len(sel) < a.n: sel.append(by[k].pop())
norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
train_q = set(); train_ex = {}
for l in open(a.train, encoding="utf-8"):
    m = re.search(r"<\|q\|>(.*?)(?:<\|oa\||<\|part\||<\|end\|)", l)
    if m: train_q.add(norm(m.group(1))[:120])
lex_all = eng.lexicon

# ---------- RAW
eng.verify_on = False; raw = []; t0 = time.time(); n_dead = 0
for (b, l, s, u, m, t) in sel:
    h = eng.header(b, l, s, u, m, t); hid = eng.tok.encode(h).ids
    st = eng._try_once(hid, t, m, True, a.temp, 0.92, 520)
    if st is None: n_dead += 1; continue
    it = eng.finalize(st, b, l, s, u, m, t)
    if it: raw.append((it, u, s))
eng.verify_on = True
issues = collections.Counter(); ok = 0; anchored = 0; copies = 0; arith_bad = 0; key_bad = 0; opt_bad = 0; mcq_n = 0; arith_n = 0; q_seen = set()
for it, u, s in raw:
    v = VF.verify_item(it, unit=u, lexicon=lex_all.get(s) or lex_all.get("*"), strict_anchor=bool(lex_all)); ok += v["ok"]
    for i in v["issues"]: issues[re.sub(r"\(.*|: .*", "", i)[:36]] += 1
    anchored += (v["anchor"]["hits"] > 0 or v["anchor"]["lex"] >= 2)
    if it["kind"] == "mcq":
        mcq_n += 1; key_bad += bool(VF.check_key(it["options"], it["key"], it["explanation"])); opt_bad += bool(VF.check_options(it["options"], it["question"]))
    txt = " ".join([it["question"], it.get("explanation") or "", it.get("rubric") or "", *[p["text"] for p in it.get("parts", [])]]); arith_bad += bool(VF.check_arith(txt))
    k = norm(it["question"])[:120]; copies += k in train_q; q_seen.add(k)
nr = max(1, len(raw))
RAW = {"n_prompts": len(sel), "constraint dead-end rate": round(n_dead / len(sel), 3), "raw verifier pass rate": round(ok / nr, 3), "arithmetic error rate": round(arith_bad / nr, 3),
       "MCQ key-mismatch rate": round(key_bad / max(1, mcq_n), 3), "MCQ option-inhomogeneity rate": round(opt_bad / max(1, mcq_n), 3), "concept-anchor rate": round(anchored / nr, 3),
       "verbatim copy of training stem": round(copies / nr, 3), "distinct stems": round(len(q_seen) / nr, 3), "raw seconds/item": round((time.time() - t0) / len(sel), 2)}
# ---------- FULL
eng.stats = dict(attempts=0, items=0, rejects={}, dead_ends=0); fails = 0; t1 = time.time(); fsel = sel[:a.full_n]; att = []
for (b, l, s, u, m, t) in fsel:
    try: it = eng.generate_item(b, l, s, u, m, t, attempts=12, temperature=a.temp); att.append(it["attempts"])
    except PS.ItemGenerationError: fails += 1
FULL = {"full-engine success rate": round(1 - fails / len(fsel), 3), "mean attempts to verified item": round(sum(att) / max(1, len(att)), 2), "full seconds/item": round((time.time() - t1) / len(fsel), 2)}
res = dict(label=a.label, ckpt=a.ckpt or a.onnx, raw=RAW, full=FULL, raw_issue_counts=dict(issues.most_common(12)), engine_rejects=dict(sorted(eng.stats["rejects"].items(), key=lambda x: -x[1])[:10]))
if a.ckpt:
    import torch; d = torch.load(a.ckpt, map_location="cpu"); res["val_loss"] = d.get("val_loss"); res["val_clean"] = d.get("val_clean")
json.dump(res, open(f"{a.out}/benchmark_{a.label}.json", "w"), indent=1); print(json.dumps(res, indent=1))
if a.live:
    import live_status as LS
    cur = {**{k: v for k, v in RAW.items() if k != "n_prompts"}, **FULL}; prev = {}
    if a.prev and os.path.exists(a.prev): pj = json.load(open(a.prev)); prev = {**pj["raw"], **pj["full"]}
    LS.update("eval", label=a.label, current=cur, previous=prev)
