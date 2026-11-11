#!/usr/bin/env python3
"""Stage-2 independent verification of teacher-written MCQs (MoLab GPU).

Teacher candidates already passed: structure, one blind solve, CoT for numerics.  Self-agreement alone proved insufficient
(a verbatim petty-cash item had a key contradicting its own explanation), so each candidate must now survive FIVE more checks:
  P  permutation-consistency : blind solve under 4 cyclic option orders; the key TEXT must win every time (mean p>=.85, min p>=.6)
  E  explanation entailment  : P(Yes | explanation supports key, no errors) >= .85
  D  discrimination probe    : the SAME explanation attached to the best wrong option must be rejected (P(Yes) <= .30)
  N  program-aided numeric   : for computational stems a blind Python program (executed, no option shown) must reproduce the key's
                               number within 1 % AND be closer to the key than to any distractor; unparseable key -> reject
  X  explanation arithmetic  : every number in the key option must occur in the explanation (or be derivable) for numeric items
usage: teacher_verify.py MODEL_DIR IN_JSONL OUT_DIR
"""
import json, sys, os, re, time, math, subprocess, tempfile
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL, INP, OUT = sys.argv[1:4]
STATUS = "/tmp/paperlm/status_verify.json"; os.makedirs(OUT, exist_ok=True); t0 = time.time()
LET = "ABCD"; SYS = "You are a meticulous senior examiner and subject expert for Nepali board and entrance exams. You are accurate and strict."
counts = dict(total=0, P=0, E=0, D=0, N_applicable=0, N=0, X=0, kept=0)
prog = dict(done=0, total=1, msg="loading"); last = {"v": None}


def status():
    json.dump(dict(ts=time.time(), elapsed=round(time.time() - t0), counts=counts, last=last["v"], **prog), open(STATUS + ".tmp", "w")); os.replace(STATUS + ".tmp", STATUS)


status()
tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map="cuda"); model.eval()
LID = [tok.encode(c, add_special_tokens=False)[0] for c in LET]
YN = [tok.encode(c, add_special_tokens=False)[0] for c in ("Yes", "No")]


def chat(u, prefix=""):
    return tok.apply_chat_template([{"role": "system", "content": SYS}, {"role": "user", "content": u}], tokenize=False, add_generation_prompt=True) + prefix


