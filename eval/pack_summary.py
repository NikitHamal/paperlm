#!/usr/bin/env python3
"""Builds eval/results/packs/summary.md from docs/packs/*: params, MB (ONNX + TFLite), held-out val loss/ppl (UNSEEN anchors), SFT/DPO bench, bank sizes, Node bench."""
import glob, json, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); D = f"{R}/docs/packs"; O = f"{R}/eval/results/packs"; os.makedirs(O, exist_ok=True)
J = lambda p: json.load(open(p)) if os.path.exists(p) else {}
bench = J(f"{O}/bench.json"); rows = ["| pack | params | ONNX INT8 MB | TFLite INT8 MB (top-1 agree) | train / val items | held-out val loss (ppl) | gate rate (SFT -> final) | bank MCQ / short | node neural / bank / empty |", "|---|---|---|---|---|---|---|---|---|"]
for pid in sorted(os.listdir(D)):
    if not os.path.isdir(f"{D}/{pid}"): continue
    m = J(f"{D}/{pid}/pack.json"); tr = J(f"{R}/packs/{pid}/train_report.json"); tf = J(f"{D}/{pid}/tflite_report.json"); b = dict(bench.get(pid, {})); bk = J(f"{D}/{pid}/bank.json"); bi = bk if isinstance(bk, list) else bk.get('items', []); b['bank_mcq'] = sum(1 for i in bi if i.get('type') == 'mcq'); b['bank_short'] = sum(1 for i in bi if i.get('type') != 'mcq')
    rows.append(f"| {pid} | {m.get('params', 0) / 1e6:.2f}M | {m.get('onnx_mb')} | {tf.get('tflite_mb', '-')} ({tf.get('top1_agreement', '-')}) | {tr.get('n_train_items')} / {tr.get('n_val_items')} | {tr.get('val_loss')} ({tr.get('ppl')}) | "
                f"{tr.get('bench_sft', {}).get('strict_gate_rate')} -> {tr.get('bench_final', {}).get('strict_gate_rate')} | {b.get('bank_mcq', '-')} / {b.get('bank_short', '-')} | {b.get('neural_accepted', '-')} / {b.get('bank_fallback', '-')} / {b.get('empty', '-')} |")
open(f"{O}/summary.md", "w").write("\n".join(rows) + "\n"); print("\n".join(rows))
