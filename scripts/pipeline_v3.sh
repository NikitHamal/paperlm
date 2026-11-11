#!/bin/bash
# Runs on the MoLab VM: pick best pretrain ckpt -> benchmark -> verifier-guided rejection sampling (Stage C) -> fine-tune -> benchmark -> export -> release dir.
cd /tmp/paperlm; CK=/tmp/paperlm/ckpt2; R=/tmp/paperlm/release; mkdir -p $R $R/bench
live() { python3 -c "import sys;sys.path.insert(0,'/tmp/paperlm');import live_status as LS;LS.update('stage',name=sys.argv[1],phase=sys.argv[2],detail=sys.argv[3]);LS.update('iteration',n=3,label='v3',note=sys.argv[2])" "$1" "$2" "$3"; }
for n in v2h v2i; do until grep -q '^DONE' logs/run_$n.log 2>/dev/null; do sleep 20; done; done
live "SELECT" "choosing best v2 checkpoint" "by held-out val_clean"
BEST=$(python3 - <<PY
import torch,glob
c=[]
for f in glob.glob("$CK/v2[ghi]/best_*.pt")+glob.glob("$CK/v2[efd]/best_*.pt"):
    d=torch.load(f,map_location="cpu"); c.append((d["val_clean"],d["val_loss"],f))
c.sort(); print(c[0][2]); import sys; print(c[:4],file=sys.stderr)
PY
)
echo BEST=$BEST; cp $BEST $CK/best_v2.pt
live "BENCH v2" "benchmarking v2 pretrain checkpoint" "$BEST"
(cd eval && python3 benchmark.py --ckpt $CK/best_v2.pt --label v2 --n 240 --full_n 80 --prev /tmp/paperlm/evalout/benchmark_v1.json --live 1 > /tmp/paperlm/logs/bench_v2.log 2>&1)
live "RFT" "verifier-guided rejection sampling (Stage C)" "12 shards x 400 prompts"
NS=12; mkdir -p rft/v3; rm -f rft/v3/cand_*.jsonl
for i in $(seq 0 $((NS-1))); do (cd model && python3 rft.py gen --ckpt $CK/best_v2.pt --shard $i --nshards $NS --per 420 --out /tmp/paperlm/rft/v3 > /tmp/paperlm/logs/rft_$i.log 2>&1 &) ; done
sleep 30; while pgrep -f "rft.py gen" > /dev/null; do sleep 15; done
(cd model && python3 rft.py merge --out /tmp/paperlm/rft/v3 --replay 0.5 > /tmp/paperlm/logs/rft_merge.log 2>&1)
live "TRAIN v3" "Stage C fine-tune on verified self-generated + gold replay" "lr 2e-4, dropout 0.05"
(cd model && python3 train_v2.py --name v3 --bs 32 --eval_every 100 --warmup 50 --init $CK/best_v2.pt --plan "C,stageC.txt,3,2e-4,0.05" --live 1 --iter v3 --sample_every 100000 > /tmp/paperlm/logs/run_v3.log 2>&1)
live "BENCH v3" "benchmarking v3" "stage C checkpoint"
(cd eval && python3 benchmark.py --ckpt $CK/v3/best_C.pt --label v3 --n 240 --full_n 80 --prev /tmp/paperlm/evalout/benchmark_v2.json --live 1 > /tmp/paperlm/logs/bench_v3.log 2>&1)
python3 - <<PY
import json,torch
a=json.load(open("/tmp/paperlm/evalout/benchmark_v2.json")); b=json.load(open("/tmp/paperlm/evalout/benchmark_v3.json"))
vc2=torch.load("$CK/best_v2.pt",map_location="cpu")["val_clean"]; vc3=torch.load("$CK/v3/best_C.pt",map_location="cpu")["val_clean"]
better = b["raw"]["raw verifier pass rate"] >= a["raw"]["raw verifier pass rate"] and vc3 <= vc2 + 0.06
pick = "$CK/v3/best_C.pt" if better else "$CK/best_v2.pt"; open("/tmp/paperlm/release/final_choice.json","w").write(json.dumps(dict(pick=pick,label="v3" if better else "v2",v2=a["raw"],v3=b["raw"],vc2=vc2,vc3=vc3)))
print(pick)
PY
FINAL=$(python3 -c "import json;print(json.load(open('/tmp/paperlm/release/final_choice.json'))['pick'])")
live "EXPORT" "INT8/FP16 ONNX export" "$FINAL"
python3 model/export.py $FINAL /tmp/paperlm/tok/paperlm_tokenizer.json /tmp/paperlm/gold2/val_clean.txt $R > logs/export.log 2>&1
cp evalout/benchmark_v*.json $R/bench/; cp gold2/dataset_v2_stats.json gold2/stageA2_stats.json gold2/lexicon.json rft/v3/rft_stats.json $R/ 2>/dev/null
cp ckpt2/v2*/train_log.json $R/ 2>/dev/null; for n in v2d v2e v2f v2g v2h v2i v3; do cp ckpt2/$n/train_log.json $R/train_log_$n.json 2>/dev/null; done
(cd eval && python3 sample_compare.py /tmp/paperlm/ckpt/f/best.pt $FINAL v1 $(python3 -c "import json;print(json.load(open('/tmp/paperlm/release/final_choice.json'))['label'])") $R/samples.json > /tmp/paperlm/logs/samples.log 2>&1)
live "DONE" "v3 pipeline complete" "release dir /tmp/paperlm/release ready"
touch $R/READY
