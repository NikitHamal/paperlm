#!/bin/bash
# Continuous verified-teacher loop on the MoLab GPU: generate (seeded) -> stage-2 verify -> accumulate -> merge into bank_current.json.
# Each cycle is independent; harvest /tmp/paperlm/verified_all.jsonl + bank_current.json at any time.
cd /tmp/paperlm
[ -f bank_current.json ] || cp repo/docs/model/bank.json bank_current.json
for i in $(seq ${START:-2} ${END:-9}); do
  SEED=$i python3 eval/teacher_gen.py /dev/shm/qwen32b bank_current.json repo/docs/model/catalog.json gen_v8_$i 8 1 > logs/gen_v8_$i.log 2>&1
  [ -s gen_v8_$i/teacher_items.jsonl ] || continue
  python3 eval/teacher_verify.py /dev/shm/qwen32b gen_v8_$i/teacher_items.jsonl verify_v8_$i > logs/verify_v8_$i.log 2>&1
  [ -f verify_v8_$i/teacher_verified.jsonl ] && cat verify_v8_$i/teacher_verified.jsonl >> verified_all.jsonl
  python3 eval/merge_teacher.py verified_all.jsonl bank_current.json >> logs/merge_v8.log 2>&1
  echo "cycle $i done $(date)" >> logs/pipeline_v8.log
done
