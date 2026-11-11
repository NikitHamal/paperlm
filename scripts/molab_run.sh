#!/bin/bash
# usage: molab_run.sh '<shell command>' ; runs shell on MoLab VM, prints stdout/stderr
CMD="$1"
python3 -m marimo pair execute --url "${MOLAB_URL:-https://sb-bc79ba58e2c2c51f.sb.molab.run/}" --session "${MOLAB_SESSION:-sess-qa914tcyg7j8cndd}" --token-file "${MOLAB_TOKEN_FILE:-/tmp/molab_token}" --code-file - <<PY | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('stdout','')+d.get('stderr','')+('' if d.get('success') else str(d)))"
import subprocess
r=subprocess.run(r'''$CMD''',shell=True,capture_output=True,text=True)
print(r.stdout+r.stderr)
PY
