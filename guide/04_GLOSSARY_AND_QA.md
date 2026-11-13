# Glossary and "what do I say when..." answers

## Glossary (plain words)

| Word | Meaning |
|---|---|
| **Model** | A file of numbers that predicts the next piece of text. |
| **Parameters** | The numbers inside the model. Ours: about 10 million. ChatGPT-class: hundreds of billions. |
| **Transformer** | The standard design of modern language models. Ours is a small Llama-style one. |
| **Token** | A piece of text (a word or part of a word). The model reads and writes tokens. |
| **Tokenizer / BPE** | The dictionary that splits text into tokens. Each pack has its own 4,096-token one built from its subject. |
| **Training** | Adjusting the numbers by showing examples many times. |
| **Loss / perplexity (ppl)** | How surprised the model is by unseen text. Lower is better. Ours: loss 1.9 to 3.8 (ppl 6.5 to 46). |
| **Held-out / validation** | Test data the model never trained on (we hide 6% of facts). Honest quality measure. |
| **SFT** | Supervised fine-tuning: learn from correct examples. |
| **DPO / contrastive tuning** | Learn from pairs: good item vs spoiled item, prefer the good. |
| **Distillation / teacher** | A big AI (Qwen2.5-32B) writes data; the small AI learns from it. |
| **Anchor / fact** | One short verified textbook statement a question must be based on. |
| **Concept graph (`syllabus_graph.json`)** | Units, their facts, weights and syllabus shares. |
| **Answer-first** | The model writes the answer before the question, so the question must fit that answer. |
| **Conditioning** | Giving the model the textbook fact in the prompt. |
| **FSM / grammar-constrained decoding** | A state machine that blocks illegal next tokens, so structure can't break. |
| **Logit masking** | The mechanism: illegal tokens get score minus infinity. |
| **Best-of-K / reranking** | Make K candidates, score them, keep the best. K = 3 here. |
| **Entailment** | "Does the passage actually say this?" A check that a claim is supported. |
| **Distractor** | A wrong option in an MCQ. Good ones are plausible. |
| **Grounding gate / strict gate** | The set of checks a neural question must pass. |
| **Hallucination** | AI confidently writing something false. The gates exist to stop it. |
| **Pack** | One specialist: model + tokenizer + graph + bank for one class and subject. |
| **Bank** | The locker of verified questions in a pack. |
| **Gold** | Real NEB past-paper style items. **Teacher** items: AI-written then verified. |
| **Harness / engine** | All the code around the model: plan, solve, check. |
| **Neuro-symbolic** | Neural network (fuzzy, learned) plus exact code rules. That is our design. |
| **INT8 quantisation** | Storing each number in 8 bits instead of 32, making the file about 4x smaller with little loss. |
| **ONNX / TFLite** | File formats to run a model: ONNX in the browser/PC, TFLite on Android. |
| **KV cache** | Remembering earlier computation so each new token is fast. |
| **Lazy loading** | Download only the pack you use. |
| **MoLab** | The rented GPU computer used for the heavy jobs. |
| **Wave** | One scripted full re-run (data, teacher, train, publish). We are at wave 9; wave 10 was planned. |

## Questions people will ask, and good answers

**Is this ChatGPT? Does it call an API?**
No. It runs entirely on the device. After the first download of a pack it works with no internet. No API, no cloud cost.

**How big are the models and how many are there?**
Ten, each 10.2 million numbers, 10.7 MB. A user downloads only one at a time.

**Why ten small ones and not one big one?**
A tiny brain has limited room. Dedicating each to one subject and class keeps terms like "xylem" or LaTeX whole,
avoids mixing Class 11 and 12 content, and lets us ship a 10 MB download.

**Did you train the models yourself?**
Yes. Each is trained from scratch (not a copy of someone else's model) on our own data, with our own tokenizer.
The big teacher (Qwen2.5-32B, open source) is used only to write practice questions that are then verified.

**Where does the data come from?**
Real NEB past papers and textbooks collected in the `NikitHamal/NEB` repo (gold items), plus teacher-written items that passed verification.

**How do you know the answers are right?**
Three ways: (1) numericals are computed by formula, (2) neural questions must pass the grounding gate against a textbook fact,
(3) bank questions were solved blind by a big AI, checked against the passage, and each wrong option was tested to be wrong.
Then a cleaning pass removed sloppy items.

**Can it hallucinate?**
The small model alone could. The engine blocks that: structure is forced by the grammar, numbers must come from the fact, and
if checks fail the question is replaced from the bank. We show the source on every question.

**Then is the AI actually writing the questions?**
Honestly: rarely. The small model passes our strict checks only 4% to 37% of the time, so most questions come from the verified bank
and the formula engine. The small models are working and shipped, but improving them needs more verified training data.
(Say this before someone finds it. It builds trust.)

**What makes the exam papers good as papers?**
The planner: questions per chapter match the syllabus share, no repeated concept, written answers have a marking scheme with marks adding up.

**Does it work on phones?**
The web app works in a mobile browser. The Android code exists in Kotlin (`engine/android/`) with TFLite models checked against ONNX in Python
(top-1 agreement 0.93 to 1.00), but the Kotlin app has **not been compiled yet** (no Android toolchain was available).

**Does it support Nepali?**
The checks allow Devanagari characters, but the shipped packs are English NEB content.

**What is not done?**
Wave 10 (more teacher data, retrain) never ran because the GPU VM was shut down by the platform. A better neural writer needs that data.
Android app is not compiled. Other levels (Class 8, SEE, IOE, CEE, BCA, nursing) appear in the legacy data but have no packs.

**What would you do next?**
(1) More verified data and an "edit" task (model rewrites a verified item into a new wording, harness verifies it).
(2) Compile and test the Android app. (3) Add more subjects and classes as packs.

## Do not say

- "The AI writes all the questions." (Not true today.)
- "It is always correct." Say "every question is checked and shows its source".
- "It is as good as GPT." It is a tiny specialist, not a general chatbot.
