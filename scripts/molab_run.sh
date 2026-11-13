#!/bin/bash
# usage: molab_run.sh '<shell command>' ; runs shell on MoLab VM, prints stdout/stderr
CMD="$1"
python3 -m marimo pair execute --url "${MOLAB_URL:-https://sb-f920ad548f3c95a5.sb.molab.run/}" --session "${MOLAB_SESSION:-sess-2jr6f0tx18s41ctv}" --token-file "${MOLAB_TOKEN_FILE:-$HOME/.molab_token}" --code-file - <<PY | python3 -c "import sys,json;d=json.load(sys.stdin);print((d.get('stdout') or '')+(d.get('stderr') or '')+('' if d.get('success') else str(d)))"
import subprocess
r=subprocess.run(r'''$CMD''',shell=True,capture_output=True,text=True,errors="replace")
print(r.stdout+r.stderr)
PY
