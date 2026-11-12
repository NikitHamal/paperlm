#!/bin/bash
# Deterministic validation of every shipped pack (no browser): Python onnxruntime FSM decode, planner invariants, Node onnxruntime-node load.
# prerequisites: pip install onnxruntime tokenizers numpy ; (cd /tmp/jsenv && npm i onnxruntime-node)
cd "$(dirname "$0")/.." || exit 1
python3 eval/ort_pack_check.py 3 2 | cut -c1-200
python3 eval/pack_paper_test.py | tail -1
[ -d /tmp/jsenv/node_modules/onnxruntime-node ] && node eval/node_pack_bench.mjs 4 2 "${@:-phy11}" | grep -E '"(neural_accepted|empty|duplicates|bank_size)"'
