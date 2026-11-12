#!/usr/bin/env python3
"""Specialist ~10M pack: subject-pure 4096-BPE -> answer-first concept-conditioned SFT -> contrastive (DPO) rejection tuning -> best-of-K grounded bench -> INT8 ONNX.
usage: train_pack.py <pack_id> [steps_a] [steps_b] [dpo_steps]"""
import copy, hashlib, json, math, os, random, re, sys, time, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, "..", "..", "model"), "/work/paperlm/model"]
import torch, torch.nn.functional as F, numpy as np
from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders, Regex, normalizers
from architecture import PaperLM, PaperLMConfig
import export as EX, fsm
pid = sys.argv[1]; SA, SB, SD = [int(x) for x in (sys.argv[2:5] + ["2500", "3500", "400"][len(sys.argv[2:5]):])]
SPECS = json.load(open(os.path.join(HERE, "..", "pack_specs.json"))); S = SPECS[pid]; D = f"/tmp/packs/{pid}"; O = f"{D}/out"; os.makedirs(O, exist_ok=True)
random.seed(3); torch.manual_seed(3); dev = "cuda"; PAT = r" ?\\[A-Za-z]+| ?[A-Za-z\u0900-\u097F]+| ?[0-9]| ?[^\sA-Za-z0-9\u0900-\u097F]|\s+"
rd = lambda p: [json.loads(l) for l in open(p)] if os.path.exists(p) else []
items = rd(f"{D}/gold_items.jsonl") + rd(f"{D}/verified.jsonl"); graph = json.load(open(f"{D}/syllabus_graph.json")); UT = {u["name"]: set(u["terms"]) for u in graph["units"]}
isval = lambda it: int(hashlib.md5(it["anchor"].encode()).hexdigest(), 16) % 100 < 6
tr_items, va_items = [i for i in items if not isval(i)], [i for i in items if isval(i)]
prompt = lambda it: f"<|bos|><|pack={pid}|><|type={it['type']}|><|marks={it['marks']}|><|unit|>{it['unit']}<|book|>{it['anchor']}<|ans|>"
def comp(it, ds=None):
    if it["type"] == "mcq": d = ds or it["distractors"]; return f"{it['answer']}<|q|>{it['question']}<|d|>{d[0]}<|d|>{d[1]}<|d|>{d[2]}<|why|>{it['why']}<|end|>"
    return f"{it['answer']}<|q|>{it['question']}<|end|>"
# ---------------- subject-pure tokenizer
specials = fsm.STRUCT + [f"<|pack={pid}|>", "<|type=mcq|>", "<|type=short|>"] + [f"<|marks={m}|>" for m in range(1, 6)]
book = [l.rstrip("\n") for l in open(f"{D}/book_lm.txt")]
corpus = book + [prompt(i) + comp(i) for i in tr_items]; open(f"{D}/tok_corpus.txt", "w").write("\n".join(corpus))
tok = Tokenizer(models.BPE(unk_token=None)); tok.normalizer = normalizers.NFC()
tok.pre_tokenizer = pre_tokenizers.Sequence([pre_tokenizers.Split(Regex(PAT), behavior="isolated", invert=False), pre_tokenizers.ByteLevel(add_prefix_space=False, use_regex=False)]); tok.decoder = decoders.ByteLevel()
tok.train([f"{D}/tok_corpus.txt"], trainers.BpeTrainer(vocab_size=4096, special_tokens=specials, initial_alphabet=pre_tokenizers.ByteLevel.alphabet(), min_frequency=2, show_progress=False))
tok.save(f"{O}/tokenizer.json"); T = fsm.tok_tables(tok); SP = T["special"]; enc = lambda s: tok.encode(s).ids
cfg = PaperLMConfig(vocab_size=4096, d_model=320, n_layers=7, n_heads=5, ffn_hidden=896, max_seq=768, dropout=0.1); model = PaperLM(cfg).to(dev); NP = model.n_params(); print(pid, "params", NP, flush=True)
def mk(it, ds=None): p, c = enc(prompt(it)), enc(comp(it, ds)); return p, c
def mcq_variants(it):
    vs = [None]
    if it["type"] == "mcq": vs += [random.sample(it["distractors"], 3) for _ in range(2)]
    return [mk(it, v) for v in vs]
TR = [v for it in tr_items for v in mcq_variants(it)]; VA = [mk(i) for i in va_items]
BK = []
for l in book:
    ids = enc(l); BK += [ids[i:i + 500] for i in range(0, len(ids), 450) if len(ids[i:i + 500]) > 40]
