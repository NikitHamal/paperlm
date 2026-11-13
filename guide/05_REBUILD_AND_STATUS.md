# Rebuild recipe and honest status

## The whole system as one flow

```
NEB past papers + textbooks (repo NikitHamal/NEB)
        |  data/extract_*.py + data/validator.py
        v
 GOLD items (2,703 across the 10 packs)          textbook facts per class+subject
        |                                                 |
        |        packs/tools/build_pack.py  ---> syllabus_graph.json + anchors + book text
        |                                                 |
        |                        packs/tools/teacher.py (Qwen2.5-32B on a GPU)
        |                         write -> blind solve -> entailment -> distractor probe
        v                                                 v
        +--------------> VERIFIED items (12,094 teacher) <+
                               |  packs/tools/bank_qa.py (clean)
                               v
                 bank.json (14,797 items total)  +  training data
                               |  packs/tools/train_pack.py
                               |  tokenizer -> stage A -> stage B -> DPO -> bench -> INT8 ONNX
                               |  packs/tools/export_tflite.py
                               v
                  packs/tools/publish.py ---> docs/packs/<id>/  ---> GitHub Pages / Android assets
                                                      |
                              runtime: planner -> computed | neural+gates | bank  -> paper
```

## Commands (for the person who rebuilds)

Heavy steps need an NVIDIA GPU (the project used a rented MoLab VM). From a fresh VM:

1. `bash scripts/vm_bootstrap.sh` - clone this repo to `/work/paperlm` and the NEB repo to `/tmp/neb_src`. Needs a GitHub token via `/tmp/gitenv.sh` (never commit a token).
2. `bash scripts/vm_hydrate.sh` - build the gold set and per-pack anchors under `/tmp/gold` and `/tmp/packs/<id>/`.
3. Download Qwen2.5-32B-Instruct to `/dev/shm/qwen32b`.
4. `bash packs/tools/build_all.sh` - per-pack graphs/anchors.
5. `python3 packs/tools/teacher.py <packs>` - create and verify questions.
6. `python3 packs/tools/train_pack.py <pack> [stepsA stepsB stepsDPO]` - train one pack.
7. `python3 packs/tools/export_tflite.py <pack>` then `python3 packs/tools/publish.py <packs>` - publish.
8. `packs/tools/wave9.sh` (or `wave10.sh`) chains steps 5 to 7 for all ten packs and pushes.

On a normal laptop (CPU only), the shipped models can be tested without a GPU:
`bash eval/validate_all.sh` (loads every pack in ONNX Runtime, decodes under the grammar, plans papers, checks counts).
The browser app needs no build: open `docs/index.html` through any static server.

## Status (as of the last log entry, v21)

Done and working:
- 10 specialist packs shipped: each 10,203,840 params, INT8 ONNX 10.73 MB, TFLite INT8 12.38 MB.
- Subject-pure tokenizers (4,096), syllabus graphs, answer-first training, contrastive tuning.
- FSM grammar-constrained decoding in Python, JS and Kotlin.
- 251 deterministic formula templates; Python and JS agree.
- Paper planner with syllabus quotas, anti-duplication and marking schemes. Tested: 0 violations, 0 empty slots, 0 duplicates.
- Verified bank of 14,797 items (2,703 gold, 12,094 teacher), cleaned by bank QA.
- Lazy pack loading and browser caching in the web app; copy-as-text and print/PDF export.
- Web app live on GitHub Pages.

Weak or unfinished (be honest about these):
- The 10M models are weak writers: strict gate passes 4% to 37%; held-out ppl 6.5 to 46. Most shown questions are bank or computed.
- Wave 10 (more verified teacher items, then retrain) did not run: the GPU VM was terminated by the platform (HTTP 410) in v20 and v21.
- Android Kotlin code has never been compiled (no Android toolchain on the VM). The TFLite models were verified in Python.
- Best-of-K "entailment reranker" in the browser uses lexical grounding scores, not a learned entailment model. The big-AI entailment check is used offline when building the bank.
- Only 10 packs (Class 11 and 12 Biology, Physics, Chemistry, Maths, Computer Science). Other exams are legacy-only.
- Optional lever to improve the model: an "edit" task where the model rewrites a verified item, which the harness then verifies.

## Security note

A GitHub personal access token was pasted into chat prompts. Treat it as exposed: revoke it at GitHub (Settings, Developer settings,
Personal access tokens) and make a new one. The bootstrap only writes it to `/tmp/gitenv.sh`, which is not tracked by git.
A new MoLab token or URL was not included in the latest request, so no GPU VM was connected in this session.
