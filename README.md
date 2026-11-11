# PaperLM

**PaperLM-Tiny** — a ~10M-parameter on-device "Board Setter Brain" for Nepali exam preparation
(Class 8 BLE, Class 10 SEE, Class 11/12 NEB, IOE, CEE, BCA, BSc Nursing, BE).
Generates mock tests, model papers, OR-twin questions, MCQs with distractors and marking rubrics, fully offline.

See `PAPERLM_STATUS.md` for the live build status. Layout: `data/` (extraction, validation, dataset), `tokenizer/`,
`model/` (architecture, training, export), `engine/` (constrained PaperSetterEngine + web/Android SDK), `eval/`, `molab/` (GPU VM dashboard + keep-alive).
