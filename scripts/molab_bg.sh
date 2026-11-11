#!/bin/bash
# usage: molab_bg.sh <name> '<shell command>' ; runs detached on VM, logs to /tmp/paperlm/logs/<name>.log
NAME="$1"; CMD="$2"
python3 -m marimo pair execute --url "${MOLAB_URL:-https://sb-bc79ba58e2c2c51f.sb.molab.run/}" --session "${MOLAB_SESSION:-sess-qa914tcyg7j8cndd}" --token-file "${MOLAB_TOKEN_FILE:-/tmp/molab_token}" --code-file - <<PY | python3 -c "import sys,json;d=json.load(sys.stdin);print('started' if d.get('success') else d)"
import subprocess,os
os.makedirs('/tmp/paperlm/logs',exist_ok=True)
open('/tmp/paperlm/logs/$NAME.sh','w').write(r'''$CMD''')
subprocess.Popen('setsid nohup bash /tmp/paperlm/logs/$NAME.sh > /tmp/paperlm/logs/$NAME.log 2>&1 < /dev/null &',shell=True)
PY
