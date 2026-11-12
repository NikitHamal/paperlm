#!/usr/bin/env python3
"""Export PaperLM-Tiny: fp32/fp16 safetensors + weight-only INT8 ONNX (KV-cache graph) for Web (onnxruntime-web) & Android (ORT mobile).
usage: export.py <best.pt> <tokenizer.json> <val.txt> <outdir>"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, torch.nn as nn, torch.nn.functional as F
from architecture import PaperLM, PaperLMConfig
from safetensors.torch import save_file
from tokenizers import Tokenizer

class QLinear(nn.Module):
    def __init__(self, w):
        super().__init__(); s = w.abs().amax(1, keepdim=True).clamp(min=1e-8) / 127.0
        self.register_buffer("q", torch.round(w / s).clamp(-127, 127).to(torch.int8)); self.register_buffer("s", s.float())
    def forward(self, x): return F.linear(x, self.q.float() * self.s)
class QEmb(nn.Module):
    def __init__(self, w):
        super().__init__(); s = w.abs().amax(1, keepdim=True).clamp(min=1e-8) / 127.0
        self.register_buffer("q", torch.round(w / s).clamp(-127, 127).to(torch.int8)); self.register_buffer("s", s.float())
    def forward(self, idx): return self.q[idx].float() * self.s[idx]
    @property
    def weight(self): return self.q.float() * self.s

def quantize(model):
    for b in model.blocks:
        for mod, names in ((b.attn, ["qkv", "o"]), (b.mlp, ["gate", "up", "down"])):
            for n in names: setattr(mod, n, QLinear(getattr(mod, n).weight.data))
    model.emb = QEmb(model.emb.weight.data); return model

class Wrap(nn.Module):
    def __init__(self, m): super().__init__(); self.m = m; m.return_cache = True
    def forward(self, ids, past_k, past_v):
        lg, k, v = self.m(ids, past_k, past_v); return lg[:, -1:, :], k, v

def val_loss(model, tok, path, dev, seq=512):
    items = [tok.encode(l.rstrip("\n")).ids[:seq] for l in open(path, encoding="utf-8") if l.strip()]
    rows, cur = [], []
    for it in items:
        if len(cur) + len(it) > seq: rows.append(cur); cur = []
        cur += it
    rows.append(cur)
    X = torch.zeros(len(rows), seq, dtype=torch.long)
    for i, r in enumerate(rows): X[i, :len(r)] = torch.tensor(r)
    model.eval(); model.return_cache = False; L = N = 0
    with torch.no_grad():
        for i in range(0, len(X), 32):
            x = X[i:i + 32].to(dev); lg = model(x[:, :-1]).float()
            L += F.cross_entropy(lg.reshape(-1, lg.shape[-1]), x[:, 1:].reshape(-1), ignore_index=0, reduction="sum").item(); N += (x[:, 1:] != 0).sum().item()
    return L / N

def main():
    ck, tokp, valp, out = sys.argv[1:5]; os.makedirs(out, exist_ok=True); dev = "cuda" if torch.cuda.is_available() else "cpu"
    d = torch.load(ck, map_location=dev); cfg = PaperLMConfig(**d["cfg"]); cfg.dropout = 0.0
    tok = Tokenizer.from_file(tokp); rep = {}
    m = PaperLM(cfg).to(dev); m.load_state_dict(d["model"]); rep["params"] = m.n_params(); rep["val_fp32"] = val_loss(m, tok, valp, dev)
    sd = {k: v.detach().cpu().contiguous() for k, v in m.state_dict().items()}
    save_file(sd, f"{out}/paperlm_tiny_fp32.safetensors"); save_file({k: v.half() for k, v in sd.items()}, f"{out}/paperlm_tiny_fp16.safetensors")
    mh = PaperLM(cfg).to(dev); mh.load_state_dict({k: v.half().float() for k, v in sd.items()}); rep["val_fp16"] = val_loss(mh, tok, valp, dev)
    q = quantize(PaperLM(cfg).to(dev).eval() if False else (lambda mm: (mm.load_state_dict(d["model"]), mm)[1])(PaperLM(cfg).to(dev)).eval())
    rep["val_int8"] = val_loss(q, tok, valp, dev)
    qs = {k: v.cpu() for k, v in q.state_dict().items() if k.endswith((".q", ".s")) or "norm" in k or k.endswith("weight") and "emb" not in k and ".q" not in k}
    save_file({k: v.contiguous() for k, v in q.state_dict().items()}, f"{out}/paperlm_tiny_int8.safetensors")
    w = Wrap(q).cpu().eval(); L, H, D = cfg.n_layers, cfg.n_heads, cfg.d_model // cfg.n_heads
    ids = torch.randint(5, 100, (1, 7)); pk = torch.randn(L, 1, H, 5, D) * 0.1; pv = torch.randn(L, 1, H, 5, D) * 0.1
    torch.onnx.export(w, (ids, pk, pv), f"{out}/paperlm_tiny_int8.onnx", input_names=["ids", "past_k", "past_v"], output_names=["logits", "present_k", "present_v"],
                      dynamic_axes={"ids": {1: "S"}, "past_k": {3: "P"}, "past_v": {3: "P"}, "logits": {}, "present_k": {3: "T"}, "present_v": {3: "T"}},
                      opset_version=17, do_constant_folding=False, dynamo=False)
    import onnxruntime as ort, numpy as np
    s = ort.InferenceSession(f"{out}/paperlm_tiny_int8.onnx", providers=["CPUExecutionProvider"])
    lo, k, v = s.run(None, {"ids": ids.numpy(), "past_k": pk.numpy(), "past_v": pv.numpy()})
    with torch.no_grad(): t = w(ids, pk, pv)
    rep["onnx_vs_torch_maxdiff"] = float(np.abs(lo - t[0].numpy()).max())
    # empty-cache path (P=0) parity
    pk0 = np.zeros((L, 1, H, 0, D), np.float32); lo0, _, _ = s.run(None, {"ids": ids.numpy(), "past_k": pk0, "past_v": pk0})
    with torch.no_grad(): t0 = w(ids, torch.zeros(L, 1, H, 0, D), torch.zeros(L, 1, H, 0, D))
    rep["onnx_empty_cache_maxdiff"] = float(np.abs(lo0 - t0[0].numpy()).max())
    for f in os.listdir(out):
        rep["size_MB_" + f] = round(os.path.getsize(f"{out}/{f}") / 1e6, 2)
    rep["ppl_fp32"] = math.exp(rep["val_fp32"]); rep["ppl_int8"] = math.exp(rep["val_int8"])
    json.dump(rep, open(f"{out}/export_report.json", "w"), indent=1); print(json.dumps(rep, indent=1))
if __name__ == "__main__": main()
