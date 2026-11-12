#!/usr/bin/env python3
"""Android path: static-shape (S=256) full-sequence TFLite export of a pack via ai-edge-torch (needs `pip install ai-edge-torch`), plus ORT-mobile
(.onnx INT8 KV-cache, already shipped) as the primary Android runtime.  usage: export_tflite.py <pack_id> [seq=256]"""
import json, os, sys, torch
sys.path[:0] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "model"), "/work/paperlm/model"]
from architecture import PaperLM, PaperLMConfig
import ai_edge_torch
pid = sys.argv[1]; S = int(sys.argv[2]) if len(sys.argv) > 2 else 256; O = f"/tmp/packs/{pid}/out"
d = torch.load(f"{O}/ckpt.pt", map_location="cpu"); cfg = PaperLMConfig(**d["cfg"]); cfg.dropout = 0.0; m = PaperLM(cfg); m.load_state_dict(d["model"]); m.eval()
class W(torch.nn.Module):
    def __init__(s, m): super().__init__(); s.m = m
    def forward(s, ids): return s.m(ids)
x = torch.randint(5, 100, (1, S), dtype=torch.int32).long(); edge = ai_edge_torch.convert(W(m).eval(), (x,)); edge.export(f"{O}/model_s{S}.tflite")
print("tflite MB", round(os.path.getsize(f"{O}/model_s{S}.tflite") / 1e6, 2))
