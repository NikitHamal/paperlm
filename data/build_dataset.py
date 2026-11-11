#!/usr/bin/env python3
"""PaperLM gold dataset builder.

raw.jsonl (extract_neb.py)  ->  normalise  ->  validate (LaTeX/char/structure/visual-ref)  ->  classify
-> render strict schema lines  ->  train/val split by SOURCE FILE (no leakage)  ->  stats.

Schema (special tokens are written as <|...|>):
 <|bos|><|board=NEB|><|level=C12|><|subj=physics|><|unit|>UNIT TEXT<|marks=5|><|type=NUMERICAL|>
 <|q|>QUESTION [<|oa|>A<|ob|>B<|oc|>C<|od|>D  |  <|part|>(a) text<|pm|>2 ...] [<|or|><|part|>...]
 <|ans|>b<|why|>reason<|end|>        (MCQ)      |   ... <|sol|>marking rubric / model answer<|end|>  (written)

Usage: build_dataset.py <raw.jsonl> <outdir> [--seed 7]
"""
import collections, hashlib, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validator as V

MARKS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15]
TYPES = ["MCQ", "CONCEPTUAL", "DERIVATION", "NUMERICAL", "LONG", "OR", "SHORT"]
LEVELS = ["C8", "C10", "C11", "C12", "IOE", "CEE", "BCA", "BSN", "BE"]
BOARDS = ["BLE", "SEE", "NEB", "IOE", "CEE", "TU", "CTEVT"]
MIN_SUBJ = 12

INTENT = re.compile(r"\b(define|state|what|why|how|explain|describe|differentiate|distinguish|derive|prove|show|calculate|find|determine|compute|evaluate|solve|write|list|name|give|discuss|compare|draw|illustrate|justify|mention|identify|classify|outline|enumerate|define|obtain|deduce|establish|express|convert|simplify|factorise|factorize|expand|construct|verify|differentiate|integrate|if|when|is|are|does|do|can|which|who|where|a |an |the |two |in |by |from |for |let |consider |using |with )", re.I)
BAD_UNIT = re.compile(r"^group\b|model answer|answers?\b|solution|marking|key\b|question paper|practice|summary|verification|sources?\b|comprehension|worked", re.I)
CONCEPT = re.compile(r"^(define|state|what|why|explain|describe|differentiate|distinguish|list|name|give (reason|two|any)|write (short|any|two|a note)|mention|identify|discuss|compare|outline|enumerate|justify)", re.I)
DERIV = re.compile(r"\b(derive|prove|show that|deduce|establish|obtain an expression|obtain the expression|find an expression|obtain a relation)\b", re.I)
NUMR = re.compile(r"\b(calculate|find|determine|compute|evaluate|solve|how much|how many|what is the (value|number|speed|force|mass|current|resistance|energy)|if .* then)\b", re.I)
NOSHUF = re.compile(r"\b(both|all of|none of|above|neither|either|only|and\b.*\bboth|a and b|a, b|a & b)\b|^\(?[a-d]\)?$", re.I)

def clean(t):
    t = t or ""
    t = re.sub(r"\[\[[\d+]+\]\]", "", t)
    t = re.sub(r"\s*\((?:NEB|SEE|BLE|IOE|CEE|TU|PU|KU)[^)]{0,40}\)\s*$", "", t)
    t = re.sub(r"\s*\[\d+\]\s*$", "", t)
    t = re.sub(r"\s*\((?:NEB|SEE|BLE|IOE|CEE|TU)[^)]{0,40}\)", "", t)
    t = V.normalize(t)
    t = re.sub(r"\s+([,.;:?!])", r"\1", t)
    return t

def marks_in(t):
    m = re.findall(r"\[\[([\d+]+)\]\]", t or "")
    return sum(sum(int(x) for x in g.split("+") if x) for g in m)

def classify(rec, stem, parts, alt, marks):
    if rec["qtype"] == "MCQ": return "MCQ"
    if alt: return "OR"
    body = " ".join([stem] + [p[1] for p in parts])
    if DERIV.search(body): return "DERIVATION"
    if re.search(r"\d", body) and NUMR.search(body) and (re.search(r"\$|\d+\s*(m|kg|cm|s|N|V|A|J|W|mol|g|%|°)", body)): return "NUMERICAL"
    if marks >= 8 or (len(parts) >= 3 and marks >= 6): return "LONG"
    if CONCEPT.search(stem or (parts[0][1] if parts else "")) : return "CONCEPTUAL"
    return "SHORT"

def snap_marks(m):
    return min(MARKS, key=lambda x: abs(x - m))

