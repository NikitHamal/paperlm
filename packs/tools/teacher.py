#!/usr/bin/env python3
"""Teacher distillation with independent verification (Qwen2.5-32B) -> /tmp/packs/<id>/verified.jsonl.
Every item is generated from ONE syllabus anchor (textbook fact) and must pass: structure, blind multi-order solve, passage entailment,
per-distractor wrongness probe.  usage: teacher.py <pack_id...>   env: MAXA (anchors/pack), NSHORT"""
import json, os, random, re, sys, time, torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, "/work/paperlm/data"]
import validator as V
from transformers import AutoTokenizer, AutoModelForCausalLM
M = "/dev/shm/qwen32b"; tk = AutoTokenizer.from_pretrained(M); tk.padding_side = "left"
model = AutoModelForCausalLM.from_pretrained(M, torch_dtype=torch.bfloat16, device_map="cuda").eval()
SPECS = json.load(open(os.path.join(HERE, "..", "pack_specs.json"))); MAXA = int(os.environ.get("MAXA", 2800)); NSHORT = int(os.environ.get("NSHORT", 800)); OFF = int(os.environ.get("OFF", 0)); SUF = os.environ.get("SUF", "")
STYLES = ["a definition or recall question", "a concept-application question (a short scenario or reason)", "a 'why/how' reasoning question",
          "a question that distinguishes between two related ideas", "an identification question (name the term, law, organ, unit or process)"]
SYS = "You are a senior Nepal NEB board examiner who writes precise, factually exact exam questions strictly from the given textbook passage."
YES, NO = tk.encode("Yes")[0], tk.encode("No")[0]; LET = [tk.encode(x)[0] for x in "ABCD"]
def chat(u): return tk.apply_chat_template([{"role": "system", "content": SYS}, {"role": "user", "content": u}], tokenize=False, add_generation_prompt=True)
@torch.no_grad()
def gen(prompts, max_new=int(os.environ.get("MAXNEW", 300)), bs=128, temp=0.7):
    out = []
    for i in range(0, len(prompts), bs):
        b = tk(prompts[i:i + bs], return_tensors="pt", padding=True).to("cuda")
        o = model.generate(**b, max_new_tokens=max_new, do_sample=True, temperature=temp, top_p=0.92, pad_token_id=tk.eos_token_id)
        out += tk.batch_decode(o[:, b.input_ids.shape[1]:], skip_special_tokens=True)
    return out
@torch.no_grad()
def nextp(prompts, ids, bs=24):
    res = []
    for i in range(0, len(prompts), bs):
        b = tk(prompts[i:i + bs], return_tensors="pt", padding=True).to("cuda")
        lg = model(**b).logits[:, -1, :].float(); res += torch.softmax(lg[:, ids], -1).cpu().tolist()
    return res
def pj(t):
    m = re.search(r"\{.*\}", t, re.S)
    try: return json.loads(m.group(0)) if m else None
    except Exception: return None
BAD = re.compile(r"(all of the above|none of the|both [a-d]\b|\bpassage\b|\btext\b states|according to the)", re.I)
def okt(s, lo=2, hi=420): return isinstance(s, str) and lo <= len(s.strip()) <= hi and V.check_text(s.strip()) is None
def mcq_prompt(a, title, style):
    return chat(f"Subject: {title}. Unit: {a['unit']}.\nTextbook passage:\n\"{a['anchor']}\"\n\nWrite ONE NEB-standard multiple-choice question ({style}) whose correct answer is stated in the passage. "
                "The question must be self-contained (never mention 'the passage'). Give one correct answer and three plausible but clearly wrong distractors of the same type and similar length (no 'all of the above', no 'none'). "
                "Use LaTeX in $...$ for formulas and units. Reply with ONLY JSON: {\"question\": str, \"answer\": str, \"distractors\": [str,str,str], \"explanation\": \"one sentence stating the fact that proves the answer\"}")
