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
| 3 | PaperLM-Tiny 10M arch, GPU training, constrained PaperSetterEngine, INT8/FP16/ONNX export, web+Android SDK, eval | pending |

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
