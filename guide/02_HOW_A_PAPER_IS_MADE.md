# How a paper is made (runtime, step by step)

This is what happens on a student's phone or browser. Code twins: `docs/packlm.js` (web),
`engine/android/*.kt` (Android), `engine/*.py` and `packs/tools/fsm.py` (Python, used for testing).
The web screen is `docs/index.html` + `docs/packs-app.js`.

## Step 0 - The student picks a pack (lazy loading)

The page shows 10 chips from `docs/packs/pack_registry.json`. **Only the chosen pack is downloaded**
(`Pack.load` in `docs/packlm.js`): tokenizer, syllabus graph, bank, then the 10 MB `model.onnx`.
It is stored in the browser's cache, so next time it is instant and works offline. Picking another pack
frees the first one. The model runs with ONNX Runtime Web (WebAssembly) on the device. On Android,
`PackRegistry.kt` does the same and runs `model.tflite`.

## Step 1 - The blueprint planner builds the paper skeleton

`planPaper` (JS) / `engine/pack_paper.py` (Python):

1. The user says how many MCQs and written questions they want.
2. Each chapter (unit) gets a share of the questions **in proportion to its syllabus share**
   (largest-remainder rounding, so totals are exact). Big chapters get more questions.
3. Slots are shuffled, then each slot gets one **fact** from its chapter that has not been used yet.
4. **Anti-duplication tracker:** no repeated question, no repeated fact, and no near-duplicate
   (words overlap, "Jaccard" >= 0.6, counts as a duplicate).

Result: full syllabus coverage, no repeats, before any text is written.

## Step 2 - Fill every slot (three tiers, in this order)

```
slot (unit + fact + type + marks)
  |
  +--> numerical slot?  --> TIER 1  Computed: formula template + random numbers (code, 100% exact)
  |
  +--> TIER 2  Neural: the 10M model writes from the fact, under strict rules
  |        pass all gates?  yes --> use it
  |                         no  --> next tier
  +--> TIER 3  Verified bank: a pre-checked question for that unit (gold NEB or teacher-verified)
```

The UI source selector has three modes: "Neural + verifier, bank fallback" (hybrid, default), "Verified bank only",
and "Neural only (strict gate)". A circuit breaker stops neural attempts after 6 straight rejections in a
paper to save phone battery, and the bank serves the rest. Every question shows a tag naming its source.

### Tier 1 - Deterministic numerical solver (`engine/parametric.py`, `docs/parametric.js`)

There are 251 formula templates in `engine/param_templates.json`. Example (physics): "A car with initial
velocity u accelerates at a for time t. Find final velocity." with formula `u+a*t`.
- Random values come from allowed ranges, so each paper has fresh numbers.
- The answer is **evaluated by code**, not written by AI.
- The three wrong options come from **typical mistakes** of the same formula (`u+a`, `a*t`, `(u+a*t)/2`),
  so all four options have the same unit and the key is correct by construction.
- The worked solution comes from the template, with the numbers filled in.
- The Python and JS versions are tested to give identical results (`eval/param_parity.mjs`).
Each pack lists the templates allowed for it (for example bio12 has 19, phy11 has 36), so a Class 11
pack never gets a Class 12 template. Maths and reasoning series (`engine/reasoning.py`) work the same way.

### Tier 2 - The neural writer, boxed in by the harness

1. **Prompt.** `<|bos|><|pack=bio12|><|type=mcq|><|marks=1|><|unit|>Genetics<|book|>[the textbook fact]<|ans|>`
2. **Answer first.** The model writes the correct answer, then `<|q|>` question, `<|d|>` three wrong options,
   `<|why|>` explanation, `<|end|>`.
3. **Grammar-constrained decoding (the "FSM").** At every token, illegal tokens are blocked ("logit masking").
   So tags come in the right order, an MCQ has exactly 3 wrong options, `$...$` maths and `{...}` brackets
   always close, only allowed characters appear, length limits hold, and 4-token loops are cut.
   Broken structure is impossible, not just unlikely (`packs/tools/fsm.py`, `FSM` class in `docs/packlm.js`).
4. **Copy-bias.** A small push toward words that appear in the textbook fact, so it sticks to it.
5. **Best-of-K.** It writes K = 3 candidates, scores each for grounding, and keeps the best.
6. **Strict gate** (`engine/ground.py`, `grounding` and `strictOK` in JS). The candidate is accepted only if:
   - every number in the answer/explanation appears in the fact or the question (no invented figures),
   - the explanation uses the fact's words (precision and recall),
   - the question is on topic,
   - the key option is supported by the fact and **no wrong option is also supported** (no two right answers),
   - options are distinct and look alike (same kind of thing),
   - a word-level lexicon check and a minimum model confidence are met.
7. Only now are the options shuffled, with the key letter set by code (`NOSHUF` keeps "all of the above" style options in place).

If anything fails, the slot falls to Tier 3. The engine never displays unverified text.

### Tier 3 - The verified bank

`bank.json` items already passed the teacher verification and the bank QA (see `01_THE_MODELS.md`, step 3 and 4).
A random unused item of the right unit and type is picked, options are shuffled, and the key is recomputed.

## Step 3 - Marking scheme for written answers

Written (short/long) answers get a marking scheme: the model answer is split into steps and the marks are
spread across steps, adding up exactly to the question's marks (`scheme` in `engine/pack_paper.py`).

## Step 4 - Output

The paper is shown with maths typeset (KaTeX), answers hidden until the student asks, and can be copied as
text or printed/saved as PDF (the print style hides controls). The UI follows the M3 design rules:
no shadows, no emojis, no gradients.

## Why this design (the idea in one paragraph)

A 10M model cannot be trusted on its own. So we split the job: **code does everything that must be exact**
(plan, numbers, structure, grounding checks), **the model does only the fuzzy part** (phrasing from a given
fact), and **a verified bank is the safety net**. The model is "boxed in" so the worst case is that the bank is used.
