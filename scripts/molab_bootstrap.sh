#!/bin/bash
# Re-create the PaperLM GPU workspace on a NEW MoLab sandbox. usage: MOLAB_URL=... MOLAB_SESSION=... [MOLAB_TOKEN_FILE=$HOME/.molab_token] scripts/molab_bootstrap.sh
set -e; cd "$(dirname "$0")/.."
R=scripts/molab_run.sh
$R 'mkdir -p /tmp/paperlm/{logs,eval,scripts,repo/docs/model,gen_v8_2}; nvidia-smi --query-gpu=name,memory.total --format=csv'
for f in eval/teacher_gen.py eval/teacher_verify.py eval/cross_verify.py eval/merge_teacher.py molab/dash_judge.py molab/keepalive.py scripts/pipeline_v8.sh scripts/pipeline_v9.sh data/coherence_gate.py; do
  case $f in eval/*) d=/tmp/paperlm/eval/$(basename $f);; scripts/*) d=/tmp/paperlm/scripts/$(basename $f);; *) d=/tmp/paperlm/$(basename $f);; esac; scripts/molab_put.sh $f $d; done
for f in bank.json catalog.json; do scripts/molab_put.sh docs/model/$f /tmp/paperlm/repo/docs/model/$f; done
scripts/molab_bg.sh keepalive 'cd /tmp/paperlm && python3 keepalive.py'
scripts/molab_bg.sh dl_models 'python3 -c "
from huggingface_hub import snapshot_download as d
d(\"Qwen/Qwen2.5-32B-Instruct\", local_dir=\"/dev/shm/qwen32b\", allow_patterns=[\"*.safetensors\",\"*.json\",\"tokenizer*\",\"*.txt\"])
d(\"mistralai/Mistral-Small-24B-Instruct-2501\", local_dir=\"/dev/shm/mistral24b\", allow_patterns=[\"*.safetensors\",\"*.json\",\"tokenizer*\",\"*.model\"])
print(\"DONE\")"'
echo "next: python3 -m marimo pair execute ... --code-file molab/install_verify.py / install_cross.py ; then scripts/molab_bg.sh v8 'START=2 END=9 bash /tmp/paperlm/scripts/pipeline_v8.sh' and pipeline_v9.sh"
