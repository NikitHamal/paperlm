#!/bin/bash
# Fresh MoLab VM hydration (run ON the VM). Needs /tmp/gitenv.sh (askpass echoing the PAT; never committed).
mkdir -p /work /tmp/paperlm/logs
cd /work
[ -d paperlm/.git ] || GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git clone -q https://NikitHamal@github.com/NikitHamal/paperlm.git paperlm
cd paperlm && git checkout -q -B main && git config user.name NikitHamal && git config user.email nikithamal@users.noreply.github.com
git log --oneline | head -2
[ -d /tmp/neb_src/.git ] || GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git clone -q --depth 1 https://NikitHamal@github.com/NikitHamal/NEB.git /tmp/neb_src
ls /tmp/neb_src | head
curl -sI -m 10 https://huggingface.co | head -1
df -h /dev/shm /tmp | tail -2
pip list 2>/dev/null | grep -i -E "torch|transformers|onnx|tokenizers|marimo|sentencepiece|vllm|accelerate"
