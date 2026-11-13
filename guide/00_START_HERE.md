# PaperLM in plain English (start here)

Read this page first. It is the whole project in about five minutes. The other pages go deeper:

| Page | What it answers |
|---|---|
| `01_THE_MODELS.md` | What exactly are the 10 models, what is inside them, how are they made |
| `02_HOW_A_PAPER_IS_MADE.md` | What happens, step by step, when a student clicks "Generate paper" |
| `03_CODEBASE_MAP.md` | Every folder and important file, in plain words |
| `04_GLOSSARY_AND_QA.md` | Every technical word explained, plus questions people will ask you and good answers |
| `05_REBUILD_AND_STATUS.md` | How the whole thing is rebuilt from scratch, what is finished, what is weak |

## One sentence

PaperLM makes **mock exam papers for Nepal's NEB Class 11 and 12** (Biology, Physics, Chemistry, Maths,
Computer Science). It works **offline in a browser or Android phone**. It uses **small AI models**
and, more importantly, **strict checking code around them** so a student does not get wrong or broken questions.

## The picture in your head

Think of a school with **ten specialist teachers**, not one teacher for everything.

- Each teacher knows **one subject in one class** only (for example "Biology Class 12").
  That is called a **pack**. There are 10 packs: `bio11 bio12 phy11 phy12 chem11 chem12 math11 math12 cs11 cs12`.
- Each teacher has a **brain** (a small neural network, about 10 million numbers, about 10 MB) and a
  **locker of already-checked questions** (the "bank", 1,100 to 1,900 questions per pack, 14,797 in total).
- Around the teachers is a **strict exam office** (the "engine" or "harness"). It plans the paper, makes
  sure every unit of the syllabus is covered, checks every question, does the maths itself for numericals,
  and never lets a broken question reach the student.

## The three ways a question is produced (and the most important honest fact)

1. **Computed** (numericals): a formula template plus random numbers. The answer and the wrong options come
   from code, so they are exactly right. The AI does not touch these. There are 251 formula templates.
2. **Neural** (the 10M model writes it): the model is shown one textbook fact and asked to write a question.
   Every attempt must pass strict gates. Today the small model passes only about **4% to 37%** of the time.
3. **Verified bank** (the locker): questions already written and checked earlier, either from real NEB past
   papers ("gold") or written by a big AI (Qwen2.5-32B, "teacher") and then checked hard.

**Honest truth to know and say:** in practice almost everything a student sees comes from tiers 1 and 3.
The 10M model is real, it works, it is shipped and tested, but it is a *weak writer*. The product's quality
comes from the **verified data + the checking engine**, not from the small model being smart.
Each question on screen is labelled with where it came from, so nothing is hidden.

## What you can say if someone asks "what is this?"

**30 seconds:**
"PaperLM is an offline exam paper generator for Nepal's NEB Class 11 and 12 science and computer subjects.
Instead of one big AI, we train ten small specialist models, one per subject and class, each about 10 MB.
They run on a phone or in a browser with no internet. Around the models we built a checking engine: it computes
numerical answers with exact formulas, checks every question against the textbook fact it came from, and plans the
whole paper so every chapter is covered with no repeats."

**One line on why it is different:**
"We don't trust the AI to be right. We make it impossible for it to be shown wrong, by checking and by computing."

**One line on honesty (say this before they ask):**
"The tiny models are still weak writers on their own; most questions come from a bank checked by a bigger AI plus
real past papers, and every question shows its source."

## Where things live

- Live web app: `docs/` (served by GitHub Pages at https://nikithamal.github.io/paperlm/)
- The 10 models and their data: `docs/packs/<pack_id>/`
- The code that trains them: `packs/tools/`
- The checking engine: `engine/` (Python), `docs/packlm.js` (browser), `engine/android/` (Kotlin)
- Status log (very long, written by earlier AI sessions): `PAPERLM_STATUS.md`
