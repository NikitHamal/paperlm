"""PaperLM Semantic Verifier: a small char-level cross-encoder that scores how well an item is supported by a concept anchor.

Why: the lexical grounding gate cannot tell a grammatical nonsense sentence from a real exam item.  This verifier is trained
on the contrast that matters — verified items (computed by the parametric engine, projected from the closed-world fact
tables, or taken from the audited gold bank) versus the *hard* negatives that the lexical gate lets through (rejection
sampling candidates from the 10M model) and mismatched anchor/item pairs.  It is used as the semantic gate of the
experimental neural tier and as the reward for rejection fine-tuning.

    python3 model/verifier.py train --data /tmp/paperlm/vf --out /tmp/paperlm/vf/verifier.pt
    python3 model/verifier.py eval  --data /tmp/paperlm/vf --ckpt /tmp/paperlm/vf/verifier.pt
    python3 model/verifier.py score --ckpt ... --anchor "..." --text "..."
"""
import argparse
import json
import math
import os
import random
import sys
import time

import torch
import torch.nn as nn


class Verifier(nn.Module):
    def __init__(self, vocab=256, d=256, layers=4, heads=8, ffn=1024, max_len=768, dropout=0.1):
        super().__init__()
        self.emb = nn.Embedding(vocab, d)
        self.pos = nn.Embedding(max_len, d)
        enc = nn.TransformerEncoderLayer(d, heads, ffn, dropout, batch_first=True, norm_first=True, activation="gelu")
        self.enc = nn.TransformerEncoder(enc, layers)
        self.head = nn.Sequential(nn.LayerNorm(d), nn.Linear(d, d), nn.GELU(), nn.Linear(d, 1))
        self.max_len = max_len

    def forward(self, ids):
        n = ids.shape[1]
        h = self.emb(ids) + self.pos(torch.arange(n, device=ids.device))[None]
        mask = ids.eq(0)
        h = self.enc(h, src_key_padding_mask=mask)
        m = (~mask).float().unsqueeze(-1)
        pooled = (h * m).sum(1) / m.sum(1).clamp(min=1)
        return self.head(pooled).squeeze(-1)


def encode(anchor, text, max_len=768):
    s = (str(anchor) + "  [[SEP]]  " + str(text))[:max_len]
    ids = [max(1, min(255, ord(c))) for c in s]  # byte-ish char ids, 0 reserved for padding
    return ids


def collate(batch, max_len=768):
    L = min(max_len, max(len(x[0]) for x in batch))
    out = torch.zeros(len(batch), L, dtype=torch.long)
    for i, (ids, _y) in enumerate(batch):
        ids = ids[:L]
        out[i, :len(ids)] = torch.tensor(ids, dtype=torch.long)
    y = torch.tensor([float(x[1]) for x in batch])
    return out, y


