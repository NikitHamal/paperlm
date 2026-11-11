#!/usr/bin/env python3
"""PaperLM-Tiny trainer with live MoLab telemetry.  usage: train.py --name main --lr 2e-3 --dropout 0.1 --epochs 12"""
import argparse, json, math, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, "/tmp/paperlm"); sys.path.insert(0, "/tmp/paperlm/data")
import torch, torch.nn.functional as F
from tokenizers import Tokenizer
from architecture import build
from sampling import generate, pretty
import validator as V
try: import live_status as LS
except Exception: LS = None

ap = argparse.ArgumentParser()
ap.add_argument("--name", default="main"); ap.add_argument("--lr", type=float, default=2e-3); ap.add_argument("--dropout", type=float, default=0.1)
ap.add_argument("--epochs", type=int, default=12); ap.add_argument("--bs", type=int, default=64); ap.add_argument("--seq", type=int, default=512)
ap.add_argument("--wd", type=float, default=0.1); ap.add_argument("--warmup", type=int, default=100); ap.add_argument("--eval_every", type=int, default=40)
ap.add_argument("--sample_every", type=int, default=200); ap.add_argument("--live_samples", type=int, default=0); ap.add_argument("--seed", type=int, default=1); ap.add_argument("--book_frac", type=float, default=1.0); ap.add_argument("--ffn", type=int, default=960)
ap.add_argument("--data", default="/tmp/paperlm/gold"); ap.add_argument("--tok", default="/tmp/paperlm/tok/paperlm_tokenizer.json"); ap.add_argument("--out", default="/tmp/paperlm/ckpt")
a = ap.parse_args()
torch.manual_seed(a.seed); random.seed(a.seed)
dev = "cuda"; tok = Tokenizer.from_file(a.tok)
out = f"{a.out}/{a.name}"; os.makedirs(out, exist_ok=True)
PAD, END = 0, 2

def encode(path):
    return [tok.encode(l.rstrip("\n")).ids for l in open(path, encoding="utf-8") if l.strip()]
tr, va = encode(f"{a.data}/train.txt"), encode(f"{a.data}/val.txt")
tr = [x[:a.seq] for x in tr]; va = [x[:a.seq] for x in va]
if os.path.exists(f"{a.data}/book.txt") and a.book_frac > 0:
    bk = [x[:a.seq] for x in encode(f"{a.data}/book.txt")]; random.Random(0).shuffle(bk)
    nb = int(len(bk) * a.book_frac); tr = tr + bk[:nb]; print("book chunks added:", nb, flush=True)
ntok_train = sum(map(len, tr))

def pack(items, shuffle):
    items = items[:]
    if shuffle: random.shuffle(items)
    rows, cur = [], []
    for it in items:
        if len(cur) + len(it) > a.seq: rows.append(cur); cur = []
        cur = cur + it
    if cur: rows.append(cur)
    X = torch.full((len(rows), a.seq), PAD, dtype=torch.long)
    for i, r in enumerate(rows): X[i, :len(r)] = torch.tensor(r)
    return X
Xv = pack(va, False).to(dev)

cfg = dict(vocab_size=tok.get_vocab_size(), dropout=a.dropout, max_seq=1024, ffn_hidden=a.ffn)
model = build(cfg).to(dev)
nparams = model.n_params()
decay = [p for n, p in model.named_parameters() if p.dim() >= 2]; nodecay = [p for n, p in model.named_parameters() if p.dim() < 2]
opt = torch.optim.AdamW([{"params": decay, "weight_decay": a.wd}, {"params": nodecay, "weight_decay": 0}], lr=a.lr, betas=(0.9, 0.95), fused=True)
steps_per_epoch = math.ceil(pack(tr, True).shape[0] / a.bs); total = steps_per_epoch * a.epochs
def lr_at(s):
    if s < a.warmup: return a.lr * (s + 1) / a.warmup
    p = (s - a.warmup) / max(1, total - a.warmup); return a.lr * (0.05 + 0.95 * 0.5 * (1 + math.cos(math.pi * p)))

def loss_fn(x):
    with torch.autocast("cuda", dtype=torch.bfloat16):
        lg = model(x[:, :-1])
    return F.cross_entropy(lg.float().reshape(-1, lg.shape[-1]), x[:, 1:].reshape(-1), ignore_index=PAD, reduction="sum"), (x[:, 1:] != PAD).sum()

