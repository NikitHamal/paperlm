# PAPERLM_STATUS.md — PaperLM-Tiny (10M) build log (single source of truth, resume from here)

## Infra (MoLab)
- Notebook: https://sb-bc79ba58e2c2c51f.sb.molab.run/  (session id via `marimo pair notebook list`; token in local file, never committed)
- GPU: NVIDIA RTX PRO 6000 Blackwell (96 GB), 160 GB RAM, 20 CPU. torch 2.11, tokenizers, onnxruntime, safetensors preinstalled.
- Keep-alive daemon: `/tmp/paperlm/keepalive.py` (pid in `/tmp/paperlm/keepalive.pid`, heartbeat `/tmp/paperlm/heartbeat.txt`).
  Pings local + public marimo URL and runs a tiny CUDA op every 60 s; merges `/tmp/paperlm/status_*.json` into
  `/tmp/paperlm_live_status.json` every 2 s. RESTART: `setsid nohup python3 /tmp/paperlm/keepalive.py &` (do NOT `pkill -f` from the same shell).
- Live dashboard: 5 marimo cells (`molab/install_dashboard.py`, renderers in `molab/dash_lib.py`), auto-refresh 3 s.
- NEB clones on VM: `/tmp/paperlm/neb/<branch_with_underscores>` (private repo; PAT askpass removed after clone).
- Helpers (local): `scripts/molab_run.sh`, `molab_put.sh`, `molab_bg.sh`, `molab_tail.sh`.

## Pipeline & milestones
| # | Milestone | State |
|---|-----------|-------|
| 1 | MoLab paired, keep-alive, live dashboard, NEB extractor (`data/extract_neb.py`) | DONE (push 1) |
| 2 | Gold dataset builder + validator + exam-math BPE tokenizer + stats | DONE (push 2) |
| 3 | PaperLM-Tiny 10M arch, GPU training, constrained PaperSetterEngine, INT8/FP16/ONNX export, web+Android SDK, eval | DONE (push 3) |

## Corpus findings
- NEB branches that exist: main, resources/past-papers-class12, claude/engineering, claude/bsc-nursing
  (`claude/bca-entrance-complete`, `polish/school-books-claude` do not exist on the remote).
- Sources: `notes/papers/**/content/*.md` (past papers DSL `@mcq/@opts/@q/@or/@s`) and
  `backend_python/web/data/study/*/*.json` (HTML banks: MCQ + key + reason, Group B/C + model answers).
- First extraction (resources branch only): 22,199 unique raw items (C8/C10/C11/C12/CEE/IOE).

## Dataset (push 2) — built on VM `/tmp/paperlm/gold`, tokenizer `/tmp/paperlm/tok`
- Raw 42,396 unique items from 4 NEB branches -> **18,593 gold** items (11.3k MCQ with keys+reasons, ~7k written w/ marks, OR twins, solutions);
  23.8k rejected by validator (answer-blobs, unmarked, visual-dependent, bad LaTeX, duplicate options, ...). See `dataset/dataset_stats.json`.
- Train 37,067 lines (incl. MCQ option-shuffle aug x2, train only) / val 865 lines, split by SOURCE FILE hash (no leakage). 3.29M train tokens.
- Tokenizer: byte-level BPE vocab 6144 (119 specials), exact LaTeX-aware pre-split regex, 0 round-trip failures, 3.98 chars/token.
- Full dataset (`gold.jsonl`, `train.txt`) is derived from the PRIVATE NEB repo, so it is NOT committed to this public repo; it lives on the VM
  (`/tmp/paperlm/gold`). Only stats + a 40-line validation sample are committed. Rebuild: `data/extract_neb.py` -> `data/build_dataset.py` -> `tokenizer/train_tokenizer.py`.

## Model, training, export (push 3)
- Architecture `model/architecture.py`: Llama/SmolLM-style, RoPE + RMSNorm + SwiGLU, tied embeddings, 6 layers, d=320, 5 heads, ffn 832, vocab 8192, ctx 1024, KV-cache. **9,875,520 parameters**.
- Corpus for LM training: 37k gold exam lines (3.3M tokens) + 18.4k validated textbook chunks (`data/extract_books.py`, ~6M tokens). Val = held-out source files (exam items only).
- Sweep runs e/f/g (lr 1.5-3e-3, dropout 0.1-0.15, 8-10 epochs), best = run f: **val loss 2.0198, perplexity 7.54** (fp32); INT8 weight-only: val 2.0200 / ppl 7.54. Logs in `model/logs/`.
- Weights (`weights/`): fp32 safetensors 39.51 MB, fp16 19.76 MB, int8 safetensors 10.01 MB, **int8 ONNX (KV-cache graph) 10.43 MB**; ONNX-vs-torch max logit diff 1.2e-05.
- Engine: `engine/paper_setter.py` (Python, Torch/ONNX backends), `engine/web/paperlm.js` (onnxruntime-web/node, verified under node on the VM),
  `engine/android/{PaperLm,ConstrainedDecoder}.kt` (ORT Android; NOT compiled in the sandbox - verify in the NEBians module).
- Eval (`eval/evaluate.py`, results in `eval/results/`): constrained engine schema-valid 100.0% of 46 items (unconstrained baseline 89.6%), mean 1.54 attempts, 0.69 s/item on server CPU.
- KNOWN LIMITS (honest): validity (syntax/LaTeX/schema/marks) is guaranteed by constrained decoding + validator; *semantic correctness* (are MCQ keys true, do facts hold) is NOT guaranteed by a 10M model - generated items must be reviewed/verified (e.g. against a verified bank) before being shown as official. Some (board,level,subject,type) cells can dead-end; the engine resamples and raises ItemGenerationError rather than emitting an invalid item. Characters like <=, >= are emitted as LaTeX (\leq) because they are multi-token UTF-8.
- Next: verified-answer layer (numeric solver checks), more training data (more NEB solutions), distillation of rubric style, Android compile + benchmark, JS decoder resample-on-dead-end parity.
