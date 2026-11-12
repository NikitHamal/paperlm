#!/usr/bin/env python3
"""Android path: pack checkpoint -> pure-TensorFlow twin of PaperLM (fixed shapes, KV cache, RoPE/RMSNorm/SwiGLU) -> INT8 dynamic-range TFLite
with two signatures:  decode(ids[1,1], pos[], past_k, past_v) and prefill(ids[1,64], pos[], past_k, past_v)  (cache [L,1,H,P,Dh], P=max_seq).
Outputs logits[1,S,V] + updated caches. The cache write is a one-hot blend (no dynamic-update-slice) so it runs on every TFLite delegate.
Parity vs PyTorch is checked with the TFLite interpreter. usage: export_tflite.py <pack_id> [ckpt] [out_dir]   (CUDA hidden on purpose)"""
import json, os, sys
os.environ.setdefault("CUDA_VISIBLE_DEVICES", ""); os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
import numpy as np, torch, tensorflow as tf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(HERE, "..", "..", "model"), "/work/paperlm/model"]
from architecture import PaperLM, PaperLMConfig, rope_tables
PF = 64

class TFPaperLM(tf.Module):
    def __init__(self, sd, cfg):
        super().__init__(); self.c = cfg; self.H = cfg.n_heads; self.Dh = cfg.d_model // cfg.n_heads; self.P = cfg.max_seq; g = lambda k: tf.constant(sd[k].float().numpy())
        self.emb = g("emb.weight"); self.nf = g("norm.weight"); self.blocks = []
        for i in range(cfg.n_layers):
            p = f"blocks.{i}."; self.blocks.append({k: g(p + v) for k, v in dict(n1="n1.weight", qkv="attn.qkv.weight", o="attn.o.weight", n2="n2.weight", gate="mlp.gate.weight", up="mlp.up.weight", down="mlp.down.weight").items()})
        cos, sin = rope_tables(self.Dh, cfg.max_seq, cfg.rope_theta); self.cos, self.sin = tf.constant(cos.numpy()), tf.constant(sin.numpy())
    def rms(self, x, w): return x * tf.math.rsqrt(tf.reduce_mean(tf.square(x), -1, keepdims=True) + self.c.norm_eps) * w
    def rope(self, x, cos, sin):  # x [1,H,S,Dh]; interleaved pairs exactly like model/architecture.py
        S = tf.shape(x)[2]; x = tf.reshape(x, [1, self.H, S, self.Dh // 2, 2]); x1, x2 = x[..., 0], x[..., 1]; c, s = cos[None, None], sin[None, None]
        return tf.reshape(tf.stack([x1 * c - x2 * s, x1 * s + x2 * c], -1), [1, self.H, S, self.Dh])
    def step(self, ids, pos, pk, pv, S):
        P, H, Dh, D = self.P, self.H, self.Dh, self.c.d_model; rows = pos + tf.range(S); cos, sin = tf.gather(self.cos, rows), tf.gather(self.sin, rows)
        cols = tf.range(P)[None, :]; oh = tf.cast(tf.equal(cols, rows[:, None]), tf.float32)             # [S,P] one-hot write positions
        keep = 1.0 - tf.reduce_sum(oh, 0)[None, None, :, None]; allow = tf.less_equal(cols, rows[:, None])  # causal over absolute positions
        bias = tf.where(allow, 0.0, -1e9)[None, None]; x = tf.gather(self.emb, ids); nk, nv = [], []
        for i, b in enumerate(self.blocks):
            h = self.rms(x, b["n1"]); qkv = tf.reshape(tf.matmul(h, b["qkv"], transpose_b=True), [1, S, 3, H, Dh]); qkv = tf.transpose(qkv, [2, 0, 3, 1, 4])
            q, k, v = qkv[0], qkv[1], qkv[2]; q, k = self.rope(q, cos, sin), self.rope(k, cos, sin)
            K = pk[i] * keep + tf.einsum("sp,bhsd->bhpd", oh, k); V = pv[i] * keep + tf.einsum("sp,bhsd->bhpd", oh, v); nk.append(K); nv.append(V)
            a = tf.nn.softmax(tf.matmul(q, K, transpose_b=True) / np.sqrt(Dh) + bias, -1); y = tf.reshape(tf.transpose(tf.matmul(a, V), [0, 2, 1, 3]), [1, S, D])
            x = x + tf.matmul(y, b["o"], transpose_b=True); h = self.rms(x, b["n2"])
            x = x + tf.matmul(tf.nn.silu(tf.matmul(h, b["gate"], transpose_b=True)) * tf.matmul(h, b["up"], transpose_b=True), b["down"], transpose_b=True)
        return tf.matmul(self.rms(x, self.nf), self.emb, transpose_b=True), tf.stack(nk), tf.stack(nv)
    def sig(self, S):
        L, H, Dh, P = self.c.n_layers, self.H, self.Dh, self.P
        @tf.function(input_signature=[tf.TensorSpec([1, S], tf.int32, "ids"), tf.TensorSpec([], tf.int32, "pos"), tf.TensorSpec([L, 1, H, P, Dh], tf.float32, "past_k"), tf.TensorSpec([L, 1, H, P, Dh], tf.float32, "past_v")])
        def f(ids, pos, past_k, past_v):
            lg, k, v = self.step(ids, pos, past_k, past_v, S); return {"logits": lg, "present_k": k, "present_v": v}
        return f

def main():
    pid = sys.argv[1]; ck = sys.argv[2] if len(sys.argv) > 2 else f"/tmp/packs/{pid}/out/ckpt.pt"; out = sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(ck)
    d = torch.load(ck, map_location="cpu"); cfg = PaperLMConfig(**d["cfg"]); cfg.dropout = 0.0; tm = PaperLM(cfg); tm.load_state_dict(d["model"]); tm.eval(); m = TFPaperLM(d["model"], cfg)
    dec, pre = m.sig(1), m.sig(PF); sm = os.path.join(out, "tf_saved"); tf.saved_model.save(m, sm, signatures={"decode": dec.get_concrete_function(), "prefill": pre.get_concrete_function()})
    conv = tf.lite.TFLiteConverter.from_saved_model(sm, signature_keys=["decode", "prefill"]); conv.optimizations = [tf.lite.Optimize.DEFAULT]; blob = conv.convert()
    path = os.path.join(out, "model.tflite"); open(path, "wb").write(blob); mb = round(len(blob) / 1e6, 2)
    # ---- parity: TFLite (INT8 weights) vs PyTorch fp32 on a random prompt, then 6 decode steps; compares top-1 agreement + max logit diff
    L, H, Dh, P = cfg.n_layers, m.H, m.Dh, m.P; it = tf.lite.Interpreter(model_content=blob); rs = np.random.RandomState(0); ids = rs.randint(5, cfg.vocab_size, 70).tolist()
    pk = np.zeros((L, 1, H, P, Dh), np.float32); pv = pk.copy(); pos = 0; agree = []; diffs = []; tl = []
    with torch.no_grad(): ref = tm(torch.tensor([ids]))[0].numpy()
    pf, dc = it.get_signature_runner("prefill"), it.get_signature_runner("decode")
    for c0 in range(0, len(ids), PF):
        ch = ids[c0:c0 + PF]; n = len(ch); r = pf(ids=np.array([ch + [0] * (PF - n)], np.int32), pos=np.int32(c0), past_k=pk, past_v=pv); pk, pv = r["present_k"], r["present_v"]
        lg = r["logits"][0][:n]; diffs.append(float(np.abs(lg - ref[c0:c0 + n]).max())); agree += (lg.argmax(-1) == ref[c0:c0 + n].argmax(-1)).tolist()
    # decode continuation parity (last prompt token re-fed at its position must reproduce prefill logits)
    r = dc(ids=np.array([[ids[-1]]], np.int32), pos=np.int32(len(ids) - 1), past_k=pk, past_v=pv); agree.append(int(r["logits"][0, 0].argmax() == ref[-1].argmax()))
    rep = dict(pack=pid, tflite_mb=mb, top1_agreement=round(float(np.mean(agree)), 4), max_logit_diff=round(max(diffs), 3), signatures=["decode", "prefill"], prefill_chunk=PF, cache_len=P)
    json.dump(rep, open(os.path.join(out, "tflite_report.json"), "w"), indent=1); print(rep)

if __name__ == "__main__": main()
