#!/bin/bash
# wave 6 (supersedes wave4/5): finish bio12 teacher, then (fixed teacher: MAXNEW=300 + rejection telemetry) phy11 bio11 phy12 + chem/math/cs -> train ALL 10 in parallel -> TFLite -> publish -> push
cd /work/paperlm; L=/tmp/paperlm/logs; SA=${SA:-1400}; SB=${SB:-500}; SD=${SD:-250}; ALL="bio12 phy11 bio11 phy12 chem11 chem12 math11 math12 cs11 cs12"
pkill -f "[w]ave5.sh"
while ! grep -q "^bio12 kept" $L/teacher4a.log; do sleep 10; done
pkill -f "[t]eacher.py"; sleep 8
rm -f /tmp/paperlm/WAVE6_DONE /tmp/paperlm/TRAINED_*
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
OFF=600 MAXA=${MAXA1:-450} NSHORT=${NSHORT:-140} SUF=3 python3 packs/tools/teacher.py phy11 bio11 phy12 > $L/teacher6a.log 2>&1
OFF=0 MAXA=${MAXA2:-380} NSHORT=${NSHORT:-120} SUF=3 python3 packs/tools/teacher.py chem11 chem12 math11 math12 cs11 cs12 > $L/teacher6b.log 2>&1
touch /tmp/paperlm/TEACHER6_DONE
for p in $ALL; do ( python3 packs/tools/train_pack.py $p $SA $SB $SD > $L/train_$p.log 2>&1; cd /tmp && python3 /work/paperlm/packs/tools/export_tflite.py $p > $L/tflite_$p.log 2>&1; touch /tmp/paperlm/TRAINED_$p ) & done
wait
python3 packs/tools/publish.py $ALL > $L/publish.log 2>&1
git add -A; git commit -qm "packs wave6: 10 specialist packs (bio/phy/chem/math/cs x C11/C12), scaled distillation, TFLite (MoLab GPU)"; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:main
touch /tmp/paperlm/WAVE6_DONE
