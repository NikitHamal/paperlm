#!/usr/bin/env python3
"""Cross-family verification (MoLab GPU).  The Qwen-based teacher/verifier tiers share blind spots, so every MCQ is re-judged by a
DIFFERENT model family (Mistral-Small-24B).  Checks (all logit-based, no sampling):
  P  4 cyclic option orders, blind: the key TEXT must be the argmax every time (mean p >= PMIN)
  E  entailment: P(Yes | key + explanation correct & consistent) >= EMIN
  D  discrimination: the same explanation attached to the strongest wrong option must get P(Yes) <= DMAX
usage: cross_verify.py MODEL_DIR OUT_DIR  (--bank BANK.json | --jsonl ROWS.jsonl)   [--limit N]
rows = {sk:'NEB|C12|physics', unit, item:{q,o[4],k,w,...}}.  Output OUT_DIR/cross_checked.jsonl (+ cross_summary.json, DONE)."""
import json, sys, os, time, argparse
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

ap = argparse.ArgumentParser(); ap.add_argument("model"); ap.add_argument("out"); ap.add_argument("--bank"); ap.add_argument("--jsonl"); ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--pmin", type=float, default=0.80); ap.add_argument("--emin", type=float, default=0.80); ap.add_argument("--dmax", type=float, default=0.35)
ap.add_argument("--tag", default="cross")
A = ap.parse_args(); os.makedirs(A.out, exist_ok=True); t0 = time.time()
STATUS = f"/tmp/paperlm/status_{A.tag}.json"; LET = "ABCD"
SYS = "You are a meticulous senior examiner and subject expert for Nepali board and entrance exams. You are accurate and strict."
counts = dict(total=0, P=0, E=0, D=0, all=0); prog = dict(done=0, total=1, msg="loading"); last = {"v": None}


def status():
    json.dump(dict(ts=time.time(), elapsed=round(time.time() - t0), counts=counts, last=last["v"], model=os.path.basename(A.model), **prog), open(STATUS + ".tmp", "w")); os.replace(STATUS + ".tmp", STATUS)


status()
rows = []
if A.bank:
    b = json.load(open(A.bank))
    for sk, us in b["seeds"].items():
        for u, its in us.items():
            for it in its:
                if it.get("c") == "mcq" and len(it.get("o") or []) == 4 and it.get("k") in "abcd" and it.get("w"): rows.append(dict(sk=sk, unit=u, item=it))
else:
    rows = [json.loads(l) for l in open(A.jsonl)]
if A.limit: rows = rows[:A.limit]
counts["total"] = len(rows)
tok = AutoTokenizer.from_pretrained(A.model); tok.padding_side = "left"
if tok.pad_token_id is None: tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(A.model, dtype=torch.bfloat16, device_map="cuda"); model.eval()


def first(s):
    ids = tok.encode(s, add_special_tokens=False); return ids[-1] if len(ids) == 1 else ids[0]


LID = [first(c) for c in LET]; YN = [first("Yes"), first("No")]


def chat(u):
    return tok.apply_chat_template([{"role": "system", "content": SYS}, {"role": "user", "content": u}], tokenize=False, add_generation_prompt=True)


def ctx_of(r): b, l, s = r["sk"].split("|"); return f"Subject: {s} ({b} {l}), unit: {r['unit']}"


def mcq_prompt(r, order):
    it = r["item"]; opts = "\n".join(f"{LET[j]}. {it['o'][i]}" for j, i in enumerate(order))
    return chat(f"{ctx_of(r)}\n\nQuestion: {it['q']}\n{opts}\n\nWhich option is correct? Reply with only the letter.")


def ent_prompt(r, idx):
    it = r["item"]; opts = "\n".join(f"{LET[j]}. {o}" for j, o in enumerate(it["o"]))
    return chat(f"{ctx_of(r)}\n\nQuestion: {it['q']}\n{opts}\n\nProposed correct answer: {LET[idx]}. {it['o'][idx]}\nProposed explanation: {it['w']}\n\n"
                "Is the proposed answer truly correct, AND is the explanation factually correct, consistent with that answer, and free of contradictions? Reply Yes or No.")


@torch.no_grad()
def last_logits(prompts, ids, bs=48, tag=""):
    order = sorted(range(len(prompts)), key=lambda i: len(prompts[i])); outs = [None] * len(prompts)
    for s in range(0, len(prompts), bs):
        idx = order[s:s + bs]
        enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        lg = model(**enc, logits_to_keep=1).logits[:, -1].float()[:, ids]
        for i, p in zip(idx, torch.softmax(lg, -1).cpu().tolist()): outs[i] = p
        prog.update(msg=f"{tag} {min(s + bs, len(prompts))}/{len(prompts)}"); status()
    return outs


for r in rows: r["chk"] = {}; r["_k"] = LET.index(r["item"]["k"].upper())
orders = [[(j + sft) % 4 for j in range(4)] for sft in range(4)]
prog.update(total=len(rows) * 3, done=0); status()
pr = last_logits([mcq_prompt(r, o) for r in rows for o in orders], LID, tag="P")
for i, r in enumerate(rows):
    ps = []
    for j, o in enumerate(orders):
        p = pr[i * 4 + j]; pk = o.index(r["_k"]); ps.append((max(range(4), key=lambda x: p[x]) == pk, p[pk]))
    mean = sum(p for _, p in ps) / 4; r["chk"]["P"] = all(a for a, _ in ps) and mean >= A.pmin; r["chk"]["Pmean"] = round(mean, 3); counts["P"] += r["chk"]["P"]
    p0 = pr[i * 4]; r["_w"] = max((x for x in range(4) if x != r["_k"]), key=lambda x: p0[x])
prog.update(done=len(rows)); status()
ent = last_logits([ent_prompt(r, r["_k"]) for r in rows], YN, tag="E")
for r, e in zip(rows, ent): r["chk"]["E"] = e[0] >= A.emin; r["chk"]["Ep"] = round(e[0], 3); counts["E"] += r["chk"]["E"]
prog.update(done=len(rows) * 2); status()
dis = last_logits([ent_prompt(r, r["_w"]) for r in rows], YN, tag="D")
for r, d in zip(rows, dis): r["chk"]["D"] = d[0] <= A.dmax; r["chk"]["Dp"] = round(d[0], 3); counts["D"] += r["chk"]["D"]
for r in rows:
    c = r["chk"]; r["xpass"] = bool(c["P"] and c["E"] and c["D"]); counts["all"] += r["xpass"]; r.pop("_k"); r.pop("_w")
    if r["xpass"]:
        it = r["item"]; last["v"] = f"[{r['sk']} | {r['unit']}]\n{it['q']}\n" + "\n".join(f"{LET[j]}. {o}" for j, o in enumerate(it["o"])) + f"\nkey {it['k'].upper()} — {it['w']}"
with open(os.path.join(A.out, "cross_checked.jsonl"), "w") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
json.dump(counts, open(os.path.join(A.out, "cross_summary.json"), "w"), indent=1)
prog.update(done=len(rows) * 3, msg="done"); status(); open(os.path.join(A.out, "DONE"), "w").write(json.dumps(counts)); print(counts)
