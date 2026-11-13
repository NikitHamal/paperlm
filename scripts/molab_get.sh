#!/bin/bash
# usage: molab_get.sh <remote_path> <local_path>   (binary-safe, via base64 over marimo pair)
python3 -m marimo pair execute --url "${MOLAB_URL:-https://sb-bcd34742cc2db121.sb.molab.run/}" --session "${MOLAB_SESSION:-sess-g6jk0kts3q0wvw99}" --token-file "${MOLAB_TOKEN_FILE:-$HOME/.molab_token}" --code-file - <<PY | python3 -c "
import sys,json,base64
d=json.load(sys.stdin); assert d.get('success'),d
open('$2','wb').write(base64.b64decode(d['stdout'].strip()))
print('got $2')"
import base64
print(base64.b64encode(open('$1','rb').read()).decode())
PY
