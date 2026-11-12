#!/bin/bash
# wave 4 (MoLab VM, sequential GPU): teacher scale-up (verified + raw drafts) for ALL packs -> train all in parallel -> TFLite -> publish -> bench -> push
cd /work/paperlm; L=/tmp/paperlm/logs; SA=${SA:-1500}; SB=${SB:-500}; SD=${SD:-250}; ALL="bio12 phy11 bio11 phy12 chem11 chem12"
rm -f /tmp/paperlm/WAVE4_DONE /tmp/paperlm/TRAINED_*
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
[ -z "$SKIPT" ] && { OFF=600 MAXA=${MAXA:-520} NSHORT=${NSHORT:-160} SUF=3 python3 packs/tools/teacher.py bio12 phy11 bio11 phy12 > $L/teacher4a.log 2>&1
  OFF=0 MAXA=${MAXA:-520} NSHORT=${NSHORT:-160} SUF=3 python3 packs/tools/teacher.py chem11 chem12 > $L/teacher4b.log 2>&1; }
touch /tmp/paperlm/TEACHER4_DONE
for p in $ALL; do ( python3 packs/tools/train_pack.py $p $SA $SB $SD > $L/train_$p.log 2>&1; cd /tmp && python3 /work/paperlm/packs/tools/export_tflite.py $p > $L/tflite_$p.log 2>&1; touch /tmp/paperlm/TRAINED_$p ) & done
wait
python3 packs/tools/publish.py $ALL > $L/publish.log 2>&1
git add -A; git commit -qm "packs wave4: scaled teacher distillation (verified + raw drafts), retrained 6 specialist packs, TFLite (MoLab GPU)"; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:main
touch /tmp/paperlm/WAVE4_DONE