def load_pairs(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            rows.append((encode(r["anchor"], r["text"]), int(r["label"])))
    return rows


def train(a):
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tr = load_pairs(os.path.join(a.data, "train.jsonl"))
    va = load_pairs(os.path.join(a.data, "val.jsonl"))
    random.Random(0).shuffle(tr)
    m = Verifier().to(dev)
    n_par = sum(p.numel() for p in m.parameters())
    print(f"verifier {n_par/1e6:.2f}M params, {len(tr)} train / {len(va)} val pairs", flush=True)
    opt = torch.optim.AdamW(m.parameters(), lr=3e-4, weight_decay=0.01)
    steps = math.ceil(len(tr) / a.batch) * a.epochs
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, 3e-4, total_steps=steps, pct_start=0.1)
    lossf = nn.BCEWithLogitsLoss()
    best = 0.0
    os.makedirs(a.out, exist_ok=True)
    log = open(os.path.join(a.out, "verifier_log.jsonl"), "a")
    for ep in range(a.epochs):
        m.train()
        t0 = time.time(); tot = 0.0; nb = 0
        for i in range(0, len(tr), a.batch):
            ids, y = collate(tr[i:i + a.batch])
            ids, y = ids.to(dev), y.to(dev)
            opt.zero_grad()
            loss = lossf(m(ids), y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0)
            opt.step(); sched.step()
            tot += float(loss); nb += 1
            if nb % 50 == 0:
                rec = dict(step=nb, epoch=ep, loss=round(tot / nb, 4), lr=sched.get_last_lr()[0])
                print(json.dumps(rec), flush=True); log.write(json.dumps(rec) + "\n"); log.flush()
        auc, acc, prec = evaluate(m, va, dev)
        rec = dict(event="epoch", epoch=ep, loss=round(tot / max(1, nb), 4), val_auc=round(auc, 4), val_acc=round(acc, 4),
                   val_precision=round(prec, 4), seconds=round(time.time() - t0, 1))
        print(json.dumps(rec), flush=True); log.write(json.dumps(rec) + "\n"); log.flush()
        if auc >= best:
            best = auc
            torch.save(dict(model=m.state_dict(), cfg=dict(vocab=256, d=256, layers=4, heads=8, ffn=1024), auc=auc), os.path.join(a.out, "verifier.pt"))
    print(json.dumps(dict(event="done", best_val_auc=round(best, 4))), flush=True)


@torch.no_grad()
def scores(m, rows, dev, batch=128):
    m.eval(); out = []
    for i in range(0, len(rows), batch):
        ids, _ = collate(rows[i:i + batch])
        out += torch.sigmoid(m(ids.to(dev))).cpu().tolist()
    return out


def evaluate(m, rows, dev):
    s = scores(m, rows, dev)
    y = [r[1] for r in rows]
    pos = [x for x, t in zip(s, y) if t == 1]; neg = [x for x, t in zip(s, y) if t == 0]
    auc = 0.0
    if pos and neg:
        # rank-based AUC (no sklearn dependency)
        allv = sorted([(v, t) for v, t in zip(s, y)])
        r = 1; ranks = {}
        i = 0
        while i < len(allv):
            j = i
            while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
                j += 1
            for k in range(i, j + 1):
                ranks[k] = (i + j) / 2 + 1
            i = j + 1
        rp = sum(ranks[k] for k, (v, t) in enumerate(allv) if t == 1)
        auc = (rp - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))
    acc = sum(1 for x, t in zip(s, y) if (x >= 0.5) == (t == 1)) / max(1, len(y))
    prec = sum(1 for x, t in zip(s, y) if x >= 0.5 and t == 1) / max(1, sum(1 for x in s if x >= 0.5))
    return auc, acc, prec


def load(ckpt, dev=None):
    dev = dev or ("cuda" if torch.cuda.is_available() else "cpu")
    d = torch.load(ckpt, map_location=dev)
    m = Verifier(**{k: v for k, v in d["cfg"].items() if k != "vocab"}).to(dev)
    m.load_state_dict(d["model"]); m.eval()
    return m, dev


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("--data", default="/tmp/paperlm/vf")
    ap.add_argument("--ckpt", default="/tmp/paperlm/vf/verifier.pt"); ap.add_argument("--out", default="/tmp/paperlm/vf")
    ap.add_argument("--epochs", type=int, default=3); ap.add_argument("--batch", type=int, default=96)
    ap.add_argument("--anchor", default=""); ap.add_argument("--text", default="")
    a = ap.parse_args()
    if a.mode == "train":
        train(a)
    elif a.mode == "eval":
        m, dev = load(a.ckpt)
        va = load_pairs(os.path.join(a.data, "val.jsonl"))
        auc, acc, prec = evaluate(m, va, dev)
        print(json.dumps(dict(val_auc=round(auc, 4), val_acc=round(acc, 4), val_precision=round(prec, 4))))
    else:
        m, dev = load(a.ckpt)
        with torch.no_grad():
            x = torch.tensor([encode(a.anchor, a.text)], device=dev)
            print(json.dumps(dict(score=round(float(torch.sigmoid(m(x))[0]), 4))))
