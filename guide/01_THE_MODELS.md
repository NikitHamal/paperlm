# The models: what they are, what is inside, how they are made

## 1. What is a "model" here?

A language model is a program that **predicts the next small piece of text** (a "token"), again and again.
Chat assistants are huge ones (billions of numbers). Ours are tiny: **10,203,840 numbers ("parameters")** each.
Those numbers are saved in one file, `docs/packs/<pack>/model.onnx` (10.73 MB, compressed to 8-bit numbers = "INT8").
An Android version, `model.tflite`, has the same numbers (12.38 MB).

Learning = adjusting those 10 million numbers until its next-word guesses on exam-style text are good.
That adjustment is called **training**.

## 2. The 10 models (packs)

`bio11 bio12 chem11 chem12 phy11 phy12 math11 math12 cs11 cs12` - all identical in shape, each trained on
**only its own subject and class**. No Class 12 chapter leaks into a Class 11 pack. The reason: a tiny brain
has little room, so spending it all on one subject is better than spreading thin.

Shape of every pack (from `packs/tools/train_pack.py`, class `PaperLMConfig`):

| Setting | Value | Plain meaning |
|---|---|---|
| vocabulary | 4,096 tokens | the model's "dictionary" of text pieces, built only from that subject |
| layers | 7 | 7 stacked processing blocks |
| width (`d_model`) | 320 | each token is a list of 320 numbers |
| heads | 5 | 5 "attention" views per layer (64 numbers each) |
| feed-forward width | 896 | size of the thinking part of each block |
| max length | 768 tokens | about one short question plus its context |

The architecture is the standard modern "Llama-style" transformer (`model/architecture.py`): attention with rotary
position (RoPE), RMSNorm, SwiGLU, tied input/output embeddings. You do not need to explain more than:
"a small Llama-style transformer".

Quick size sanity check you can say: embeddings 4096x320 = 1.3M numbers, each of the 7 blocks about 1.27M, total about 10.2M.

## 3. Each pack comes with more than a brain

`docs/packs/bio12/` contains:

| File | What it is |
|---|---|
| `model.onnx` / `model.tflite` | the 10M-number brain (browser/PC and Android) |
| `tokenizer.json` | the subject's own dictionary (4,096 pieces). "xylem", "phloem" stay whole words |
| `syllabus_graph.json` | the **concept graph**: units (chapters), the verified facts in each, weights, exam share |
| `bank.json` | the verified question locker (the "bank") |
| `numeric_templates.json`, `numeric_bank.json` | which formula templates apply, plus computed numericals |
| `pack.json` | settings the browser/phone needs, including the grammar rules for decoding |

The **syllabus graph** matters: each chapter ("unit") has facts (laws, definitions, formulas), a weight, and a
`share` (its proportion of the syllabus). Example: Biology 12 "Plant Anatomy" has 28 facts and share 0.0776.
It is built **only** from content tagged with that class and subject (`packs/tools/build_pack.py`).

## 4. How a pack is made (the recipe, in order)

1. **Collect real material.** Real NEB past papers and textbook chapters come from the repo `NikitHamal/NEB`
   (`data/extract_neb.py`, `data/extract_books.py`). A strict checker (`data/validator.py`) throws out messy items.
   Items that survive are "gold".
2. **Build the pack's graph and prompts.** `packs/tools/build_pack.py` keeps only this class + subject, builds
   the syllabus graph, a list of "anchors" (one textbook fact each), and the textbook text for language learning.
3. **A big AI teacher writes more questions.** `packs/tools/teacher.py` runs Qwen2.5-32B (a 32-billion-number
   model on a rented GPU) on each anchor. A draft is **kept only if** it passes all checks:
   - structure is correct,
   - the teacher solves it blind, with shuffled option orders, and gets the same key (score >= 0.6),
   - the textbook passage really supports the answer ("entailment", score >= 0.85),
   - no wrong option looks right (distractor probe, max <= 0.25).
   Passing items go to the bank and to training data. Failed drafts are not used for the bank.
4. **Clean the bank.** `packs/tools/bank_qa.py` removes items that mash two topics, mention "option (b)" in the
   explanation, refer to "the given reaction" with nothing given, or leak passage wording.
5. **Train the tiny model** (`packs/tools/train_pack.py`):
   - **Own tokenizer** (4,096 pieces) trained on this pack's text only.
   - **Answer-first, concept-conditioned format.** Input is: pack id, question type, marks, unit, **the textbook fact**.
     Output order is: **answer first**, then question, then three wrong options, then the reason, then end.
     Writing the answer first means the question must be consistent with a known answer.
   - **Stage A** (script default 2,500 steps; wave 9 used 1,400): learn the textbook language and items together.
   - **Stage B** (default 3,500; wave 9 used 500): practise only on verified items.
   - **Contrastive tuning ("DPO")** (default 400; wave 9 used 250): show the model good items against deliberately spoiled ones
     (key duplicated in the options, wrong key, off-topic question) and push it toward the good ones.
   - 6% of anchors are hidden as a test set (chosen by a hash). We report the loss on those unseen anchors.
   - The best checkpoint on unseen anchors is kept, not the last one (stops it from just memorising).
6. **Export and publish.** `model/export.py` and `packs/tools/export_tflite.py` shrink to INT8; `packs/tools/publish.py`
   copies everything to `docs/packs/<pack>/` and refuses a retrained model that is more than 2% worse than the shipped one.

## 5. How good are they, honestly

From `eval/results/packs/summary.md` (held-out loss on unseen anchors; lower is better; "ppl" is the same idea, easier to read):

| Pack | loss (ppl) | Pack | loss (ppl) |
|---|---|---|---|
| math11 | 1.87 (6.5) | chem12 | 2.99 (19.9) |
| math12 | 1.91 (6.7) | bio11 | 3.49 (32.8) |
| phy11 | 2.09 (8.1) | bio12 | 3.51 (33.4) |
| phy12 | 2.19 (8.9) | cs11 | 3.57 (35.4) |
| chem11 | 2.82 (16.7) | cs12 | 3.83 (46.2) |

Math and physics are more regular so the model predicts them better. Biology and CS are wordier, so worse.
On a 24-fact benchmark the "strict gate" accepted the model's own question only 4% to 37% of the time.
**The model never gets to show a question that fails the gate.** If it fails, the bank is used.

## 6. The older single model (legacy)

`docs/model/` and `weights/` hold the first version: ONE 9.9M model for all subjects (6,144 tokens, 6 layers).
It is kept in `docs/legacy.html` as a playground. It is superseded by the 10 specialist packs.
