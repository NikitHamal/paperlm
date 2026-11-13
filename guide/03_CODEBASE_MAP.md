# Codebase map (every folder, in plain words)

Top level of `NikitHamal/paperlm`:

```
README.md            short intro
PAPERLM_STATUS.md    very long build diary by earlier sessions (newest on top)
guide/               THIS guide
data/                turn raw NEB material into clean training data
dataset/             stats about the first (legacy) dataset
tokenizer/           the legacy single tokenizer (the packs make their own)
model/               architecture + generic training/export code
packs/               the 10 specialist packs: specs, tools, reports
engine/              the checking/planning engine (Python) + Android (Kotlin) + web twin
eval/                tests, benchmarks, audits, results
docs/                the live website (GitHub Pages) and the shipped pack files
molab/ scripts/      rented-GPU (MoLab) helpers and pipeline scripts
weights/ docs/model/ the legacy single 9.9M model
```

## `data/` - make clean data

| File | Job |
|---|---|
| `extract_neb.py`, `extract_books.py` | read past papers and textbooks from the `NikitHamal/NEB` repo (all branches) into JSONL |
| `validator.py` | **the single rulebook for "no mess"**: allowed characters, balanced maths, valid options. Used for data, engine and ports |
| `build_dataset.py`, `build_v2.py`, `build_v4.py` | assemble the gold set and the legacy training set |
| `build_facts.py`, `facts_a..e.py`, `fact_units.py`, `fact_classes.py` | hand-checked fact lists (laws, formulas, definitions) by unit |
| `build_syllabus.py` | list of units per class+subject (names only) |
| `build_templates*.py` | build the formula templates |
| `clean_bank.py`, `filter_bank.py`, `coherence_gate.py`, `apply_judge.py` | remove bad items |
| `merge_teacher.py`, `merge_cross.py` | merge teacher-written items in |

## `model/` - the neural network code

| File | Job |
|---|---|
| `architecture.py` | the transformer itself (`PaperLM`, about 70 lines) |
| `train.py`, `train_v2.py` | legacy single-model training |
| `rft.py` | rejection-sampling fine-tuning: keep only good self-generated items and train on them |
| `verifier.py` | a small learned checker (legacy) |
| `sampling.py`, `export.py` | decoding helpers; export to ONNX / INT8 / safetensors |

## `packs/` - the 10 specialists

| Path | Job |
|---|---|
| `pack_specs.json` | for each pack: class, subject, title, which numerical templates it may use |
| `pack_registry.json` | the list of packs with size and quality numbers |
| `<pack_id>/` | reports only: `train_report.json`, `bank_qa_report.json`, `samples.json`, `syllabus_graph.json` |
| `tools/build_pack.py` | build a pack's syllabus graph, anchors, training text (class+subject only) |
| `tools/teacher.py` | the big AI (Qwen2.5-32B) writes + verifies questions |
| `tools/train_pack.py` | tokenizer, Stage A, Stage B, DPO, benchmark, ONNX export |
| `tools/fsm.py` | grammar-constrained decoding + grounding score (Python) |
| `tools/bank_qa.py` | final cleaning of the bank |
| `tools/publish.py` | copy the trained pack into `docs/packs/`, regression guard |
| `tools/export_tflite.py` | make the Android file and check it matches the ONNX |
| `tools/add_*_templates.py`, `assign_templates.py`, `build_numeric_bank.py` | add formula templates and computed numericals per pack |
| `tools/wave3..wave10.sh`, `chain.sh`, `scale.sh`, `build_all.sh` | "waves": scripted full re-runs on the GPU VM (data, teacher, train, publish) |

## `engine/` - the harness

| File | Job |
|---|---|
| `pack_paper.py` | paper planner (quotas, anti-duplication, marking scheme) |
| `parametric.py` + `param_templates.json` | formula solver + 251 templates |
| `reasoning.py` | number/letter series generator |
| `ground.py`, `verify.py` | grounding gate and symbol/option/key checks |
| `composer.py` | legacy tier chain: parametric, then LM, then bank |
| `paper_setter.py` | legacy engine with Torch/ONNX backends and constrained decoding |
| `factbank.py`, `concept_bank.py` | fact stores |
| `web/` | JavaScript twins (`paperlm.js`, `verify.js`, `known_cmds.js`) |
| `android/` | Kotlin: `PackRegistry`, `PackEngine`, `ConstrainedDecoder`, `PackPaper`, `TflitePackRunner`, `Verify`, plus `PACKS.md` |

Rule of the project: **every rule exists in Python, JavaScript and Kotlin, and tests check they agree.**

## `docs/` - the website

| File | Job |
|---|---|
| `index.html`, `packs-app.js`, `packs.css` | the pack app (the main page) |
| `packlm.js` | pack loader, tokenizer, FSM, sampler, gate, planner |
| `parametric.js`, `reasoning.js`, `ground.js`, `verify.js`, `composer.js`, `factbank.js` | JS twins of the engine |
| `packs/<id>/` | what is downloaded for a pack (about 24 MB per pack with both model formats) |
| `legacy.html`, `app.js`, `paperlm.js`, `model/` | old all-subjects playground |
| `vendor/katex` | maths typesetting |

## `eval/` - proof it works

`validate_all.sh` runs the main checks. `ort_pack_check.py` loads each ONNX model and decodes under the FSM.
`node_pack_bench.mjs` does the same in Node. `pack_paper_test.py` checks planner rules (0 duplicates, keys present,
marks add up). `pack_numeric_test.py`, `param_test.py`, `param_parity.mjs` check numericals and Python-vs-JS equality.
`purity_audit.py` checks no cross-class/subject leaks. `bank_audit.py`, `audit_items.py`, `judge_bank.py` audit quality.
`pack_summary.py` writes `results/packs/summary.md`; `verbatim_report.py` writes sample papers.

## `molab/` and `scripts/`

MoLab is a rented GPU computer (a "VM") controlled from a notebook (marimo). `molab/*.py` are dashboard cards and a
keep-alive. `scripts/molab_*.sh` run/put/get files on it; `vm_bootstrap.sh` and `vm_hydrate.sh` set up a fresh VM
(clone this repo, clone the NEB data repo, build the corpus). `pipeline_v3..v9.sh` are older end-to-end runs.
GPU work (teacher, training) happens there because it is too slow on a laptop. Everything shipped is plain files in this repo.
