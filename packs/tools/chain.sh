#!/bin/bash
# teacher distillation -> parallel specialist training -> publish -> git push (all on the MoLab VM)
cd /work/paperlm; P="${PACKS:-bio12 phy11 bio11 phy12}"
MAXA=${MAXA:-600} NSHORT=${NSHORT:-220} python3 packs/tools/teacher.py $P > /tmp/paperlm/logs/teacher_chain.log 2>&1
for p in $P; do python3 packs/tools/train_pack.py $p 2200 3000 300 > /tmp/paperlm/logs/train_$p.log 2>&1 & done; wait
python3 packs/tools/publish.py $P
git add -A; git commit -qm "specialist packs: $P (trained on MoLab GPU)"; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:main; touch /tmp/paperlm/CHAIN_DONE