def short_prompt(facts, title, unit, m):
    return chat(f"Subject: {title}. Unit: {unit}.\nTextbook facts:\n" + "\n".join(f"- {f}" for f in facts) + f"\n\nWrite ONE NEB {m}-mark written question that can be fully answered from these facts, and its model answer "
                f"({m} clear, factual points in {m * 22} words at most, no fluff, use $...$ for formulas). Reply with ONLY JSON: {{\"question\": str, \"answer\": str}}")
def opts_text(q, ops): return q + "\n" + "\n".join(f"{c}) {o}" for c, o in zip("ABCD", ops))
def verify_mcq(items, anchors):
    keep = []; rng = random.Random(1)
    for it in items:
        ops = [it["answer"]] + it["distractors"]; it["perms"] = [rng.sample(range(4), 4) for _ in range(2)]
    pr, ix = [], []
    for n, it in enumerate(items):
        for p in it["perms"]:
            o = [([it["answer"]] + it["distractors"])[j] for j in p]
            pr.append(chat(opts_text(it["question"], o) + "\nAnswer with the single letter of the correct option.") ); ix.append((n, p.index(0)))
    ps = nextp(pr, LET); ok = [[] for _ in items]
    for (n, k), pp in zip(ix, ps): ok[n].append(pp[k])
    ent = nextp([chat(f"Passage: {anchors[it['aid']]}\nQuestion: {it['question']}\nProposed answer: {it['answer']}\nIs the proposed answer fully correct and supported by the passage? Answer Yes or No.") + "" for it in items], [YES, NO])
    dp, di = [], []
    for n, it in enumerate(items):
        for d in it["distractors"]: dp.append(chat(f"Passage: {anchors[it['aid']]}\nQuestion: {it['question']}\nProposed answer: {d}\nIs the proposed answer correct? Answer Yes or No.")); di.append(n)
    dy = nextp(dp, [YES, NO]); dmax = [0.0] * len(items)
    for n, p in zip(di, dy): dmax[n] = max(dmax[n], p[0])
    for n, it in enumerate(items):
        it["scores"] = dict(solve=round(min(ok[n]), 3), entail=round(ent[n][0], 3), dist_max=round(dmax[n], 3)); it.pop("perms")
        if min(ok[n]) >= 0.6 and ent[n][0] >= 0.85 and dmax[n] <= 0.25: keep.append(it)
    return keep
def verify_short(items, anchors):
    pr = [chat(f"Facts: {' '.join(it['facts'])}\nQuestion: {it['question']}\nModel answer: {it['answer']}\nIs the model answer entirely correct, supported by the facts, and does it answer the question? Answer Yes or No.") for it in items]
    p = nextp(pr, [YES, NO]); keep = []
    for it, x in zip(items, p):
        it["scores"] = dict(entail=round(x[0], 3))
        if x[0] >= 0.85: keep.append(it)
    return keep
REJ = {}
def status(pid, **kw):
    try: json.dump(dict(pack=pid, t=time.time(), **kw), open("/tmp/paperlm/status_packs.json", "w"))
    except Exception: pass