def unit_clean(u):
    u = re.sub(r"^\s*(unit\s*)?\d+([.\-]\d+)*[.:)]?\s*", "", u or "").strip()
    u = re.sub(r"\([^)]*\)", "", u).strip(" -–—:")
    u = re.sub(r"\s+", " ", V.normalize(u))
    if not u or BAD_UNIT.search(u) and not u.lower().startswith("paper"): return "General"
    w = u.split()
    return " ".join(w[:8])[:60]

def subj_slug(s):
    s = re.sub(r"^(course-|bca-)", "", s or "general")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:28] or "general"

def render_mcq(h, q, opts, key, why):
    t = f"{h}<|q|>{q}<|oa|>{opts[0]}<|ob|>{opts[1]}<|oc|>{opts[2]}<|od|>{opts[3]}<|ans|>{key}"
    if why: t += f"<|why|>{why}"
    return t + "<|end|>"

def render_written(h, stem, parts, alt, sol):
    t = f"{h}<|q|>{stem}"
    for lab, tx, mk in parts:
        t += f"<|part|>{'(' + lab + ') ' if lab else ''}{tx}" + (f"<|pm|>{mk}" if mk else "")
    if alt:
        t += "<|or|>"
        for lab, tx, mk in alt:
            t += f"<|part|>{'(' + lab + ') ' if lab else ''}{tx}" + (f"<|pm|>{mk}" if mk else "")
    if sol: t += f"<|sol|>{sol}"
    return t + "<|end|>"

def trunc_sentence(t, n):
    if len(t) <= n: return t
    cut = t[:n]; k = max(cut.rfind(". "), cut.rfind("; "))
    return cut[:k + 1] if k > n * 0.4 else ""

