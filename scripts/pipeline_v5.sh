#!/bin/bash
# Runs on the MoLab VM (background): grounded RFT rounds -> val bench -> pick best -> export -> release4 -> factual benchmark.
cd /tmp/paperlm; CK=/tmp/paperlm/ckpt2; D=/tmp/paperlm/gold4; R=/tmp/paperlm/release4; mkdir -p $R logs rft
live() { python3 -c "import sys;sys.path.insert(0,'/tmp/paperlm');import live_status as LS;LS.update('stage',name=sys.argv[1],phase=sys.argv[2],detail=sys.argv[3]);LS.update('iteration',n=4,label='v4',note=sys.argv[2])" "$1" "$2" "$3"; }
gen() { # $1 ckpt $2 split $3 outdir $4 per $5 shards
  for i in $(seq 0 $(($5-1))); do (cd eval && python3 rft4.py gen --ckpt $1 --split $2 --shard $i --nshards $5 --per $4 --out $3 --tries ${6:-6} --beta 2.5 > /tmp/paperlm/logs/rft4_$(basename $3)_$i.log 2>&1) & done; wait; }
bench() { gen $1 val /tmp/paperlm/rft/val_$2 90 8 4; (cd eval && python3 rft4.py bench --out /tmp/paperlm/rft/val_$2 --label $2 > /tmp/paperlm/logs/bench4_$2.log 2>&1); cp /tmp/paperlm/rft/val_$2/bench_$2.json $R/; }
BEST=$CK/v4b/best_A.pt; BL=v4b
live "BENCH v4b" "grounded val benchmark" "concept-conditioned SFT checkpoint"; bench $BEST v4b
for r in 1 2 3; do
  live "RFT $r" "grounded rejection sampling round $r" "16 shards x 300 anchors, copy-bias beta=2.5, verify + strict gate"; rm -rf rft/g$r; gen $BEST train /tmp/paperlm/rft/g$r 300 16 6
  (cd eval && python3 rft4.py merge --out /tmp/paperlm/rft/g$r --dest $D/stageR$r.txt > logs/merge4_$r.log 2>&1); cp rft/g$r/rft_stats.json $R/rft4_stats_round$r.json
  live "TRAIN RFT $r" "fine-tune on gate-passing items" "round $r"; python3 model/train_v2.py --name v4r$r --plan "R,stageR$r.txt,2,3e-4,0.1" --init $BEST --data $D --live 1 --iter v4 --eval_every 50 --sample_every 400 --wd 0.2 > logs/run_v4r$r.log 2>&1
  live "BENCH v4r$r" "grounded val benchmark" "round $r"; bench $CK/v4r$r/best_R.pt v4r$r
  NEW=$(python3 -c "import json;a=json.load(open('$R/bench_$BL.json'));b=json.load(open('$R/bench_v4r$r.json'));print('new' if b['prompts_resolved_rate']>=a['prompts_resolved_rate'] else 'old')")
  if [ "$NEW" = "new" ]; then BEST=$CK/v4r$r/best_R.pt; BL=v4r$r; fi
done
echo $BEST $BL > $R/final_choice.txt
live "EXPORT" "INT8/FP16 ONNX export" "$BL"; python3 model/export.py $BEST /tmp/paperlm/tok/paperlm_tokenizer.json $D/val_clean.txt $R > logs/export4.log 2>&1
cp $D/concept_bank.json $D/dataset_v4_stats.json $R/; cp logs/run_v4*.log $R/ 2>/dev/null
live "FACTUAL BENCH" "composed-system accuracy benchmark" "600 requests"; (cd eval && python3 factual_bench.py --ckpt $BEST --bank $D/concept_bank.json --val $D/val.txt --n 600 --out $R --label $BL --live 1 > ../logs/factual4.log 2>&1)
touch $R/READY; live "DONE" "v5 pipeline complete" "release4 ready: $BL"