for pid in sys.argv[1:]:
    S = SPECS[pid]; D = f"/tmp/packs/{pid}"; A = [json.loads(l) for l in open(f"{D}/anchors.jsonl")]; rng = random.Random(7); rng.shuffle(A)
    pri = {"law": 0, "formula": 0, "def": 1, "fact": 2}; A = sorted(A, key=lambda a: pri[a["kind"]] + rng.random() * 1.2)[OFF:OFF + MAXA]; amap = {a["aid"]: a["anchor"] for a in A}
    todo = [(a, STYLES[i % 5]) for i, a in enumerate(A)] + [(a, STYLES[(i + 2) % 5]) for i, a in enumerate(A) if a["kind"] != "fact" and i % 2 == 0]
    fr = open(f"{D}/raw{SUF}.jsonl", "w")
    fo = open(f"{D}/verified{SUF}.jsonl", "w"); nraw = nkeep = 0; t0 = time.time(); seen = set()
    for c in range(0, len(todo), 384):
        part = todo[c:c + 384]; raw = gen([mcq_prompt(a, S["title"], st) for a, st in part]); items = []
        for (a, st), r in zip(part, raw):
            j = pj(r); nraw += 1; why_rej = None
            if not j: why_rej = "json"
            elif not okt(j.get("question"), 15, 360): why_rej = "q_text"
            elif not okt(j.get("answer"), 1, 160): why_rej = "a_text"
            elif not isinstance(j.get("distractors"), list) or len(j["distractors"]) != 3: why_rej = "n_dist"
            if why_rej: REJ[why_rej] = REJ.get(why_rej, 0) + 1; continue
            ds = [d.strip() for d in j["distractors"] if okt(d, 1, 160)]; why = j.get("explanation", "")
            if len(ds) != 3: why_rej = "d_text"
            elif not okt(why, 15, 300): why_rej = "why_text"
            elif BAD.search(j["question"] + j["answer"] + " ".join(ds) + why): why_rej = "bad_phrase"
            else:
                allo = [x.strip().lower() for x in ds + [j["answer"]]]
                if len(set(allo)) != 4: why_rej = "dup_opts"
                elif j["question"].strip().lower() in seen: why_rej = "dup_q"
            if why_rej: REJ[why_rej] = REJ.get(why_rej, 0) + 1; continue
            seen.add(j["question"].strip().lower()); items.append(dict(type="mcq", marks=1, unit=a["unit"], aid=a["aid"], anchor=a["anchor"], question=j["question"].strip(), answer=j["answer"].strip(), distractors=ds, why=why.strip()))
        fr.write("".join(json.dumps(dict(it, tier="raw"), ensure_ascii=False) + "\n" for it in items)); fr.flush()   # structurally valid, UNVERIFIED teacher drafts: stage-A pretraining only, never the bank
        for it in verify_mcq(items, amap): fo.write(json.dumps(it, ensure_ascii=False) + "\n"); nkeep += 1
        for it in items:
            sc_ = it.get("scores", {})
            for nm, bad in (("v_solve", sc_.get("solve", 1) < 0.6), ("v_entail", sc_.get("entail", 1) < 0.85), ("v_distractor", sc_.get("dist_max", 0) > 0.25)):
                if bad: REJ[nm] = REJ.get(nm, 0) + 1
        fo.flush(); status(pid, stage="mcq", rej=REJ, done=c + len(part), total=len(todo), raw=nraw, kept=nkeep, eta_min=round((time.time() - t0) / (c + len(part)) * (len(todo) - c - len(part)) / 60, 1))
    byu = {}
    for a in A: byu.setdefault(a["unit"], []).append(a["anchor"])
    jobs = []
    for i in range(NSHORT):
        u = rng.choice(list(byu)); m = rng.choice([2, 3, 3, 5]); fs = rng.sample(byu[u], min(len(byu[u]), 1 if m == 2 else 2 if m == 3 else 3)); jobs.append((u, m, fs))
    for c in range(0, len(jobs), 256):
        part = jobs[c:c + 256]; raw = gen([short_prompt(f, S["title"], u, m) for u, m, f in part], max_new=330); items = []
        for (u, m, fs), r in zip(part, raw):
            j = pj(r)
            if j and okt(j.get("question"), 15, 300) and okt(j.get("answer"), 20, 650) and not BAD.search(j["question"]): items.append(dict(type="short", marks=m, unit=u, facts=fs, anchor=" ".join(fs), question=j["question"].strip(), answer=j["answer"].strip()))
        for it in verify_short(items, amap): fo.write(json.dumps(it, ensure_ascii=False) + "\n"); nkeep += 1
        fo.flush(); status(pid, stage="short", done=c + len(part), total=len(jobs), kept=nkeep)
    status(pid, stage="done", kept=nkeep, raw=nraw, minutes=round((time.time() - t0) / 60, 1)); print(pid, "kept", nkeep, "raw", nraw, flush=True)
