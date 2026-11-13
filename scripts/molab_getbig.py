#!/usr/bin/env python3
"""Chunked binary download from the MoLab VM (marimo pair stdout is capped ~1MB). usage: molab_getbig.py REMOTE LOCAL"""
import sys, json, base64, subprocess, os
URL=os.environ.get("MOLAB_URL","https://sb-f920ad548f3c95a5.sb.molab.run/"); SESS=os.environ.get("MOLAB_SESSION","sess-2jr6f0tx18s41ctv"); TOK=os.environ.get("MOLAB_TOKEN_FILE",os.path.expanduser("~/.molab_token"))
CH=500_000
def ex(code):
    r=subprocess.run([sys.executable,"-m","marimo","pair","execute","--url",URL,"--session",SESS,"--token-file",TOK,"--code-file","-"],input=code,capture_output=True,text=True)
    d=json.loads(r.stdout); assert d.get("success"),d; return d["stdout"].strip()
remote,local=sys.argv[1],sys.argv[2]
n=int(ex(f"import os;print(os.path.getsize({remote!r}))"))
out=bytearray()
for off in range(0,n,CH):
    out+=base64.b64decode(ex(f"import base64\nf=open({remote!r},'rb');f.seek({off});print(base64.b64encode(f.read({CH})).decode())"))
open(local,"wb").write(out); print("got",local,len(out),"of",n)
