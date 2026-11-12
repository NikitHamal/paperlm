# Validation run v16 (shipped packs, before wave8r lands) - deterministic, no browser

- Python onnxruntime (`eval/ort_pack_check.py 3 2`): 10/10 packs (bio12 phy11 bio11 phy12 chem11 chem12 math11 math12 cs11 cs12) load INT8 ONNX (10,203,840 params, 10.73 MB each) and decode under the FSM; 0 empty slots; neural strict gate accepted 1 of 30 slots (phy11), the other 29 served by the verified bank.
- Node onnxruntime-node (`eval/node_pack_bench.mjs 4 2 phy11 bio12`): both packs load via `docs/packlm.js`, 6 slots each, 0 empty, 0 duplicates, neural accepted 0/12 attempts on bio12 (bank 801 = 570 MCQ + 231 short).
- Planner (`eval/pack_paper_test.py`): 360 papers, 9,360 slots, TOTAL violations 0 (dup_q, dup_anchor, near_dup, key_missing, scheme_bad all 0); unit_cov_mean 0.79 (phy11) to 1.00 (bio12).
- Honest position: the 10M LMs are weak free writers; everything a student sees is verified-bank or computed, each item carries a provenance tag.
- Teacher sanitiser (v16) measured on math11 first chunk of 384 prompts: 327 structurally valid drafts (85 %), versus 428 of 900 (47.6 %) for chem12 under the old reject-on-phrase rule. Verification gates unchanged.
