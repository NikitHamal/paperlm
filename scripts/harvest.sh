#!/bin/bash
# usage: scripts/harvest.sh  -> prints wave markers, teacher yield/rejects, publish tail from the MoLab VM, then pulls the VM's pushed packs.
cd "$(dirname "$0")/.." || exit 1
scripts/molab_run.sh 'ls /tmp/paperlm/*DONE /tmp/paperlm/TRAINED_* 2>/dev/null; cut -c1-520 /tmp/paperlm/status_packs.json; echo; tail -3 /tmp/paperlm/logs/publish.log | cut -c1-300; tail -1 /tmp/paperlm/heartbeat.txt; ps -eo etime,cmd | grep -E "[w]ave|[t]eacher|[t]rain_pack" | cut -c1-120' | tail -30
GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git pull -q --rebase 2>&1 | tail -2; git log --oneline | head -3
