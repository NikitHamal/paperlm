#!/bin/bash
# stage-2 teacher scale-up: next anchors (OFF) -> verified2.jsonl per pack, then retrain
cd /work/paperlm; P="${PACKS:-bio12 phy11 bio11 phy12}"
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OFF=${OFF:-600} MAXA=${MAXA:-1500} NSHORT=${NSHORT:-450} SUF=2 python3 packs/tools/teacher.py $P > /tmp/paperlm/logs/teacher_scale.log 2>&1
touch /tmp/paperlm/TEACHER2_DONE
