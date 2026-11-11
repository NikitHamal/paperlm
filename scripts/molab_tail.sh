#!/bin/bash
scripts_dir=$(dirname "$0"); "$scripts_dir/molab_run.sh" "tail -n ${2:-20} /tmp/paperlm/logs/$1.log | cut -c1-400"