@torch.no_grad()
def last_logits(prompts, ids, bs=32):
    res = []
    for s in range(0, len(prompts), bs):
        enc = tok(prompts[s:s + bs], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        lg = model(**enc, logits_to_keep=1).logits[:, -1].float()[:, ids]
        res += torch.softmax(lg, -1).cpu().tolist()
    return res


@torch.no_grad()
def generate(prompts, max_new, bs=64):
    out_all = []
    for s in range(0, len(prompts), bs):
        enc = tok(prompts[s:s + bs], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        out = model.generate(**enc, max_new_tokens=max_new, do_sample=False, pad_token_id=tok.pad_token_id)
        out_all += tok.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    return out_all


def ctx_of(r): b, l, s = r["sk"].split("|"); return f"Subject: {s} ({b} {l}), unit: {r['unit']}"


def mcq_prompt(r, order):
    it = r["item"]; opts = "\n".join(f"{LET[j]}. {it['o'][i]}" for j, i in enumerate(order))
    return chat(f"{ctx_of(r)}\n\nQuestion: {it['q']}\n{opts}\n\nWhich option is correct? Reply with only the letter.")


def ent_prompt(r, idx):
    it = r["item"]; opts = "\n".join(f"{LET[j]}. {o}" for j, o in enumerate(it["o"]))
    return chat(f"{ctx_of(r)}\n\nQuestion: {it['q']}\n{opts}\n\nProposed correct answer: {LET[idx]}. {it['o'][idx]}\nProposed explanation: {it['w']}\n\n"
                "Is the proposed answer truly correct, AND is the explanation factually correct, consistent with that answer, and free of contradictions? Reply Yes or No.")


# ---- numeric parsing -------------------------------------------------------------------------------------------------
def tex2py(s):
    s = s.strip().strip("$").replace("\\,", "").replace("\\!", "").replace("\\ ", " ")
    s = re.sub(r"(?<=\d),(?=\d{3}\b)", "", s)
    s = re.sub(r"\\(?:text|mathrm|mathbf)\{[^}]*\}", "", s)
    s = re.sub(r"\\(?:frac|dfrac)\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", s)
    s = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", s)
    s = s.replace("\\times", "*").replace("\\cdot", "*").replace("\\pi", "pi").replace("^", "**").replace("{", "(").replace("}", ")")
    s = re.sub(r"\\circ|°|%|\\%", "", s)
    return s


def num_of(opt):
    """Leading numeric value of an option, or None."""
    s = re.sub(r"(\d|\))\s*(sqrt|pi|\()", r"\1*\2", tex2py(opt))
    m = re.match(r"\s*[-+−]?\s*[\d.(][\d.eE+\-*/() sqrtpi]*", s)
    if not m: return None
    expr = m.group(0).replace("−", "-").strip()
    while expr and expr[-1] in "+-*/ (": expr = expr[:-1]
    expr = re.sub(r"(\d)\s+(\d)", r"\1\2", expr)
    try:
        v = eval(expr, {"__builtins__": {}}, {"sqrt": math.sqrt, "pi": math.pi}); return float(v)
    except Exception: return None


NUMQ = re.compile(r"calculate|compute|evaluate|find the (?:value|sum|product|area|volume|distance|speed|current|resistance|amount|number|mean|median|rate)|how many|how much|what is the (?:value|sum|product|area|volume)", re.I)


def is_numeric(r):
    q = r["item"]["q"]; nums = re.findall(r"\d+(?:\.\d+)?", q)
    return len(nums) >= 2 or (len(nums) >= 1 and NUMQ.search(q) is not None)


def run_code(code):
    code = re.sub(r"^```(?:python)?|```$", "", code.strip(), flags=re.M).strip()
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f: f.write("import math\nfrom math import *\ntry:\n    import sympy\nexcept Exception: pass\n" + code + "\n"); p = f.name
    try:
        r = subprocess.run([sys.executable, p], capture_output=True, text=True, timeout=10)
        m = re.findall(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", r.stdout)
        return float(m[-1]) if m else None
    except Exception: return None
    finally: os.unlink(p)


def close(a, b, rel=0.01): return abs(a - b) <= rel * max(abs(a), abs(b), 1e-9) or abs(a - b) < 1e-9


# ---- run ------------------------------------------------------------------------------------------------------------
rows = [json.loads(l) for l in open(INP)]
counts["total"] = len(rows); prog.update(total=len(rows) * 5, msg="P: permutation consistency"); status()
for r in rows: r["chk"] = {}; r["_k"] = LET.index(r["item"]["k"].upper())

# P
orders = [[(j + sft) % 4 for j in range(4)] for sft in range(4)]
prompts = [mcq_prompt(r, o) for r in rows for o in orders]
pr = last_logits(prompts, LID)
for i, r in enumerate(rows):
    ps = []
    for j, o in enumerate(orders):
        p = pr[i * 4 + j]; pos_of_key = o.index(r["_k"]); ps.append((max(range(4), key=lambda x: p[x]) == pos_of_key, p[pos_of_key]))
    ok = all(a for a, _ in ps) and sum(p for _, p in ps) / 4 >= 0.85 and min(p for _, p in ps) >= 0.6
    r["chk"]["P"] = ok; r["chk"]["Pmean"] = round(sum(p for _, p in ps) / 4, 3); counts["P"] += ok
prog.update(done=len(rows), msg="E/D: explanation entailment + discrimination"); status()

# E and D
ent = last_logits([ent_prompt(r, r["_k"]) for r in rows], YN)
bad_idx = []
for r, e in zip(rows, ent):
    r["chk"]["E"] = e[0] >= 0.85; r["chk"]["Ep"] = round(e[0], 3); counts["E"] += r["chk"]["E"]
    # best wrong option according to the P-stage text probabilities is not stored; use the model's blind ranking under the original order
pr0 = pr[0::4]
for r, p in zip(rows, pr0):
    wrong = max((x for x in range(4) if x != r["_k"]), key=lambda x: p[x]); bad_idx.append(wrong)
dis = last_logits([ent_prompt(r, w) for r, w in zip(rows, bad_idx)], YN)
for r, d in zip(rows, dis):
    r["chk"]["D"] = d[0] <= 0.30; r["chk"]["Dp"] = round(d[0], 3); counts["D"] += r["chk"]["D"]
prog.update(done=len(rows) * 2, msg="N: program-aided numeric check"); status()

# N (blind program-aided) + X
num_rows = [r for r in rows if is_numeric(r)]; counts["N_applicable"] = len(num_rows)
codes = generate([chat(f"{ctx_of(r)}\n\nQuestion (no options are shown): {r['item']['q']}\n\nWrite a short, self-contained Python program (standard library, math or sympy) that computes the numerical answer to this question from first principles and prints ONLY the final number in the unit most natural for this question (base-10 digits, no text). Output only code.") for r in num_rows], 500)
for r in rows: r["chk"]["N"] = True; r["chk"]["X"] = True
for r, code in zip(num_rows, codes):
    it = r["item"]; v = run_code(code); vals = [num_of(o) for o in it["o"]]; kv = vals[r["_k"]]
    ok = v is not None and kv is not None and close(v, kv)
    if ok:
        for j, x in enumerate(vals):
            if j != r["_k"] and x is not None and abs(x - v) < abs(kv - v) - 1e-12: ok = False
    r["chk"]["N"] = bool(ok); r["chk"]["Nprog"] = v
    # X: key number must appear in the explanation
    kn = re.findall(r"\d+(?:\.\d+)?", tex2py(it["o"][r["_k"]]))
    r["chk"]["X"] = (not kn) or all(n in re.sub(r",", "", it["w"]) for n in kn[:2])
for r in rows: counts["N"] += r["chk"]["N"] if r in num_rows else 0; counts["X"] += r["chk"]["X"]
prog.update(done=len(rows) * 4, msg="finalising"); status()

kept = []
for r in rows:
    c = r["chk"]; r["pass"] = bool(c["P"] and c["E"] and c["D"] and c["N"] and c["X"])
    if r["pass"]:
        it = dict(r["item"]); it["v"] = "T32v"; it["p"] = c["Pmean"]; kept.append(dict(sk=r["sk"], unit=r["unit"], item=it)); counts["kept"] += 1
        last["v"] = f"[{r['sk']} | {r['unit']}]\n{it['q']}\n" + "\n".join(f"{LET[j]}. {o}" for j, o in enumerate(it["o"])) + f"\nkey {it['k'].upper()} — {it['w']}"
for r in rows: r.pop("_k", None)
with open(os.path.join(OUT, "teacher_verified.jsonl"), "w") as f:
    for r in kept: f.write(json.dumps(r, ensure_ascii=False) + "\n")
with open(os.path.join(OUT, "teacher_checked_all.jsonl"), "w") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
json.dump(counts, open(os.path.join(OUT, "verify_summary.json"), "w"), indent=1)
prog.update(done=len(rows) * 5, msg="done"); status(); open(os.path.join(OUT, "DONE"), "w").write(json.dumps(counts))
print(counts)
