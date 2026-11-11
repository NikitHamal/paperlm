#!/bin/bash
# v7: 32B judge audit of the gold bank -> teacher generation with independent verification. Runs on the MoLab VM.
cd /tmp/paperlm/repo
python3 eval/judge_bank.py /dev/shm/qwen32b docs/model/bank.json /tmp/paperlm/judge_full > /tmp/paperlm/logs/judge_full.out 2>&1
TARGET_MCQ=14 P_MIN=0.85 python3 eval/teacher_gen.py /dev/shm/qwen32b docs/model/bank.json docs/model/catalog.json /tmp/paperlm/gen_v7 8 4 > /tmp/paperlm/logs/gen_v7.out 2>&1
