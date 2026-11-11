#!/usr/bin/env python3
"""PaperLM-Tiny multi-stage trainer (v2+): bf16, torch.compile, curriculum plan, verifier-scored live samples.
usage: train_v2.py --name v2a --plan "A,stageA.txt,6,2e-3,0.10;B,stageB.txt,30,8e-4,0.03" [--init ckpt.pt]"""
import argparse, json, math, os, random, re, sys, time
sys.path[:0] = [os.path.dirname(os.path.abspath(__file__)), "/tmp/paperlm", "/tmp/paperlm/data", "/tmp/paperlm/engine", "/tmp/paperlm/model"]
import torch, torch.nn as nn, torch.nn.functional as F
from tokenizers import Tokenizer
from architecture import build
from sampling import generate, pretty
import validator as V, verify as VF
try: import live_status as LS
except Exception: LS = None
ap = argparse.ArgumentParser()
ap.add_argument("--name", required=True); ap.add_argument("--plan", required=True); ap.add_argument("--init", default=""); ap.add_argument("--bs", type=int, default=64); ap.add_argument("--seq", type=int, default=512)
ap.add_argument("--wd", type=float, default=0.1); ap.add_argument("--warmup", type=int, default=100); ap.add_argument("--eval_every", type=int, default=100); ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--data", default="/tmp/paperlm/gold2"); ap.add_argument("--tok", default="/tmp/paperlm/tok/paperlm_tokenizer.json"); ap.add_argument("--out", default="/tmp/paperlm/ckpt2")
ap.add_argument("--live", type=int, default=0, help="1 = publish telemetry to the dashboard"); ap.add_argument("--iter", default="v2"); ap.add_argument("--sample_every", type=int, default=400); ap.add_argument("--ffn", type=int, default=832)
a = ap.parse_args(); torch.manual_seed(a.seed); random.seed(a.seed); torch.set_float32_matmul_precision("high")
dev = "cuda"; tok = Tokenizer.from_file(a.tok); out = f"{a.out}/{a.name}"; os.makedirs(out, exist_ok=True); PAD = 0
enc = lambda p: [x[:a.seq] for x in ([tok.encode(l.rstrip("\n")).ids for l in open(p, encoding="utf-8") if l.strip()])]
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
Xv = pack(enc(f"{a.data}/val.txt"), False).to(dev); Xc = pack(enc(f"{a.data}/val_clean.txt"), False).to(dev)
cfg = dict(vocab_size=tok.get_vocab_size(), dropout=0.1, max_seq=1024, ffn_hidden=a.ffn); model = build(cfg).to(dev)
if a.init: d = torch.load(a.init, map_location=dev); model.load_state_dict(d["model"])
nparams = model.n_params(); cmodel = torch.compile(model)
def set_dropout(p):
    for m in model.modules():
        if isinstance(m, nn.Dropout): m.p = p
        if m.__class__.__name__ == "Attention": m.drop = p
def loss_fn(x, net=None):
    with torch.autocast("cuda", dtype=torch.bfloat16): lg = (net or cmodel)(x[:, :-1])
    return F.cross_entropy(lg.float().reshape(-1, lg.shape[-1]), x[:, 1:].reshape(-1), ignore_index=PAD, reduction="sum"), (x[:, 1:] != PAD).sum()
@torch.no_grad()
def ev(X):
    model.eval(); L = N = 0
    for i in range(0, X.shape[0], 64): l, n = loss_fn(X[i:i + 64]); L += l.item(); N += n.item()
    model.train(); return L / N
PROMPTS = [("NEB", "C12", "physics", "Magnetic field", 1, "MCQ"), ("SEE", "C10", "science", "Heredity", 1, "MCQ"), ("NEB", "C11", "chemistry", "Chemical bonding", 5, "CONCEPTUAL"),
           ("IOE", "IOE", "mathematics", "Calculus", 1, "MCQ"), ("CEE", "CEE", "physics", "Optics", 1, "MCQ"), ("NEB", "C12", "mathematics", "Derivatives", 5, "NUMERICAL")]
