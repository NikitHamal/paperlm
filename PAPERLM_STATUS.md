# PAPERLM_STATUS.md — PaperLM build log (single source of truth, resume from here)

## Infra (MoLab)
- Notebook https://sb-bc79ba58e2c2c51f.sb.molab.run/ (session `sess-qa914tcyg7j8cndd`; token kept in `/tmp/molab_token`, never committed). `pip install marimo` locally, then `scripts/molab_run.sh|molab_put.sh|molab_bg.sh|molab_tail.sh`, big files: `scripts/molab_getbig.py`.
- GPU RTX PRO 6000 Blackwell 96 GB. Keep-alive daemon `/tmp/paperlm/keepalive.py` (60 s ping + CUDA op, heartbeat `/tmp/paperlm/heartbeat.txt`) was verified RUNNING this session (count 157+, local=200 public=200). Restart: `setsid nohup python3 /tmp/paperlm/keepalive.py &`.
- Live dashboard: 9 auto-refreshing (3 s) marimo cards incl. new `system()` card (`molab/dash_system.py`, reads `status_system.json`, `param_test.json`).
- (superseded; pipeline_v5 is NOT running any more, release5 only has bench_v4b.json) `pipeline_v5.sh` (log `/tmp/paperlm/logs/pipeline_v5.log`): copy-bias grounded RFT rounds 1-3 -> bench -> export to `/tmp/paperlm/release5/` (`READY` file when done) -> factual bench. Harvest with `molab_getbig.py /tmp/paperlm/release5/paperlm_tiny_int8.onnx docs/model/model.onnx`, then `node eval/node_e2e.mjs docs/model/model.onnx 60 4`.

## What is live (https://nikithamal.github.io/paperlm/)
Composed system (`docs/composer.js`, twin `engine/composer.py`):
1. **Symbolic parametric engine** (`docs/parametric.js` / `engine/parametric.py`, 139 law templates in `engine/param_templates.json`): numbers, units, key, distractors (typical-mistake expressions, same unit) and worked solution are computed. `eval/param_test.py`: 41,700 instances, 0 self-check failures, 21 hand-computed known values 0 failures, 278 Python<->JS parity cases 0 failures.
2. **Audited gold bank** (`docs/model/bank.json`, `eval/bank_audit.py`): 11,760 seeds (5.0k MCQ, 6.7k written) pass option-homogeneity / key-vs-explanation / LaTeX / arithmetic checks (0 dropped). Written seeds without a model answer are never used.
3. **Neural draft tier (EXPERIMENTAL, OFF by default)**: 10M LM (v4b, concept-conditioned `<|book|>anchor`, copy-bias decoding beta=2.5) behind `ground.js` strict gate.

## Honest findings (read before claiming anything)
- 10M LM val loss: v3 2.24 -> v4b **1.8977** (ppl 6.67); zero-dropout continuation v5a 1.9017 (no gain). `val_loss < 0.50` is NOT reachable on 3.3M tokens of diverse exam text; do not promise it.
- The strict gate is lexical (grounding in the anchor, no invented numbers/symbols). It **passes grammatical nonsense** (e.g. "The programme is a subject. Write a letter to the editor."). So gated neural drafts are NOT verified and are labelled "Neural draft (experimental)". Gate yield: beta=0 1/117 tries, beta=2.5 4/114. VM bench v4b: raw gate pass 4.9%, prompts resolved 14.8% (no bias: 5.3% / 14.1%); copy-bias fixes off-topic (1178->403) and invented numbers (25.8%->19%) but raises repetition.
- Node e2e on 400 random requests (verified-only): 354 ok, 46 explicit "no verified item" errors (written types on MCQ-only boards / thin subjects). 0 neural items. Tiers: bank 187, computed 167.
- Dataset/bank derive from the PRIVATE NEB repo and the bank ships in this PUBLIC repo at the user's request (`docs/model/bank.json`, 5.5 MB). Decide whether to make the repo private or strip seeds.
- NOT done: Android Kotlin twins of composer/parametric/gate (assets `bank.json`, `templates.json` are ready; need a small expression evaluator); an LM that understands meaning (needs a verifier model or far more data); stronger semantic gate (entailment).

