#!/bin/bash
# wave 9 (sanitising teacher): second scaled distillation (FRESH anchors, never used by wave3-7) -> retrain all 10 packs on the larger verified banks -> TFLite -> publish -> push
cd /work/paperlm; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase; L=/tmp/paperlm/logs; SA=${SA:-1400}; SB=${SB:-500}; SD=${SD:-250}; ALL="bio12 phy11 bio11 phy12 chem11 chem12 math11 math12 cs11 cs12"
rm -f /tmp/paperlm/WAVE9_DONE /tmp/paperlm/TRAINED_* /tmp/paperlm/TEACHER9_DONE
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
OFF=980 MAXA=${MAXA_B:-650} NSHORT=${NSHORT:-150} SUF=7 SH=3 python3 packs/tools/teacher.py chem11 chem12 math11 math12 cs11 cs12 > $L/teacher9b.log 2>&1
OFF=1570 MAXA=${MAXA_A:-600} NSHORT=${NSHORT:-150} SUF=8 SH=3 python3 packs/tools/teacher.py bio12 phy11 bio11 phy12 > $L/teacher9a.log 2>&1
touch /tmp/paperlm/TEACHER9_DONE
for p in $ALL; do ( python3 packs/tools/train_pack.py $p $SA $SB $SD > $L/train_$p.log 2>&1; cd /tmp && CUDA_VISIBLE_DEVICES= python3 /work/paperlm/packs/tools/export_tflite.py $p > $L/tflite_$p.log 2>&1; touch /tmp/paperlm/TRAINED_$p ) & done
wait
python3 packs/tools/publish.py $ALL > $L/publish.log 2>&1
git add -A; git commit -qm "packs wave9: 10 specialist packs retrained on 2x verified banks (MoLab GPU)"; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:main
touch /tmp/paperlm/WAVE9_DONE
