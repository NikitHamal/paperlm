#!/usr/bin/env python3
"""Android-readiness check: every shipped docs/packs/<id>/model.tflite (INT8, signatures decode/prefill) is run through the TFLite interpreter on a REAL
syllabus prompt (answer-first format) and greedy-decoded for N steps next to the shipped INT8 ONNX; reports token agreement and logit top-1 agreement.
needs tensorflow (or tflite-runtime) + onnxruntime + tokenizers. usage: python3 eval/tflite_check.py [steps=24] [pack ids...] -> eval/results/packs/tflite_check.json"""
import json, os, sys, time
import numpy as np, onnxruntime as ort
from tokenizers import Tokenizer
try:
    import tensorflow as tf; Interp = tf.lite.Interpreter
except Exception:
    from tflite_runtime.interpreter import Interpreter as Interp
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 24
reg = json.load(open(f"{R}/docs/packs/pack_registry.json"))["packs"]; ids = sys.argv[2:] or [p["pack_id"] for p in reg]; out = {}
for pid in ids:
    d = f"{R}/docs/packs/{pid}"; M = json.load(open(f"{d}/pack.json")); G = json.load(open(f"{d}/syllabus_graph.json")); tok = Tokenizer.from_file(f"{d}/tokenizer.json")
    L, H, Dh, P = M["layers"], M["heads"], M["head_dim"], M["max_seq"]; PF = 64
    u = G["units"][len(G["units"]) // 2]; f = u["facts"][0]["text"]
    prompt = tok.encode(f"<|bos|><|pack={pid}|><|type=mcq|><|marks=1|><|unit|>{u['name']}<|book|>{f}<|ans|>").ids[: P - STEPS - 1]
    sess = ort.InferenceSession(f"{d}/model.onnx", providers=["CPUExecutionProvider"])
    pk = np.zeros((L, 1, H, 0, Dh), np.float32); pv = pk.copy(); lg, pk, pv = sess.run(None, {"ids": np.array([prompt], np.int64), "past_k": pk, "past_v": pv}); ref = []; t = int(lg[0, -1].argmax())
    for _ in range(STEPS):
        ref.append(t); lg, pk, pv = sess.run(None, {"ids": np.array([[t]], np.int64), "past_k": pk, "past_v": pv}); t = int(lg[0, -1].argmax())
    it = Interp(model_path=f"{d}/model.tflite"); it.allocate_tensors(); pf, dc = it.get_signature_runner("prefill"), it.get_signature_runner("decode")
    ck = np.zeros((L, 1, H, P, Dh), np.float32); cv = ck.copy(); t0 = time.time(); last = None
    for c0 in range(0, len(prompt), PF):
        ch = prompt[c0:c0 + PF]; n = len(ch); r = pf(ids=np.array([ch + [0] * (PF - n)], np.int32), pos=np.int32(c0), past_k=ck, past_v=cv); ck, cv = r["present_k"], r["present_v"]; last = r["logits"][0][n - 1]
    got = []; t = int(last.argmax()); pos = len(prompt)
    for _ in range(STEPS):
        got.append(t); r = dc(ids=np.array([[t]], np.int32), pos=np.int32(pos), past_k=ck, past_v=cv); ck, cv = r["present_k"], r["present_v"]; t = int(r["logits"][0, 0].argmax()); pos += 1
    lead = 0
    while lead < STEPS and got[lead] == ref[lead]: lead += 1
    out[pid] = dict(tflite_mb=round(os.path.getsize(f"{d}/model.tflite") / 1e6, 2), onnx_mb=M["onnx_mb"], prompt_tokens=len(prompt), steps=STEPS,
                    greedy_token_agreement=round(float(np.mean([a == b for a, b in zip(got, ref)])), 3), identical_prefix=lead, seconds=round(time.time() - t0, 1),
                    tflite_text=tok.decode(got), onnx_text=tok.decode(ref))
    print(pid, {k: v for k, v in out[pid].items() if "text" not in k}, flush=True)
os.makedirs(f"{R}/eval/results/packs", exist_ok=True); json.dump(out, open(f"{R}/eval/results/packs/tflite_check.json", "w"), indent=1, ensure_ascii=False)
