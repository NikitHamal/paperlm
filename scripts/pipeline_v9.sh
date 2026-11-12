#!/bin/bash
# v9 on the MoLab GPU: after v8 cycle 2 finishes, free the GPU and run the CROSS-FAMILY (Mistral-Small-24B) judge
#   1) over every stage-2-verified teacher MCQ (verified_all.jsonl)  -> cross_new/
#   2) over every gold MCQ with an explanation in the bank           -> cross_bank/
# then resume the Qwen teacher loop (v8 cycles 3..9) so the GPU never idles.
cd /tmp/paperlm
while ! grep -q "cycle 2 done" logs/pipeline_v8.log 2>/dev/null; do sleep 10; done
pkill -f pipeline_v8.sh; pkill -f teacher_gen.py; pkill -f teacher_verify.py; sleep 8
python3 eval/cross_verify.py /dev/shm/mistral24b cross_new --jsonl verified_all.jsonl --tag cross > logs/cross_new.log 2>&1
python3 eval/cross_verify.py /dev/shm/mistral24b cross_bank --bank bank_current.json --tag cross > logs/cross_bank.log 2>&1
echo "cross done $(date)" >> logs/pipeline_v9.log
START=3 END=9 nohup bash scripts/pipeline_v8.sh >> logs/pipeline_v8.log 2>&1 &
