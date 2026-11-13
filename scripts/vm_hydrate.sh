#!/bin/bash
# Run ON a fresh MoLab VM after vm_bootstrap.sh: raw NEB corpus -> /tmp/gold/{gold.jsonl,book.txt} -> per-pack anchors in /tmp/packs/<id>/
set -x
cd /work/paperlm
while pgrep -f "git clone.*NEB" >/dev/null; do sleep 5; done
mkdir -p /tmp/clones /tmp/gold
[ -d /tmp/clones/main ] || mv /tmp/neb_src /tmp/clones/main
for b in claude/bsc-nursing claude/engineering; do
  d=/tmp/clones/$(echo $b | tr / _); [ -d $d ] || GIT_ASKPASS=/tmp/gitenv.sh GIT_TERMINAL_PROMPT=0 git clone -q --depth 1 -b $b https://NikitHamal@github.com/NikitHamal/NEB.git $d
done
python3 data/extract_neb.py /tmp/gold/raw.jsonl /tmp/clones 2>&1 | tail -5
python3 data/build_dataset.py /tmp/gold/raw.jsonl /tmp/gold 2>&1 | tail -5
python3 data/extract_books.py /tmp/clones /tmp/gold/book.txt 2>&1 | tail -3
ls -la /tmp/gold; wc -l /tmp/gold/*.jsonl /tmp/gold/book.txt
bash packs/tools/build_all.sh bio12 phy11 bio11 phy12 chem11 chem12 math11 math12 cs11 cs12 2>&1 | tail -15
wc -l /tmp/packs/*/anchors.jsonl
touch /tmp/paperlm/HYDRATED