@torch.no_grad()
def evaluate():
    model.eval(); L = N = 0
    for i in range(0, Xv.shape[0], 64):
        l, n = loss_fn(Xv[i:i + 64]); L += l.item(); N += n.item()
    model.train(); return L / N

PROMPTS = [("NEB", "C12", "physics", "Rotational dynamics", 5, "NUMERICAL"), ("SEE", "C10", "science", "Heredity", 1, "MCQ"),
           ("NEB", "C11", "chemistry", "Chemical bonding", 5, "CONCEPTUAL"), ("IOE", "BE", "general", "Engineering Mechanics", 8, "LONG"),
           ("CEE", "CEE", "physics", "Optics", 1, "MCQ"), ("NEB", "C12", "mathematics", "Differentiation", 5, "OR")]
def make_samples(step):
    items, ok = [], 0
    for (b, l, s, u, m, t) in PROMPTS:
        sid = f"<|subj={s}|>" if f"<|subj={s}|>" in tok.get_vocab() else "<|subj=general|>"
        h = f"<|bos|><|board={b}|><|level={l}|>{sid}<|unit|>{u}<|marks={m}|><|type={t}|><|q|>"
        g = generate(model, tok.encode(h).ids, max_new=380, temperature=0.7, top_p=0.9)
        txt = h + tok.decode(g, skip_special_tokens=False).replace("Ġ", " ")
        txt = re.sub(r"\s*(<\|[^|]+\|>)\s*", r"\1", txt) if False else txt
        good = V.validate_item_text(txt) is None; ok += good
        items.append(("✅ " if good else "⚠️ ") + pretty(txt))
    return items, ok / len(PROMPTS)
import re

hist, best, t0, seen_tokens = [], 1e9, time.time(), 0
step = 0; model.train()
LSN = f"train_{a.name}"
if LS:
    LS.update("stage", name="TRAIN", phase=f"training {a.name}", detail=f"{nparams/1e6:.2f}M params · {total} steps")
for ep in range(a.epochs):
    X = pack(tr, True).to(dev)
    for i in range(0, X.shape[0], a.bs):
        xb = X[i:i + a.bs]
        for g in opt.param_groups: g["lr"] = lr_at(step)
        l, n = loss_fn(xb); (l / n).backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); opt.zero_grad(set_to_none=True)
        step += 1; seen_tokens += n.item()
        if step % a.eval_every == 0 or step == total:
            vl = evaluate(); tl = (l / n).item(); el = time.time() - t0; sps = step / el
            hist.append([step, round(tl, 4), round(vl, 4)])
            if vl < best:
                best = vl; torch.save(dict(model=model.state_dict(), cfg=model.cfg.__dict__, step=step, val_loss=vl), f"{out}/best.pt")
            if LS:
                LS.update(LSN, model=f"PaperLM-Tiny [{a.name}]", params=nparams, step=step, total_steps=total, epoch=step / steps_per_epoch, train_loss=tl, val_loss=vl,
                          ppl=math.exp(vl), lr=lr_at(step), tok_s=seen_tokens / el, eta_s=(total - step) / sps, best_val=best, history=hist[-400:], run=a.name)
            print(f"step {step}/{total} ep {step/steps_per_epoch:.2f} train {tl:.4f} val {vl:.4f} ppl {math.exp(vl):.2f} best {best:.4f} tok/s {seen_tokens/el:,.0f}", flush=True)
        if a.live_samples and step % a.sample_every == 0:
            try:
                items, rate = make_samples(step); LS.update("samples", step=step, items=items, valid_rate=rate, run=a.name)
            except Exception as e: print("sample err", e)
            model.train()
torch.save(dict(model=model.state_dict(), cfg=model.cfg.__dict__, step=step, val_loss=evaluate()), f"{out}/last.pt")
json.dump(dict(args=vars(a), params=nparams, best_val=best, ppl=math.exp(best), history=hist, train_tokens=ntok_train, seconds=time.time() - t0), open(f"{out}/train_log.json", "w"))
print("DONE best_val", best, "ppl", math.exp(best), "params", nparams, flush=True)
