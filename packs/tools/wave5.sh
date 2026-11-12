#!/bin/bash
# wave 5: wait for running flagship teacher job -> teacher for chem + math + cs packs -> train ALL 10 packs in parallel -> TFLite -> publish -> push
cd /work/paperlm; L=/tmp/paperlm/logs; SA=${SA:-1500}; SB=${SB:-500}; SD=${SD:-250}; ALL="bio12 phy11 bio11 phy12 chem11 chem12 math11 math12 cs11 cs12"
while pgrep -f "[p]acks/tools/teacher.py" > /dev/null; do sleep 20; done
rm -f /tmp/paperlm/WAVE5_DONE /tmp/paperlm/TRAINED_*
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
OFF=0 MAXA=${MAXA:-380} NSHORT=${NSHORT:-120} SUF=3 python3 packs/tools/teacher.py chem11 chem12 math11 math12 cs11 cs12 > $L/teacher5.log 2>&1
touch /tmp/paperlm/TEACHER5_DONE
for p in $ALL; do ( python3 packs/tools/train_pack.py $p $SA $SB $SD > $L/train_$p.log 2>&1; cd /tmp && python3 /work/paperlm/packs/tools/export_tflite.py $p > $L/tflite_$p.log 2>&1; touch /tmp/paperlm/TRAINED_$p ) & done
wait
python3 packs/tools/publish.py $ALL > $L/publish.log 2>&1
git add -A; git commit -qm "packs wave5: 10 specialist packs (bio/phy/chem/math/cs x C11/C12), scaled distillation, TFLite (MoLab GPU)"; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:main
touch /tmp/paperlm/WAVE5_DONE