def main():
    raw, outdir = sys.argv[1], sys.argv[2]
    seed = 7
    os.makedirs(outdir, exist_ok=True)
    try:
        sys.path.insert(0, "/tmp/paperlm"); import live_status as LS
    except Exception: LS = None
    rng = random.Random(seed)
    rejects = collections.Counter(); gold = []
    R = [json.loads(l) for l in open(raw, encoding="utf-8")]
    if LS: LS.update("stage", name="DATA", phase="validating & building gold dataset", detail=f"{len(R):,} raw items")
    for i, r in enumerate(R):
        if r["board"] not in BOARDS or r["level"] not in LEVELS: rejects["bad board/level"] += 1; continue
        unit = unit_clean(r.get("unit", ""))
        if r["qtype"] == "MCQ":
            q = clean(r["q"]); opts = [clean(o).rstrip(".") if len(clean(o)) < 3 else clean(o) for o in r["opts"]]
            key = r.get("key", "")
            if not key: rejects["mcq_no_key"] += 1; continue
            if V.needs_visual(q): rejects["needs_visual"] += 1; continue
            why = trunc_sentence(clean(r.get("why", "")), 320)
            e = V.check_mcq(q, opts, key, why)
            if e and e.startswith("why:"): why, e = "", V.check_mcq(q, opts, key, "")
            if e: rejects["mcq:" + e.split(":")[0] + ":" + (e.split(":", 1)[-1][:24])] += 1; continue
            marks, stem, parts, alt, sol = 1, q, [], [], ""
            item = dict(qtype="MCQ", q=q, opts=opts, key=key, why=why)
        else:
            if BAD_UNIT.search(r.get("unit", "")) and not r["src"].startswith("paper:") : rejects["answer_unit"] += 1; continue
            raw_parts = r.get("parts", []); stem = clean(r.get("stem", ""))
            pm = []
            for p in raw_parts:
                mk = p.get("marks") or marks_in(p["text"])
                pm.append((p.get("label", ""), clean(p["text"]), int(mk or 0)))
            altp = [(p.get("label", ""), clean(p["text"]), int(p.get("marks") or marks_in(p["text"]) or 0)) for p in r.get("alt_parts", [])]
            marks = sum(m for _, _, m in pm) or r.get("marks") or marks_in(r.get("stem", "")) or 0
            if not marks: rejects["no_marks"] += 1; continue
            if r["src"].startswith("paper:"):
                marks = sum(m for _, _, m in pm) or marks_in(" ".join(p["text"] for p in raw_parts)) or r.get("marks") or 0
            if not marks: rejects["no_marks"] += 1; continue
            marks = snap_marks(marks) if marks not in MARKS else marks
            body = " ".join([stem] + [p[1] for p in pm])
            if V.needs_visual(body + " " + " ".join(p[1] for p in altp)): rejects["needs_visual"] += 1; continue
            first = stem or (pm[0][1] if pm else "")
            if not INTENT.match(first.strip()): rejects["not_question_intent"] += 1; continue
            if len(first) < 12: rejects["too_short"] += 1; continue
            sol = trunc_sentence(clean(r.get("sol", "")), 700) if r.get("sol") else ""
            e = V.check_written(stem, pm, altp, marks, sol)
            if e and e.startswith("sol:"): sol, e = "", V.check_written(stem, pm, altp, marks, "")
            if e: rejects["written:" + e.split(":")[0] + ":" + e.split(":", 1)[-1][:24]] += 1; continue
            if sol and len(sol) < 12: sol = ""
            item = dict(qtype="WRITTEN", stem=stem, parts=pm, alt=altp, sol=sol)
        typ = classify(r, stem, item.get("parts", []), item.get("alt", []), marks)
        item.update(board=r["board"], level=r["level"], subj=subj_slug(r["subject"]), unit=unit, marks=marks, type=typ, src=r["src"], id=r["id"])
        gold.append(item)
    subj_ct = collections.Counter(g["subj"] for g in gold)
    keep = {s for s, c in subj_ct.items() if c >= MIN_SUBJ}
    for g in gold:
        if g["subj"] not in keep: g["subj"] = "general"
    subjects = sorted(keep | {"general"})
    # --- render + split
    def header(g):
        return f"<|bos|><|board={g['board']}|><|level={g['level']}|><|subj={g['subj']}|><|unit|>{g['unit']}<|marks={g['marks']}|><|type={g['type']}|>"
    train, val, bad = [], [], 0
    stat = collections.Counter(); by_level = {}
    for g in gold:
        h = header(g)
        txt = render_mcq(h, g["q"], g["opts"], g["key"], g["why"]) if g["qtype"] == "MCQ" else render_written(h, g["stem"], g["parts"], g["alt"], g["sol"])
        e = V.validate_item_text(txt)
        if e: rejects["final:" + e[:30]] += 1; bad += 1; continue
        is_val = int(hashlib.md5(g["src"].encode()).hexdigest(), 16) % 100 < 4
        (val if is_val else train).append(txt)
        s = by_level.setdefault(g["level"], {"MCQ": 0, "WRITTEN": 0}); s[g["qtype"]] += 1
        stat["type:" + g["type"]] += 1; stat[f"marks:{g['marks']}"] += 1; stat["subj:" + g["subj"]] += 1
        if g["qtype"] == "MCQ" and not is_val and not any(NOSHUF.search(o) for o in g["opts"]):
            for _ in range(2):  # option-shuffle augmentation (train only)
                perm = list(range(4)); rng.shuffle(perm)
                if perm == [0, 1, 2, 3]: continue
                no = [g["opts"][p] for p in perm]; nk = "abcd"[perm.index("abcd".index(g["key"]))]
                why = g["why"] if not re.search(r"\(([a-d])\)|option ", g["why"]) else ""
                train.append(render_mcq(h, g["q"], no, nk, why))
    rng.shuffle(train)
    with open(f"{outdir}/train.txt", "w", encoding="utf-8") as f: f.write("\n".join(train) + "\n")
    with open(f"{outdir}/val.txt", "w", encoding="utf-8") as f: f.write("\n".join(val) + "\n")
    with open(f"{outdir}/gold.jsonl", "w", encoding="utf-8") as f:
        for g in gold: f.write(json.dumps(g, ensure_ascii=False) + "\n")
    meta = dict(boards=BOARDS, levels=LEVELS, subjects=subjects, types=TYPES, marks=MARKS)
    json.dump(meta, open(f"{outdir}/schema_meta.json", "w"), indent=1)
    stats = dict(raw=len(R), gold=len(gold), train_lines=len(train), val_lines=len(val), rejected=sum(rejects.values()),
                 reject_reasons=dict(rejects.most_common(40)), by_level=by_level,
                 by_type={k[5:]: v for k, v in stat.items() if k.startswith("type:")},
                 by_marks={k[6:]: v for k, v in stat.items() if k.startswith("marks:")},
                 by_subject={k[5:]: v for k, v in stat.most_common() if k.startswith("subj:")}, chars_train=sum(map(len, train)))
    json.dump(stats, open(f"{outdir}/dataset_stats.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in stats.items() if k not in ("by_subject", "reject_reasons")}, indent=1))
    print("top rejects:", json.dumps(stats["reject_reasons"])[:900])
    if LS: LS.update("dataset", gold_items=len(gold), rejected=stats["rejected"], by_level=by_level, by_type=stats["by_type"], train_lines=len(train), val_lines=len(val))

if __name__ == "__main__":
    main()