def collate(rows, pw=0.2):  # rows: (prompt_ids, comp_ids) or plain list (book LM)
    xs, ws = [], []
    for r in rows:
        p, c = (r if isinstance(r, tuple) else ([], r)); x = (p + c)[:640]; w = ([pw] * len(p) + [1.0] * len(c))[:640]; xs.append(x); ws.append(w)
    L = max(map(len, xs)); X = torch.zeros(len(xs), L, dtype=torch.long); W = torch.zeros(len(xs), L)
    for i, (x, w) in enumerate(zip(xs, ws)): X[i, :len(x)] = torch.tensor(x); W[i, :len(w)] = torch.tensor(w)
    return X.to(dev), W.to(dev)
def nll(m, X, W):
    with torch.autocast("cuda", dtype=torch.bfloat16): lg = m(X[:, :-1])
    ce = F.cross_entropy(lg.float().reshape(-1, lg.shape[-1]), X[:, 1:].reshape(-1), reduction="none").view(X.shape[0], -1); w = W[:, 1:]; return (ce * w).sum() / w.sum().clamp(min=1)
@torch.no_grad()
def vloss(m):
    m.eval(); m.return_cache = False; L = 0; N = 0
    for i in range(0, len(VA), 64): X, W = collate(VA[i:i + 64], 0.0); n = W[:, 1:].sum().item(); L += nll(m, X, W).item() * n; N += n
    m.train(); return L / max(N, 1)
def st(**kw):
    try: json.dump(dict(pack=pid, t=time.time(), params=NP, **kw), open(f"/tmp/paperlm/status_train_{pid}.json", "w"))
    except Exception: pass
curve = []
def train(steps, pool, lr, tag, bs=48):
    opt = torch.optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.95), weight_decay=0.1); model.train(); model.return_cache = False; t0 = time.time()
    for s in range(steps):
        cur = lr * min(1, (s + 1) / 100) * (0.05 + 0.95 * 0.5 * (1 + math.cos(math.pi * s / steps)))
        for g in opt.param_groups: g["lr"] = cur
        X, W = collate(random.sample(pool, bs)); loss = nll(model, X, W); opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        if s % 250 == 0 or s == steps - 1:
            v = vloss(model); curve.append(dict(stage=tag, step=s, train=round(loss.item(), 4), val=round(v, 4))); print(tag, s, round(loss.item(), 3), "val", round(v, 3), flush=True); st(stage=tag, step=s, steps=steps, curve=curve, elapsed=round(time.time() - t0))
train(SA, TR + [(r if False else r) for r in BK] * 1, 2e-3, "A-lm+items"); train(SB, TR, 8e-4, "B-items")
# ---------------- contrastive rejection tuning (DPO with RPO NLL anchor); negatives = ungrounded / mismatched / duplicated
def corrupt(it):
    o = random.choice([x for x in tr_items if x["type"] == it["type"] and x["unit"] != it["unit"]] or tr_items); r = dict(it); k = random.random()
    if it["type"] == "mcq" and k < 0.3: r["distractors"] = [it["answer"]] + it["distractors"][1:]            # key duplicated among distractors
    elif k < 0.65: r["answer"] = o["answer"]                                                              # ungrounded / mismatched key
    else: r["question"] = o["question"]; r["answer"] = o["answer"] if it["type"] == "short" else it["answer"]  # off-topic question
    return r
def lps(m, X, W):
    with torch.autocast("cuda", dtype=torch.bfloat16): lg = m(X[:, :-1])
    lp = torch.log_softmax(lg.float(), -1).gather(-1, X[:, 1:, None])[..., 0]; return (lp * (W[:, 1:] > 0.5)).sum(1)
def bench(m, n=90, K=4, tag=""):
    m.eval(); rows = []; r = random.Random(11); S_ = r.sample(va_items, min(n, len(va_items))); ok = strict = 0; sc_all = []; samples = []
    for it in S_:
        a = it["anchor"]; kind = it["type"]; out = fsm.sample(m, T, enc(prompt(it)), kind, K=K, anchor_ids=enc(a), beta=1.0)
        best = max(out, key=lambda o: (o[2], fsm.grounding(o[0], kind, a, UT.get(it["unit"], ()))[0] + 0.02 * o[1])); sc, f = fsm.grounding(best[0], kind, a, UT.get(it["unit"], ()))
        ok += best[2]; sc_all.append(sc); gate = sc >= 0.85 and (kind == "short" or (f["distinct"] and f["homog"] and f["ans_ground"] >= 0.8)); strict += gate
        if len(samples) < 14: samples.append(dict(unit=it["unit"], type=kind, anchor=a, segs=best[0], score=round(sc, 3), gate=bool(gate)))
    return dict(tag=tag, n=len(S_), complete=ok / len(S_), mean_grounding=float(np.mean(sc_all)), strict_gate_rate=strict / len(S_)), samples
