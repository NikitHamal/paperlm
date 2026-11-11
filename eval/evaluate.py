#!/usr/bin/env python3
"""PaperLM-Tiny evaluation: unconstrained baseline vs constrained PaperSetterEngine, using the shipped INT8 ONNX graph.
usage: evaluate.py <onnx> <tokenizer.json> <syllabus.json> <gold_dir> <outdir> <ckpt.pt>"""
import collections, json, os, random, re, sys, time
sys.path.insert(0, "/tmp/paperlm/engine"); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "engine"))
import numpy as np
from paper_setter import Engine, OrtBackend, TorchBackend, render_paper, ItemGenerationError
import validator as V
onnx, tokp, syl, gold, out, ckpt = sys.argv[1:7]; os.makedirs(out, exist_ok=True)
try: sys.path.insert(0, "/tmp/paperlm"); import live_status as LS
except Exception: LS = None
e = Engine(OrtBackend(onnx), tokp, syllabus_path=syl, seed=11)
train_q = set()
for l in open(f"{gold}/train.txt", encoding="utf-8"):
    m = re.search(r"<\|q\|>(.*?)(<\||$)", l)
    if m: train_q.add(re.sub(r"\W+", "", m.group(1).lower()))
CFG = [("NEB", "C12", "physics", "MCQ", 1), ("NEB", "C12", "chemistry", "CONCEPTUAL", 5), ("NEB", "C12", "mathematics", "NUMERICAL", 5), ("NEB", "C11", "biology", "MCQ", 1),
       ("SEE", "C10", "science", "SHORT", 2), ("SEE", "C10", "mathematics", "LONG", 8), ("NEB", "C12", "physics", "OR", 8), ("IOE", "IOE", "mathematics", "MCQ", 1),
       ("CEE", "CEE", "zoology", "MCQ", 1), ("BLE", "C8", "science", "CONCEPTUAL", 4), ("TU", "BCA", "mathematics", "MCQ", 1), ("IOE", "BE", "general", "OR", 10)]
rep = {}; items = []; fails = 0; lat = []; attempts = []
N = int(os.environ.get("EVAL_PER_CFG", "5"))
for ci, (b, l, s, t, m) in enumerate(CFG):
    units = e.units_for(b, l, s)
    for i in range(N):
        u = units[(i * 3 + ci) % len(units)]; t0 = time.time()
        try: it = e.generate_item(b, l, s, u, m, t)
        except ItemGenerationError: fails += 1; continue
        lat.append(time.time() - t0); attempts.append(it["attempts"]); items.append(it)
        if LS: LS.update("eval", constrained_items=len(items), failures=fails)
ok = sum(V.validate_item_text(it["schema_text"]) is None for it in items)
rep["constrained"] = dict(requested=len(CFG) * N, produced=len(items), generation_failures=fails, schema_valid_pct=round(100 * ok / max(1, len(items)), 2),
                          mean_attempts=round(float(np.mean(attempts)), 2), mean_latency_s_ort_cpu=round(float(np.mean(lat)), 2), p95_latency_s=round(float(np.percentile(lat, 95)), 2))
qs = [re.sub(r"\W+", "", it["question"].lower()) for it in items]
rep["novelty"] = dict(verbatim_in_train_pct=round(100 * sum(q in train_q for q in qs) / len(qs), 1), distinct_questions_pct=round(100 * len(set(qs)) / len(qs), 1))
mc = [it for it in items if it["kind"] == "mcq"]; rep["mcq"] = dict(n=len(mc), key_dist=dict(collections.Counter(it["key"] for it in mc)), four_distinct_options_pct=100.0 if all(len({o.lower() for o in it["options"]}) == 4 for it in mc) else 0)
wr = [it for it in items if it["kind"] == "written"]
rep["written"] = dict(n=len(wr), marks_sum_ok_pct=round(100 * sum((not any(p["marks"] for p in it["parts"])) or sum(p["marks"] for p in it["parts"]) == it["marks"] for it in wr) / max(1, len(wr)), 1), with_rubric_pct=round(100 * sum(bool(it["rubric"]) for it in wr) / max(1, len(wr)), 1), or_twin_pct_of_OR=round(100 * sum(bool(it["or_parts"]) for it in wr if it["type"] == "OR") / max(1, sum(it["type"] == "OR" for it in wr)), 1))
# unconstrained baseline (torch, same weights family)
try:
    import torch; sys.path.insert(0, "/tmp/paperlm/model")
    tb = TorchBackend(ckpt); base_ok = base_n = 0; rng = random.Random(5)
    for (b, l, s, t, m) in CFG:
        u = e.units_for(b, l, s)[0]
        for i in range(max(2, N)):
            h = e.header(b, l, s, u, m, t); ids = e.tok.encode(h).ids + [e.S["q"]]; st = tb.start(); lg, st = tb.step(ids, st); gen = []
            for _ in range(450):
                p = np.exp((lg - lg.max()) / 0.8); p /= p.sum(); nx = int(np.random.default_rng(rng.randrange(10**9)).choice(len(p), p=p)); gen.append(nx)
                if nx == e.S["end"]: break
                lg, st = tb.step([nx], st)
            inv = {v: k for k, v in e.T.id.items()}; txt = h + "<|q|>" + "".join(inv[i] if e.T.special[i] else (e.T.strs[i] or "\ufffd") for i in gen)
            base_n += 1; base_ok += (V.validate_item_text(txt) is None)
    rep["unconstrained_baseline"] = dict(n=base_n, schema_valid_pct=round(100 * base_ok / base_n, 1))
except Exception as ex: rep["unconstrained_baseline"] = dict(error=str(ex)[:200])
# full model papers
papers = []
for (b, l, s, seed) in [("NEB", "C12", "physics", 1), ("SEE", "C10", "science", 2), ("IOE", "IOE", "mathematics", 3), ("NEB", "C11", "chemistry", 4)]:
    t0 = time.time()
    try:
        p = e.model_paper(b, l, s, seed=seed); papers.append(p)
        open(f"{out}/model_paper_{b}_{l}_{s}.txt", "w").write(render_paper(p)); json.dump(p, open(f"{out}/model_paper_{b}_{l}_{s}.json", "w"), ensure_ascii=False, indent=1)
        rep.setdefault("model_papers", []).append(dict(paper=f"{b}/{l}/{s}", total_marks=p["total_marks"], questions=sum(len(x["items"]) for x in p["sections"]), seconds=round(time.time() - t0, 1)))
    except Exception as ex: rep.setdefault("model_papers", []).append(dict(paper=f"{b}/{l}/{s}", error=str(ex)[:160]))
json.dump(rep, open(f"{out}/eval_report.json", "w"), indent=1); print(json.dumps(rep, indent=1))
if LS: LS.update("eval", **{k: json.dumps(v)[:300] for k, v in rep.items()})
