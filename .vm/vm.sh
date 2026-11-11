#!/bin/bash
# usage: vm.sh '<shell cmd>'  -> runs on MoLab VM (base64-inlined, no local file refs)
CMD="$1"
B64=$(printf '%s' "$CMD" | base64 -w0)
cat > /tmp/.vmcell.py <<PYEOF
import subprocess, base64
cmd = base64.b64decode("$B64").decode()
r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3600)
print(r.stdout[-16000:])
if r.stderr.strip(): print("--- STDERR ---"); print(r.stderr[-4000:])
PYEOF
uvx marimo@latest pair execute --url "${MOLAB_URL:-https://sb-bc79ba58e2c2c51f.sb.molab.run/}" --code-file /tmp/.vmcell.py 2>&1 | python3 -c "
import sys,json
raw=sys.stdin.read()
try:
    d=json.loads(raw); print(d.get('stdout','') or '')
    if not d.get('success'): print('NOT SUCCESS:', str(d)[:1500])
except Exception: print(raw[:4000])
"
