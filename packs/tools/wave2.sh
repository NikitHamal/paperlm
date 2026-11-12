#!/bin/bash
# wave 2 (runs on the MoLab VM): train each pack as soon as the teacher has moved on, then chem11/chem12 teacher+train, TFLite export, publish, push.
cd /work/paperlm; L=/tmp/paperlm/logs; SA=${SA:-1500}; SB=${SB:-700}; SD=${SD:-300}
fin() { p=$1; python3 packs/tools/train_pack.py $p $SA $SB $SD > $L/train_$p.log 2>&1; (cd /tmp && python3 /work/paperlm/packs/tools/export_tflite.py $p > $L/tflite_$p.log 2>&1); touch /tmp/paperlm/TRAINED_$p; }
arr=(bio12 phy11 bio11 phy12)
for i in 0 1 2 3; do p=${arr[$i]}; n=${arr[$((i+1))]}
  while [ ! -f /tmp/paperlm/TEACHER2_DONE ] && { [ -z "$n" ] || [ ! -f /tmp/packs/$n/verified2.jsonl ]; }; do sleep 10; done
  fin $p &
done
while [ ! -f /tmp/paperlm/TEACHER2_DONE ]; do sleep 10; done
rm -f /tmp/paperlm/TEACHER3_DONE
(PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OFF=0 MAXA=${CMAXA:-1300} NSHORT=400 SUF= python3 packs/tools/teacher.py chem11 chem12 > $L/teacher_chem.log 2>&1; touch /tmp/paperlm/TEACHER3_DONE) &
while [ ! -f /tmp/packs/chem12/verified.jsonl ] && [ ! -f /tmp/paperlm/TEACHER3_DONE ]; do sleep 10; done
fin chem11 &
while [ ! -f /tmp/paperlm/TEACHER3_DONE ]; do sleep 10; done
fin chem12 &
wait
python3 packs/tools/publish.py bio12 phy11 bio11 phy12 chem11 chem12 > $L/publish.log 2>&1
git add -A; git commit -qm "wave2 packs: verified bank, val-best training, TFLite (MoLab GPU)"; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:main
touch /tmp/paperlm/WAVE2_DONE