## Next
1. Harvest `release5` when `READY`; check `bench_*.json` + `factual_*.json`; ship only if prompts_resolved improves.
2. Add templates for biology/English/social-studies factual items via an audited fact table (cloze MCQs from `bank.facts` with human review).
3. Replace lexical gate with a learned verifier (train a small cross-encoder on gate-accepted vs gold items).
4. Port composer/parametric/ground to Kotlin.

## Files added this session
`data/build_templates2.py` (+52 templates), `data/clean_bank.py`, `eval/bank_audit.py`, `eval/node_e2e.mjs`, `eval/lm_tier_test.mjs`, `eval/param_parity.mjs`, `eval/samples_v5.mjs`, `eval/results/v5/*` (summary, samples_verbatim, e2e, bank_audit), `docs/{composer,ground,parametric}.js`, `scripts/pipeline_v5.sh`, `molab/dash_system.py`.

## v7 session (Qwen2.5-32B on the RTX PRO 6000; honest results)
- Connected to MoLab (token in /tmp/molab_token, not committed). Everything from the previous session was already on GitHub; Pages is live (HTTP 200, legacy build from main:/docs). `pipeline_v5` had died; GPU was idle, keep-alive daemon running (count 230+).
- Downloaded Qwen2.5-32B-Instruct to /dev/shm/qwen32b (bf16, ~65 GB). `eval/judge_bank.py` audited the gold bank: **MCQ blind-solve agreement 4,677/5,011 (93.3%) at p>=0.5, +214 confirmed by CoT; 113 MCQ disagree even after CoT**; written answers: 2,543/4,516 judged correct (p>=0.8), 1,298 with p<0.05. Outputs `eval/results/v7/judge_stage{1,2}.jsonl`, `judge_report.json`, `flagged_*.json`.
- **Key finding: the 32B judge is NOT ground truth.** Spot-checking the 113 flagged MCQs, the bank key was right and the judge wrong in nearly every sample (surface tension [MT-2], ozone/tailing of mercury, haemozoin, 2021 growth 0.92%, PAPER->REPAP reverse code). So flagged items are only a human review queue; nothing was deleted (`data/apply_judge.py`, `DROP=1` would). Bank items carry `j:1` when judge-confirmed.
- `eval/teacher_gen.py`: teacher writes MCQs for thin units, kept only after structural checks + blind re-solve + CoT for numeric items. 248 items kept (79% of structurally valid ones) in a partial run, BUT the first verbatim sample was wrong (petty-cash item: key 'Rs. 50' contradicts its own explanation), proving self-agreement filtering is insufficient. **Teacher items are NOT merged into docs/model/bank.json**; they are stored as candidates in `eval/results/v7/teacher_items.jsonl`. The composer/UI already understand `v:"T32"` items (tier "Teacher-verified") if you merge them later after an independent check (e.g. symbolic arithmetic check of the explanation vs key).
- The generation job keeps running on the VM (`/tmp/paperlm/gen_v7`, status card `status_gen.json`); two new live 3 s cards (judge audit, teacher generation) were added to the notebook (`molab/dash_judge.py`).
- Still true: 10M LM val loss 1.90 (not <0.50), neural tier OFF by default; the live output is symbolic/fact/bank only. Node e2e on 400 random requests: 385 ok / 15 explicit no-verified-item errors (tiers fact 164, param 126, bank 86, reason 8). param_test: 41,700 instances, 0 self-check failures, 21 known values 0 failures, 278 py/js parity 0 failures.
## Next
1. Add a symbolic check (explanation arithmetic vs key) before merging teacher MCQs; 2. review `flagged_mcq.json` (113) manually, 3. fix incomplete stems (e.g. matrix R element r23 missing the matrix), 4. Android Kotlin twin.
