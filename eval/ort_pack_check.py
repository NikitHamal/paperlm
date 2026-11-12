#!/usr/bin/env python3
"""Deterministic Python-onnxruntime check of every shipped pack (docs/packs/<id>): loads INT8 ONNX + subject-pure tokenizer, runs FSM-constrained
best-of-K generation on real syllabus anchors with the same grounding gate as the web harness, and falls back to the verified bank.
usage: python3 eval/ort_pack_check.py [slots_per_pack=6] [K=3] [pack ids...]   -> eval/results/packs/ort_check.json"""
import json, os, random, re, sys, time
import numpy as np, onnxruntime as ort
from tokenizers import Tokenizer
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); sys.path.insert(0, f"{R}/packs/tools"); import fsm
N = int(sys.argv[1]) if len(sys.argv) > 1 else 6; K = int(sys.argv[2]) if len(sys.argv) > 2 else 3
reg = json.load(open(f"{R}/docs/packs/pack_registry.json"))["packs"]; ids = sys.argv[3:] or [p["pack_id"] for p in reg]; report = {}; rng = random.Random(5)
for pid in ids:
    d = f"{R}/docs/packs/{pid}"; M = json.load(open(f"{d}/pack.json")); G = json.load(open(f"{d}/syllabus_graph.json")); tok = Tokenizer.from_file(f"{d}/tokenizer.json")
    bank = json.load(open(f"{d}/bank.json")); T = fsm.tok_tables(tok); sess = ort.InferenceSession(f"{d}/model.onnx", providers=["CPUExecutionProvider"]); L, H, Dh = M["layers"], M["heads"], M["head_dim"]
    def run(ids_, past):
        pk, pv = past if past else (np.zeros((L, 1, H, 0, Dh), np.float32),) * 2
        lg, k, v = sess.run(None, {"ids": np.array([ids_], np.int64), "past_k": pk, "past_v": pv}); return lg[0, -1], (k, v)
    UT = {u["id"]: set(u["terms"]) for u in G["units"]}; t0 = time.time(); acc = fb = 0; samples = []; units = set(); tries = 0
    for s in range(N):
        u = rng.choices(G["units"], weights=[x["share"] for x in G["units"]])[0]; f = rng.choice(u["facts"]); kind = "mcq" if s % 3 else "short"; marks = 1 if kind == "mcq" else 3
        prompt = f"<|bos|><|pack={pid}|><|type={kind}|><|marks={marks}|><|unit|>{u['name']}<|book|>{f['text']}<|ans|>"; best = None
        for _ in range(K):
            tries += 1; lg, past = run(tok.encode(prompt).ids, None); st = fsm.State(T, kind); bias = np.zeros(T["V"], np.float32); bias[list(set(tok.encode(f["text"]).ids))] = 1.0; lp = 0.0
            for _step in range(420):
                if st.done: break
                m = st.mask(); l = np.where(m, lg + bias, -1e9) / 0.75; p = np.exp(l - l.max()); p /= p.sum(); o = np.argsort(-p); c = np.cumsum(p[o]); keep = o[: max(1, int((c - p[o] <= 0.92).sum()))]
                q = p[keep] / p[keep].sum(); t = int(rng.choices(list(keep), weights=list(q))[0]); lp += float(np.log(p[t] + 1e-12)); st.feed(t)
                if not st.done: lg, past = run([t], past)
            if not st.done: continue
            segs = st.segs(); sc, ff = fsm.grounding(segs, kind, f["text"], UT.get(u["id"], ())) if "id" in G["units"][0] else (0, {})
            if best is None or sc > best[0]: best = (sc, ff, segs)
        ok = best and best[0] >= 0.85 and (kind == "short" or best[1].get("distinct") and best[1].get("homog") and best[1].get("ans_ground", 0) >= 0.8)
        if ok: acc += 1; src = "neural"; segs = best[2]
        else:
            pool = [b for b in bank if b["unit"] == u["name"] and b["type"] == kind] or [b for b in bank if b["type"] == kind]; b = rng.choice(pool); fb += 1; src = "bank:" + b["src"]
            segs = [b["answer"], b["question"]] + ([*b["distractors"], b.get("why", "")] if kind == "mcq" else [])
        units.add(u["name"]); samples.append(dict(unit=u["name"], kind=kind, source=src, segs=segs))
    report[pid] = dict(params=M["params"], onnx_mb=M["onnx_mb"], val_loss=M["val_loss"], slots=N, neural_accepted=acc, bank_fallback=fb, attempts=tries, units_hit=len(units), bank_items=len(bank), seconds=round(time.time() - t0, 1), samples=samples)
    print(pid, {k: v for k, v in report[pid].items() if k != "samples"}, flush=True)
os.makedirs(f"{R}/eval/results/packs", exist_ok=True); json.dump(report, open(f"{R}/eval/results/packs/ort_check.json", "w"), indent=1, ensure_ascii=False)
