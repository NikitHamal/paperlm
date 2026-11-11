#!/usr/bin/env python3
"""Teacher generation with independent verification (MoLab GPU).

For every syllabus unit that is thin in the audited bank, a 32B teacher writes board-style MCQs.  A candidate is kept ONLY if:
  1. it is structurally clean (4 distinct non-trivial options, key in range, no 'all/none of the above', explanation present),
  2. an independent BLIND solve (the model does not see the key) picks the written key with P >= P_MIN,
  3. for numeric/computational stems a chain-of-thought re-solve ALSO lands on the key,
  4. it is not a near-duplicate of an existing bank item or of another candidate.
usage: teacher_gen.py MODEL_DIR BANK_JSON CATALOG_JSON OUT_DIR [per_unit] [rounds]
"""
import json, sys, os, re, time, random
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL, BANK, CATALOG, OUT = sys.argv[1:5]
PER = int(sys.argv[5]) if len(sys.argv) > 5 else 8
ROUNDS = int(sys.argv[6]) if len(sys.argv) > 6 else 1
TARGET = int(os.environ.get("TARGET_MCQ", 12)); P_MIN = float(os.environ.get("P_MIN", 0.80))
STATUS = "/tmp/paperlm/status_gen.json"; os.makedirs(OUT, exist_ok=True); t0 = time.time(); SEED = int(os.environ.get("SEED", 11)); random.seed(SEED); torch.manual_seed(SEED)
counts = {"generated": 0, "parsed": 0, "structural_ok": 0, "blind_ok": 0, "cot_ok": 0, "kept": 0, "dup": 0}
last = {"v": None}; prog = {"done": 0, "total": 1, "msg": "loading"}


def status():
    json.dump(dict(ts=time.time(), elapsed=round(time.time() - t0), counts=counts, last=last["v"], **prog), open(STATUS + ".tmp", "w")); os.replace(STATUS + ".tmp", STATUS)


status()
tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda"); model.eval()
bank = json.load(open(BANK)); cat = json.load(open(CATALOG))
SYS = "You are a meticulous senior examiner and subject expert for Nepali board and entrance exams (SEE, NEB, IOE, CEE, TU, CTEVT). You are accurate and strict."
LET = "ABCD"
SKIP = re.compile(r"english|nepali|literature", re.I)


def chat(u, prefix=""):
    return tok.apply_chat_template([{"role": "system", "content": SYS}, {"role": "user", "content": u}], tokenize=False, add_generation_prompt=True) + prefix


def norm(s): return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def jac(a, b):
    A, B = set(norm(a).split()), set(norm(b).split())
    return len(A & B) / max(1, len(A | B))


units = []
for e in cat.values():
    for subj, sv in e["subjects"].items():
        if SKIP.search(subj): continue
        sk = f"{e['board']}|{e['level']}|{subj}"
        for u in sv["units"]:
            ex = [it for it in bank["seeds"].get(sk, {}).get(u, []) if it["c"] == "mcq"]
            if len(ex) < TARGET: units.append(dict(sk=sk, board=e["board"], level=e["level"], subject=subj, unit=u, existing=[x["q"] for x in ex], need=min(PER, TARGET - len(ex) + 2)))
print("units to fill:", len(units), flush=True)


def gen_prompt(u, n, round_i):
    angle = ["definitions and laws", "numerical / calculation based", "conceptual understanding and applications", "facts, examples and exceptions"][(round_i + SEED) % 4]
    return (f"Board/level: {u['board']} {u['level']}. Subject: {u['subject']}. Unit: {u['unit']}.\n\n"
            f"Write {n} distinct, standard-syllabus multiple-choice questions on THIS unit only, in the style of the official board paper (focus: {angle}). "
            "Rules: exactly four options with exactly one correct answer; distractors must be plausible, of the same kind and in the same units; "
            "no 'all of the above' or 'none of the above'; any numbers must be computed correctly; use LaTeX inside $...$ for formulas; the question must be self-contained.\n"
            "Output ONLY a JSON array; each element: {\"q\": str, \"options\": [4 strings], \"answer\": \"A\"|\"B\"|\"C\"|\"D\", \"explanation\": one-sentence justification}. "
            "Vary the position of the correct answer.")


def parse(txt):
    s, e = txt.find("["), txt.rfind("]")
    if s < 0 or e < 0: return []
    try: arr = json.loads(txt[s:e + 1])
    except Exception:
        try: arr = json.loads(re.sub(r"\\(?![\"\\/bfnrtu])", r"\\\\", txt[s:e + 1]))
        except Exception: return []
    return [a for a in arr if isinstance(a, dict)]


def structural(a):
    try:
        q = a["q"].strip(); o = [re.sub(r"^\(?[A-Da-d][\).:]\s+", "", str(x).strip()) for x in a["options"]]; k = a["answer"].strip().upper()[:1]; w = str(a.get("explanation", "")).strip()
    except Exception: return None
    if len(o) != 4 or k not in LET or len(q) < 15 or not w: return None
    if len({norm(x) for x in o}) < 4 or any(not x or len(x) > 160 for x in o): return None
    if any(re.search(r"all of the above|none of the above|both a and b|a and b|all the above|none of these", x, re.I) for x in o): return None
    if re.search(r"\bnull\b|\bTODO\b|\.\.\.$", q): return None
    if q.count("$") % 2 or any(x.count("$") % 2 for x in o): return None
    lens = [len(x) for x in o]
    if max(lens) > 6 * max(1, min(lens)) + 25: return None
    return dict(q=q, o=o, k=k.lower(), w=w)