b0, s0 = bench(model, tag="sft"); print(b0, flush=True); st(stage="bench_sft", curve=curve, bench=b0)
sft_sd = copy.deepcopy(model.state_dict()); ref = copy.deepcopy(model).eval(); [p.requires_grad_(False) for p in ref.parameters()]
opt = torch.optim.AdamW(model.parameters(), lr=3e-5, weight_decay=0.0); model.train(); model.return_cache = False; ref.return_cache = False
for s in range(SD):
    its = random.sample(tr_items, 24); Xc, Wc = collate([mk(i) for i in its]); Xr, Wr = collate([mk(corrupt(i)) for i in its]); L = max(Xc.shape[1], Xr.shape[1])
    pad = lambda X: F.pad(X, (0, L - X.shape[1])); Xc, Xr, Wc, Wr = pad(Xc), pad(Xr), pad(Wc), pad(Wr)
    pc, pr = lps(model, Xc, Wc), lps(model, Xr, Wr)
    with torch.no_grad(): rc, rr = lps(ref, Xc, Wc), lps(ref, Xr, Wr)
    dpo = -F.logsigmoid(0.15 * ((pc - rc) - (pr - rr))).mean(); loss = dpo + 0.5 * nll(model, Xc, Wc)
    opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
    if s % 100 == 0: print("dpo", s, round(dpo.item(), 4), flush=True); st(stage="dpo", step=s, steps=SD, dpo=round(dpo.item(), 4), curve=curve, bench=b0)
b1, s1 = bench(model, tag="sft+dpo"); print(b1, flush=True)
use_dpo = b1["strict_gate_rate"] + 0.5 * b1["mean_grounding"] >= b0["strict_gate_rate"] + 0.5 * b0["mean_grounding"] and vloss(model) < vloss_sft if False else b1["strict_gate_rate"] + 0.5 * b1["mean_grounding"] >= b0["strict_gate_rate"] + 0.5 * b0["mean_grounding"]
if not use_dpo: model.load_state_dict(sft_sd)
final, samples = (b1, s1) if use_dpo else (b0, s0); vfin = vloss(model)
# ---------------- INT8 ONNX export (KV-cache graph; Web ORT + Android ORT-mobile; opset 17)
sd = copy.deepcopy(model.state_dict()); m2 = PaperLM(cfg).to(dev); m2.load_state_dict(sd); q = EX.quantize(m2.eval()); w = EX.Wrap(q).cpu().eval(); L_, H, Dh = cfg.n_layers, cfg.n_heads, cfg.d_model // cfg.n_heads
ids = torch.randint(5, 100, (1, 7)); pk = torch.randn(L_, 1, H, 5, Dh) * .1; pv = torch.randn(L_, 1, H, 5, Dh) * .1
torch.onnx.export(w, (ids, pk, pv), f"{O}/model.onnx", input_names=["ids", "past_k", "past_v"], output_names=["logits", "present_k", "present_v"], dynamic_axes={"ids": {1: "S"}, "past_k": {3: "P"}, "past_v": {3: "P"}, "present_k": {3: "T"}, "present_v": {3: "T"}}, opset_version=17, do_constant_folding=False, dynamo=False)
import onnxruntime as ort
s_ = ort.InferenceSession(f"{O}/model.onnx", providers=["CPUExecutionProvider"]); lo = s_.run(None, {"ids": ids.numpy(), "past_k": pk.numpy(), "past_v": pv.numpy()})[0]
with torch.no_grad(): tl = w(ids, pk, pv)[0].numpy()
mb = round(os.path.getsize(f"{O}/model.onnx") / 1e6, 2); rep = dict(pack=pid, params=NP, onnx_int8_mb=mb, vocab=4096, val_loss=round(vfin, 4), ppl=round(math.exp(vfin), 2), onnx_maxdiff=float(np.abs(lo - tl).max()), used_dpo=bool(use_dpo),
           bench_sft=b0, bench_final=final, bench_dpo=b1, n_train_items=len(tr_items), n_val_items=len(va_items), n_gold=sum(1 for i in tr_items if "aid" not in i), n_teacher=sum(1 for i in tr_items if "aid" in i or "facts" in i), curve=curve)
json.dump(rep, open(f"{O}/train_report.json", "w"), indent=1); json.dump(samples, open(f"{O}/samples.json", "w"), indent=1, ensure_ascii=False)
json.dump(dict(pack_id=pid, title=S["title"], level=S["level"], subject=S["subject"], params=NP, onnx_mb=mb, vocab=4096, layers=L_, heads=H, head_dim=Dh, max_seq=cfg.max_seq, specials={k: v for k, v in SP.items()}, fsm=fsm.SPEC, beta=1.0, val_loss=round(vfin, 4), bench=final), open(f"{O}/pack.json", "w"), ensure_ascii=False)
os.system(f"cp {D}/syllabus_graph.json {O}/"); st(stage="done", curve=curve, bench=final, params=NP, mb=mb); print("DONE", pid, NP, mb, final, flush=True)
