# PaperLM subject packs on Android (TFLite / LiteRT or ONNX Runtime Mobile)

Every pack lives in `docs/packs/<pack_id>/` and is the same bundle used by the web playground:

| file | purpose |
|---|---|
| `model.tflite` | ~10M-param specialist, INT8 dynamic-range weights, signatures `decode` (S=1) and `prefill` (S=64), KV cache `[L,1,H,P,Dh]` |
| `model.onnx` | same weights, INT8 KV-cache graph (ONNX Runtime Mobile alternative) |
| `tokenizer.json` | subject-pure byte-level BPE (4096) - port `PaperTokenizer` in `PaperLm.kt` |
| `pack.json` | layer/head/head_dim/max_seq, special-token ids, FSM spec (segment order, min/max lengths) |
| `syllabus_graph.json` | units, facts (concept anchors), exam weightings, unit vocabulary |
| `bank.json` | verified items (gold NEB + teacher items that passed blind multi-order solve, entailment and per-distractor probes) |
| `numeric_templates.json` | ids of the parametric numerical templates this pack may use (`engine/android/assets/templates.json`) |

Runtime contract (identical in `docs/packlm.js` and `packs/tools/fsm.py`):
1. prompt = `<|bos|><|pack=ID|><|type=K|><|marks=M|><|unit|>NAME<|book|>ANCHOR<|ans|>`; the model writes the **answer first**, then `<|q|>`, options `<|d|>`, `<|why|>`, `<|end|>`.
2. Constrained decoding: only the legal next tag and balanced `{}`/`$` are unmasked at each step (`ConstrainedDecoder.kt`).
3. Copy-bias (`beta`) toward anchor tokens, best-of-K, lexical grounding gate, strict gate v3 (`strictOK` in JS), then fallback to `bank.json`.
4. `TflitePackRunner.kt` implements `feed(ids) -> logits(last)`; plug it in place of the ORT session. Python reference for parity: `packs/tools/export_tflite.py` (`tflite_report.json` per pack).

## Kotlin integration map (all files in `ai.paperlm`)
| file | role |
|---|---|
| `PaperTokenizer` (`PaperLm.kt`) | byte-level BPE encode, loads the pack's own `tokenizer.json` |
| `TflitePackRunner.kt` | `feed(ids) -> logits` over `model.tflite` (`prefill`/`decode` signatures) |
| `PackEngine.kt` | `PackMeta`, `TokTable`, `Fsm` (grammar-constrained decoding), `PackGate` (grounding gate + strict gate v3), `PackEngine.sample/best` (best-of-K with copy-bias + rerank) - 1:1 twin of `docs/packlm.js` |
| `assets/templates.json` + `numeric_templates.json` | deterministic parametric numerical solver (ids allowed per pack) |
| `bank.json` | verified fallback tier; the product never shows an item that failed both the neural gates and the bank |

Minimal wiring:
```kotlin
val meta = PackMeta(JSONObject(File(dir, "pack.json").readText()))
val tokJson = JSONObject(File(dir, "tokenizer.json").readText())
val runner = TflitePackRunner(File(dir, "model.tflite"), meta.layers, meta.heads, meta.headDim, meta.maxSeq, meta.vocab)
val engine = PackEngine(meta, PaperTokenizer(tokJson.toString()), TokTable(tokJson, meta.vocab), runner::feed, runner::reset)
val cands = engine.sample(unit.name, "mcq", 1, fact.text, k = 3)
val item = engine.best(cands, "mcq", fact.text, unit.terms.toSet())   // null -> take bank.json item
```
`PackEngine.kt` has not been compiled in CI (no Android toolchain on the training VM); the TFLite graph it drives has been executed and parity-checked in Python (`tflite_report.json`).