@torch.no_grad()
def generate(prompts, max_new, temp=None):
    enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
    kw = dict(do_sample=True, temperature=temp, top_p=0.95) if temp else dict(do_sample=False)
    out = model.generate(**enc, max_new_tokens=max_new, pad_token_id=tok.pad_token_id, **kw)
    return tok.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)


LID = [tok.encode(c, add_special_tokens=False)[0] for c in LET]


@torch.no_grad()
def blind_probs(items, ctx):
    res = []
    for s in range(0, len(items), 48):
        ch = items[s:s + 48]; ps = []
        for it in ch:
            opts = "\n".join(f"{LET[j]}. {o}" for j, o in enumerate(it["o"]))
            ps.append(chat(f"Subject: {ctx[id(it)]['subject']} ({ctx[id(it)]['board']} {ctx[id(it)]['level']}), unit: {ctx[id(it)]['unit']}\n\nQuestion: {it['q']}\n{opts}\n\nWhich option is correct? Reply with only the letter."))
        enc = tok(ps, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        lg = model(**enc, logits_to_keep=1).logits[:, -1].float()[:, LID]
        res += torch.softmax(lg, -1).cpu().tolist()
    return res


def cot_solve(items, ctx):
    ans = []
    for s in range(0, len(items), 96):
        ch = items[s:s + 96]; ps = []
        for it in ch:
            opts = "\n".join(f"{LET[j]}. {o}" for j, o in enumerate(it["o"]))
            ps.append(chat(f"Subject: {ctx[id(it)]['subject']} ({ctx[id(it)]['board']} {ctx[id(it)]['level']}), unit: {ctx[id(it)]['unit']}\n\nQuestion: {it['q']}\n{opts}\n\nSolve step by step, carefully checking any arithmetic, then end with a final line exactly of the form 'Answer: X' where X is A, B, C or D."))
        for t in generate(ps, 700):
            m = re.findall(r"Answer:\s*\**\s*\(?([ABCD])\b", t); ans.append(m[-1] if m else None)
    return ans


existing = {u["sk"] + "#" + u["unit"]: list(u["existing"]) for u in units}
kept_all = []; prog.update(total=len(units) * ROUNDS, msg="generating"); status()
BATCH = 48
for rnd in range(ROUNDS):
    order = list(range(len(units))); random.shuffle(order)
    for s in range(0, len(order), BATCH):
        ub = [units[i] for i in order[s:s + BATCH]]; per_call = 4
        prompts = [chat(gen_prompt(u, min(per_call, u["need"]), rnd + s // BATCH)) for u in ub]
        texts = generate(prompts, 1000, temp=0.8)
        cands = []; ctx = {}
        for u, t in zip(ub, texts):
            arr = parse(t); counts["generated"] += min(per_call, u["need"]); counts["parsed"] += len(arr)
            for a in arr[:per_call]:
                c = structural(a)
                if not c: continue
                counts["structural_ok"] += 1
                pool = existing[u["sk"] + "#" + u["unit"]]
                if any(jac(c["q"], x) > 0.7 for x in pool): counts["dup"] += 1; continue
                ctx[id(c)] = u; c["_u"] = u; cands.append(c)
        if cands:
            pr = blind_probs(cands, ctx); keep1 = []
            for c, p in zip(cands, pr):
                if LET.index(c["k"].upper()) == max(range(4), key=lambda j: p[j]) and p[LET.index(c["k"].upper())] >= P_MIN: c["p"] = round(p[LET.index(c["k"].upper())], 3); keep1.append(c)
            counts["blind_ok"] += len(keep1)
            num = [c for c in keep1 if re.search(r"\d", c["q"]) or any(re.search(r"\d", o) for o in c["o"])]
            ok_num = {id(c) for c, a in zip(num, cot_solve(num, ctx) if num else []) if a == c["k"].upper()}
            for c in keep1:
                if c in num and id(c) not in ok_num: continue
                counts["cot_ok"] += 1
                u = c["_u"]; pool = existing[u["sk"] + "#" + u["unit"]]
                if any(jac(c["q"], x) > 0.7 for x in pool): counts["dup"] += 1; continue
                pool.append(c["q"]); counts["kept"] += 1
                rec = dict(sk=u["sk"], unit=u["unit"], item=dict(c="mcq", m=1, t="MCQ", q=c["q"], o=c["o"], k=c["k"], w=c["w"], v="T32", p=c["p"], n=c in num))
                kept_all.append(rec); last["v"] = f"[{u['sk']} | {u['unit']}]\n{c['q']}\n" + "\n".join(f"{LET[j]}. {o}" for j, o in enumerate(c["o"])) + f"\nkey {c['k'].upper()} (p={c['p']}) — {c['w']}"
        prog["done"] += len(ub); prog["msg"] = f"round {rnd + 1}/{ROUNDS}"; status()
        with open(os.path.join(OUT, "teacher_items.jsonl"), "w") as f:
            for r in kept_all: f.write(json.dumps(r, ensure_ascii=False) + "\n")
prog["msg"] = "done"; status(); open(os.path.join(OUT, "DONE"), "w").write(json.dumps(counts))
