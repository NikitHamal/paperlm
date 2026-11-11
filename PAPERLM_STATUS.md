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
| 2 | Gold dataset builder + validator + exam-math BPE tokenizer + stats | pending |
| 3 | PaperLM-Tiny 10M arch, GPU training, constrained PaperSetterEngine, INT8/FP16/ONNX export, web+Android SDK, eval | pending |

## Corpus findings
- NEB branches that exist: main, resources/past-papers-class12, claude/engineering, claude/bsc-nursing
  (`claude/bca-entrance-complete`, `polish/school-books-claude` do not exist on the remote).
- Sources: `notes/papers/**/content/*.md` (past papers DSL `@mcq/@opts/@q/@or/@s`) and
  `backend_python/web/data/study/*/*.json` (HTML banks: MCQ + key + reason, Group B/C + model answers).
- First extraction (resources branch only): 22,199 unique raw items (C8/C10/C11/C12/CEE/IOE).
