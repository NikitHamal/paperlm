#!/bin/bash
# wave 8: second scaled distillation (FRESH anchors, never used by wave3-7) -> retrain all 10 packs on the larger verified banks -> TFLite -> publish -> push
cd /work/paperlm; L=/tmp/paperlm/logs; SA=${SA:-1400}; SB=${SB:-500}; SD=${SD:-250}; ALL="bio12 phy11 bio11 phy12 chem11 chem12 math11 math12 cs11 cs12"
rm -f /tmp/paperlm/WAVE8_DONE /tmp/paperlm/TRAINED_* /tmp/paperlm/TEACHER8_DONE
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
OFF=380 MAXA=${MAXA_B:-600} NSHORT=${NSHORT:-150} SUF=5 SH=2 python3 packs/tools/teacher.py chem11 chem12 math11 math12 cs11 cs12 > $L/teacher8b.log 2>&1
OFF=1050 MAXA=${MAXA_A:-520} NSHORT=${NSHORT:-150} SUF=6 SH=2 python3 packs/tools/teacher.py bio12 phy11 bio11 phy12 > $L/teacher8a.log 2>&1
touch /tmp/paperlm/TEACHER8_DONE
for p in $ALL; do ( python3 packs/tools/train_pack.py $p $SA $SB $SD > $L/train_$p.log 2>&1; cd /tmp && CUDA_VISIBLE_DEVICES= python3 /work/paperlm/packs/tools/export_tflite.py $p > $L/tflite_$p.log 2>&1; touch /tmp/paperlm/TRAINED_$p ) & done
wait
python3 packs/tools/publish.py $ALL > $L/publish.log 2>&1
git add -A; git commit -qm "packs wave8: 10 specialist packs retrained on 2x verified banks (MoLab GPU)"; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:main
touch /tmp/paperlm/WAVE8_DONE
