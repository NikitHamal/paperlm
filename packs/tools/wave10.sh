#!/bin/bash
# wave 10 (fresh VM): waits for Qwen download + corpus hydration, runs the verified teacher on anchors never used by waves 3-9,
# retrains all 10 specialist packs on the larger verified banks -> TFLite -> publish -> push (from the VM).
cd /work/paperlm; L=/tmp/paperlm/logs; SA=${SA:-1400}; SB=${SB:-500}; SD=${SD:-250}; ALL="bio12 phy11 bio11 phy12 chem11 chem12 math11 math12 cs11 cs12"
git config merge.keepvm.driver "cp %B %A"; printf 'docs/packs/** merge=keepvm\npacks/*/** merge=keepvm\n' > .git/info/attributes
while [ ! -f /tmp/paperlm/QWEN_DONE ] || [ ! -f /tmp/paperlm/HYDRATED ]; do sleep 10; done
GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase
rm -f /tmp/paperlm/WAVE10_DONE /tmp/paperlm/TRAINED_* /tmp/paperlm/TEACHER10_DONE
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
OFF=1630 MAXA=${MAXA_B:-700} NSHORT=${NSHORT:-220} SUF=9 SH=4 python3 packs/tools/teacher.py chem11 chem12 math11 math12 cs11 cs12 > $L/teacher10b.log 2>&1
OFF=2170 MAXA=${MAXA_A:-700} NSHORT=${NSHORT:-220} SUF=10 SH=4 python3 packs/tools/teacher.py bio12 phy11 bio11 phy12 > $L/teacher10a.log 2>&1
touch /tmp/paperlm/TEACHER10_DONE
for p in $ALL; do ( python3 packs/tools/train_pack.py $p $SA $SB $SD > $L/train_$p.log 2>&1; cd /tmp && CUDA_VISIBLE_DEVICES= python3 /work/paperlm/packs/tools/export_tflite.py $p > $L/tflite_$p.log 2>&1; touch /tmp/paperlm/TRAINED_$p ) & done
wait
python3 packs/tools/publish.py $ALL > $L/publish.log 2>&1
cd /work/paperlm; git add -A; git commit -qm "packs wave10: 10 specialist packs retrained on 3x verified banks (MoLab GPU)"; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase; GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git push -q origin HEAD:main
touch /tmp/paperlm/WAVE10_DONE
