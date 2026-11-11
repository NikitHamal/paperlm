#!/usr/bin/env python3
"""LLM-judge audit of the gold bank (runs on the MoLab GPU).

Stage 1 (all items, one forward pass each, no sampling):
  * MCQ: the judge answers the question WITHOUT seeing the key -> P(A..D); agreement with the stored key.
  * Written (with model answer): P(Yes) to "is this model answer correct, complete and responsive?".
Stage 2 (MCQ disagreements only): chain-of-thought re-solve (greedy) -> final letter.
Outputs: <out>/judge_stage1.jsonl, <out>/judge_stage2.jsonl, status json for the live dashboard.
usage: judge_bank.py MODEL_DIR BANK_JSON OUT_DIR [limit]
"""
import json, sys, os, time, re, math
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL, BANK, OUT = sys.argv[1:4]
LIMIT = int(sys.argv[4]) if len(sys.argv) > 4 else 0
STATUS = os.environ.get("JUDGE_STATUS", "/tmp/paperlm/status_judge.json")
os.makedirs(OUT, exist_ok=True)
t0 = time.time()


def status(**kw):
    kw["ts"] = time.time(); kw["elapsed"] = round(time.time() - t0)
    json.dump(kw, open(STATUS + ".tmp", "w")); os.replace(STATUS + ".tmp", STATUS)


tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
status(stage="loading", msg="loading judge model")
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda"); model.eval()
status(stage="loaded", msg="model on GPU", mem_gb=round(torch.cuda.memory_allocated() / 1e9, 1))

bank = json.load(open(BANK))
items = []
for sk, units in bank["seeds"].items():
    b, lv, subj = sk.split("|")
    for un, lst in units.items():
        for i, it in enumerate(lst):
            items.append(dict(id=f"{sk}#{un}#{i}", board=b, level=lv, subject=subj, unit=un, it=it))
