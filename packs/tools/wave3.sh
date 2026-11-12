#!/bin/bash
# wave 3 (budget-aware, MoLab VM, strictly sequential on the GPU): chem teacher -> train ALL packs in parallel (val-best) -> TFLite -> publish -> push
cd /work/paperlm; L=/tmp/paperlm/logs; SA=${SA:-1400}; SB=${SB:-600}; SD=${SD:-300}; ALL="bio12 phy11 bio11 phy12 chem11 chem12"
rm -f /tmp/paperlm/WAVE3_DONE /tmp/paperlm/TRAINED_*
[ -z "$SKIPT" ] && PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OFF=0 MAXA=${CMAXA:-380} NSHORT=${CNSHORT:-130} SUF= python3 packs/tools/teacher.py chem11 chem12 > $L/teacher_chem.log 2>&1
for p in $ALL; do ( python3 packs/tools/train_pack.py $p $SA $SB $SD > $L/train_$p.log 2>&1; cd /tmp && python3 /work/paperlm/packs/tools/export_tflite.py $p > $L/tflite_$p.log 2>&1; touch /tmp/paperlm/TRAINED_$p ) & done
wait
python3 packs/tools/publish.py $ALL > $L/publish.log 2>&1
git add -A; git commit -qm "packs wave3: 6 specialist packs, verified bank, val-best training, TFLite (MoLab GPU)"; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:main
touch /tmp/paperlm/WAVE3_DONE
