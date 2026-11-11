#!/bin/bash
# usage: molab_put.sh <local_file> <remote_path> ; uploads a file to the MoLab VM via marimo pair
# env: MOLAB_URL, MOLAB_SESSION, MOLAB_TOKEN_FILE
LOCAL="$1"; REMOTE="$2"
B64=$(base64 -w0 "$LOCAL")
python3 -m marimo pair execute --url "${MOLAB_URL:-https://sb-bc79ba58e2c2c51f.sb.molab.run/}" --session "${MOLAB_SESSION:-sess-qa914tcyg7j8cndd}" --token-file "${MOLAB_TOKEN_FILE:-/tmp/molab_token}" --code-file - <<PY | python3 -c "import sys,json;d=json.load(sys.stdin);print('ok' if d.get('success') else d)"
import base64,os
os.makedirs(os.path.dirname("$REMOTE"),exist_ok=True)
open("$REMOTE","wb").write(base64.b64decode("$B64"))
print("wrote $REMOTE")
PY