if LIMIT: items = items[::max(1, len(items) // LIMIT)][:LIMIT]

SYS = "You are a meticulous senior examiner and subject expert for Nepali board and entrance exams (SEE, NEB, IOE, CEE, TU, CTEVT). You are accurate and strict."
LET = "ABCD"


def chat(user, prefix=""):
    return tok.apply_chat_template([{"role": "system", "content": SYS}, {"role": "user", "content": user}], tokenize=False, add_generation_prompt=True) + prefix


def mcq_prompt(r):
    it = r["it"]
    opts = "\n".join(f"{LET[j]}. {o}" for j, o in enumerate(it["o"]))
    return f"Subject: {r['subject']} ({r['board']} {r['level']}), unit: {r['unit']}\n\nQuestion: {it['q']}\n{opts}\n\nWhich option is correct? Reply with only the letter."


def mcq_cot_prompt(r):
    it = r["it"]
    opts = "\n".join(f"{LET[j]}. {o}" for j, o in enumerate(it["o"]))
    return (f"Subject: {r['subject']} ({r['board']} {r['level']}), unit: {r['unit']}\n\nQuestion: {it['q']}\n{opts}\n\n"
            "Solve step by step, carefully checking any arithmetic, then end with a final line exactly of the form 'Answer: X' where X is A, B, C or D.")


def written_prompt(r):
    it = r["it"]
    q = it["q"] or ""
    if it.get("p"): q = (q + "\n" if q else "") + "\n".join(f"({p[0]}) {p[1]}" for p in it["p"])
    return (f"Subject: {r['subject']} ({r['board']} {r['level']}), unit: {r['unit']}, marks: {it['m']}\n\nQuestion: {q}\n\nModel answer: {it['r']}\n\n"
            "Is the model answer factually and mathematically correct, free of contradictions, and does it properly answer the question as asked? Reply with only Yes or No.")


def ids_for(words):
    out = []
    for w in words:
        t = tok.encode(w, add_special_tokens=False); out.append(t[0])
    return out


LID = ids_for(list(LET)); YES, NO = ids_for(["Yes"])[0], ids_for(["No"])[0]


@torch.no_grad()
def next_logits(prompts, budget=48000):
    enc = [tok(p, add_special_tokens=False)["input_ids"] for p in prompts]
    order = sorted(range(len(enc)), key=lambda i: len(enc[i]))
    res = [None] * len(enc); i = 0
    while i < len(order):
        L = len(enc[order[i]]); j = i
        while j < len(order) and (j - i + 1) * len(enc[order[j]]) <= budget and j - i < 128: j += 1
        j = max(j, i + 1); idx = order[i:j]; ml = max(len(enc[k]) for k in idx)
        ids = torch.full((len(idx), ml), tok.pad_token_id); att = torch.zeros((len(idx), ml), dtype=torch.long)
        for r, k in enumerate(idx):
            ids[r, ml - len(enc[k]):] = torch.tensor(enc[k]); att[r, ml - len(enc[k]):] = 1
        lg = model(input_ids=ids.cuda(), attention_mask=att.cuda(), logits_to_keep=1).logits[:, -1].float()
        lp = torch.log_softmax(lg, -1).cpu()
        for r, k in enumerate(idx): res[k] = lp[r]
        i = j
    return res


# ---------- stage 1
mc = [r for r in items if r["it"]["c"] == "mcq" and len(r["it"].get("o", [])) == 4]
wr = [r for r in items if r["it"]["c"] != "mcq" and (r["it"].get("r") or "").strip()]
status(stage="stage1", msg=f"judging {len(mc)} MCQ + {len(wr)} written", total=len(mc) + len(wr), done=0)
f1 = open(os.path.join(OUT, "judge_stage1.jsonl"), "w"); done = 0
CH = 1024
for s in range(0, len(mc), CH):
    chunk = mc[s:s + CH]; lps = next_logits([chat(mcq_prompt(r)) for r in chunk])
    for r, lp in zip(chunk, lps):
        v = lp[LID]; p = torch.softmax(v, -1).tolist(); pred = LET[int(torch.tensor(p).argmax())]
        key = r["it"]["k"].upper()
        f1.write(json.dumps(dict(id=r["id"], kind="mcq", pred=pred, key=key, agree=pred == key, p_key=p[LET.index(key)] if key in LET else 0, p_pred=max(p))) + "\n")
    f1.flush(); done += len(chunk); status(stage="stage1", msg="MCQ solve", total=len(mc) + len(wr), done=done)
for s in range(0, len(wr), CH):
    chunk = wr[s:s + CH]; lps = next_logits([chat(written_prompt(r)) for r in chunk], budget=40000)
    for r, lp in zip(chunk, lps):
        y, n = lp[YES].item(), lp[NO].item(); p_yes = math.exp(y) / (math.exp(y) + math.exp(n))
        f1.write(json.dumps(dict(id=r["id"], kind="written", c=r["it"]["c"], t=r["it"]["t"], p_yes=p_yes)) + "\n")
    f1.flush(); done += len(chunk); status(stage="stage1", msg="written judge", total=len(mc) + len(wr), done=done)
f1.close()

# ---------- stage 2: CoT re-solve of MCQ disagreements
dis = []
for l in open(os.path.join(OUT, "judge_stage1.jsonl")):
    d = json.loads(l)
    if d["kind"] == "mcq" and (not d["agree"] or d["p_key"] < 0.5): dis.append(d["id"])
byid = {r["id"]: r for r in items}
status(stage="stage2", msg=f"CoT re-solving {len(dis)} disagreements", total=len(dis), done=0)
f2 = open(os.path.join(OUT, "judge_stage2.jsonl"), "w"); BS = 96; done = 0
tok.padding_side = "left"
for s in range(0, len(dis), BS):
    ids_ = dis[s:s + BS]; prompts = [chat(mcq_cot_prompt(byid[i])) for i in ids_]
    enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
    with torch.no_grad(): out = model.generate(**enc, max_new_tokens=700, do_sample=False, pad_token_id=tok.pad_token_id)
    txt = tok.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    for i, t in zip(ids_, txt):
        m = re.findall(r"Answer:\s*\**\s*\(?([ABCD])\b", t)
        pred = m[-1] if m else None; key = byid[i]["it"]["k"].upper()
        f2.write(json.dumps(dict(id=i, cot_pred=pred, key=key, agree=pred == key, tail=t[-300:])) + "\n")
    f2.flush(); done += len(ids_); status(stage="stage2", msg="CoT re-solve", total=len(dis), done=done)
f2.close()
status(stage="done", msg="judge audit complete", total=len(dis), done=len(dis))
open(os.path.join(OUT, "DONE"), "w").write("ok")
