import subprocess, sys, os
cmd = open('/f/paperlm/.vm/cmd.txt', encoding='utf-8').read()
r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=1800)
print(r.stdout[-14000:])
print("STDERR:", r.stderr[-3000:])