def samples():
    items, ok = [], 0
    for (b, l, s, u, m, t) in PROMPTS:
        h = f"<|bos|><|board={b}|><|level={l}|><|subj={s}|><|unit|>{u}<|marks={m}|><|type={t}|><|q|>"
        g = generate(model, tok.encode(h).ids, max_new=300, temperature=0.7, top_p=0.9); txt = h + tok.decode(g, skip_special_tokens=False).replace("Ġ", " ")
        it = VF.parse_schema(txt); good = bool(it) and V.validate_item_text(txt) is None and VF.verify_item(it)["ok"]; ok += good; items.append(("PASS " if good else "FAIL ") + pretty(txt))
    return items, ok / len(PROMPTS)
plan = [p.split(",") for p in a.plan.split(";")]; hist, best_c, t0, seen, step = [], 1e9, time.time(), 0, 0; model.train(); stage_log = []
total_all = 0
for name, f, ep, lr, dr in plan:
    tr = enc(f"{a.data}/{f}"); total_all += math.ceil(pack(tr, True).shape[0] / a.bs) * int(ep)
for si, (name, f, ep, lr, dr) in enumerate(plan):
    ep, lr, dr = int(ep), float(lr), float(dr); tr = enc(f"{a.data}/{f}"); set_dropout(dr)
    spe = math.ceil(pack(tr, True).shape[0] / a.bs); tot = spe * ep; sstep = 0
    decay = [p for n, p in model.named_parameters() if p.dim() >= 2]; nod = [p for n, p in model.named_parameters() if p.dim() < 2]
    opt = torch.optim.AdamW([{"params": decay, "weight_decay": a.wd}, {"params": nod, "weight_decay": 0}], lr=lr, betas=(0.9, 0.95), fused=True)
    lr_at = lambda s: lr * (s + 1) / a.warmup if s < a.warmup else lr * (0.03 + 0.97 * 0.5 * (1 + math.cos(math.pi * (s - a.warmup) / max(1, tot - a.warmup))))
    if LS and a.live: LS.update("stage", name=f"TRAIN {a.iter}", phase=f"stage {name}: {os.path.basename(f)} x{ep} epochs, lr {lr}, dropout {dr}", detail=f"{nparams/1e6:.2f}M params, run {a.name}")
    best_s = 1e9
    for e in range(ep):
        X = pack(tr, True).to(dev)
        for i in range(0, X.shape[0], a.bs):
            xb = X[i:i + a.bs]
            for g in opt.param_groups: g["lr"] = lr_at(sstep)
            l, n = loss_fn(xb); (l / n).backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); opt.zero_grad(set_to_none=True)
            step += 1; sstep += 1; seen += n.item()
            if step % a.eval_every == 0 or sstep == tot:
                vl, vc = ev(Xv), ev(Xc); tl = (l / n).item(); el = time.time() - t0
                hist.append([step, round(tl, 4), round(vc, 4)])
                if vc < best_s: best_s = vc; torch.save(dict(model=model.state_dict(), cfg=model.cfg.__dict__, step=step, val_loss=vl, val_clean=vc, stage=name), f"{out}/best_{name}.pt")
                print(f"[{name}] step {step} ep {e+sstep/spe-e:.2f} train {tl:.4f} val {vl:.4f} clean {vc:.4f} ppl {math.exp(vc):.2f} best_{name} {best_s:.4f} tok/s {seen/el:,.0f}", flush=True)
                if LS and a.live:
                    LS.update(f"train_{a.name}", model=f"PaperLM-Tiny [{a.iter}/{a.name}/{name}]", params=nparams, step=step, total_steps=total_all, epoch=step / spe, train_loss=tl, val_loss=vc, ppl=math.exp(vc), lr=lr_at(sstep), tok_s=seen / el, eta_s=(total_all - step) / (step / el), best_val=best_s, history=hist[-400:], run=a.name)
            if a.live and step % a.sample_every == 0:
                try: it, rate = samples(); LS.update("samples", step=step, items=it, valid_rate=rate, run=a.name)
                except Exception as ex: print("sample err", ex)
                model.train()
    torch.save(dict(model=model.state_dict(), cfg=model.cfg.__dict__, step=step, val_loss=ev(Xv), val_clean=ev(Xc), stage=name), f"{out}/last_{name}.pt")
    stage_log.append(dict(stage=name, best_clean=best_s, last_val=ev(Xv), last_clean=ev(Xc), epochs=ep, lr=lr, dropout=dr))
json.dump(dict(args=vars(a), params=nparams, stages=stage_log, history=hist, seconds=time.time() - t0), open(f"{out}/train_log.json", "w"))
print("DONE", json.dumps(stage_log), flush=True)
