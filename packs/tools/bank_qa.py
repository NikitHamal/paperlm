#!/usr/bin/env python3
"""Bank QA gate (structural, deterministic). Removes items a student would see as broken:
empty / orphan stems, truncated model answers, multi-part stems whose answer misses a part,
MCQs with a repeated key, duplicate / near-duplicate options, unbalanced LaTeX.
usage: bank_qa.py [pack_id ...]   (rewrites docs/packs/<id>/bank.json, writes packs/<id>/bank_qa_report.json)
As module: qa(item) -> list of reason strings (empty = ok)."""
import json, os, re, sys, collections
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PART = re.compile(r"(?:^|\s)\(?([a-d])\)\s")
ANSPART = re.compile(r"\(([a-d])\)")


def _tex_ok(t):
    t = t.replace("\\$", "")
    return t.count("$") % 2 == 0 and t.count("{") == t.count("}")


def _norm(s):
    return re.sub(r"[\s$]+|\\(?:text|mathrm|,|;|!| \\)|[{}]", "", s.lower())


LEAKWHY = re.compile(r"\b(?:in|from|by|of|to) the (?:context|passage|provided (?:text|context|information|formula|data|calculation)|given (?:text|context|information|passage))\b|\bthe (?:context|passage) (?:states|says|gives|mentions|provides|indicates)\b|\bprovided (?:in the )?(?:context|text|passage|information)\b|\bas (?:stated|given|mentioned) in the (?:context|text|passage|provided)\b|\bthe given formula directly\b", re.I)


def repair(it):
    """v14: a rationale that points at the teacher's hidden context ('as stated in the provided information') is replaced by the verified anchor fact."""
    if it.get("why") and LEAKWHY.search(it["why"]):
        it = dict(it); it["why"] = it["anchor"] if it.get("anchor") and not LEAKWHY.search(it["anchor"]) else ""; it["repaired_why"] = 1
    return _repair_parts(it)


def _repair_parts(it):
    """Part-aligned repair: a written item whose model answer covers only some of the stem's parts
    (e.g. answer starts at '(b)') is trimmed so the stem asks exactly what the answer answers."""
    if it["type"] == "mcq": return it
    q, a = it["question"].strip(), it["answer"].strip()
    ms = list(PART.finditer(" " + q))
    if len(ms) < 2: return it
    qs = " " + q; seg = {}
    for i, m in enumerate(ms): seg[m.group(1)] = qs[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(qs)].strip()
    got = [x for x in dict.fromkeys(ANSPART.findall(a)) if x in seg]
    if not got or set(got) == set(seg): return it
    keep = [x for x in seg if x in got]; marks = 0
    for x in keep: mk = re.findall(r"\[(\d+)\]", seg[x]); marks += int(mk[-1]) if mk else 0
    out = dict(it); parts = [re.sub(r"\s*\((?:NEB|HSEB)\s*20\d\d\)\s*$", "", seg[x]).strip() for x in keep]
    if len(keep) == 1:
        out["question"] = parts[0]; out["answer"] = re.sub(r"^\(" + keep[0] + r"\)\s*", "", a)
    else:
        out["question"] = " ".join(f"{x}) {t}" for x, t in zip(keep, parts)); out["answer"] = a
    out["marks"] = marks or max(1, it["marks"] // 2); out["repaired"] = "part_aligned"
    return out


FIG = re.compile(r"\b(figure|fig\.|diagram|shown (?:below|above|here)|as shown|graph (?:given|shown)|adjacent|the (?:table|data) (?:given|below|above))\b", re.I)
DANGLE = re.compile(r"\b(than|to|as|with|of) (?:it|them|this|that)\.?$", re.I)


LEAK = re.compile(r"\b(?:based on|using|use|from|with|by|according to|in) the (?:provided|given|above|following) (?:formula|data|information|facts|text|passage|context|details|statement)s?\b|\bthe provided (?:formula|information|facts|data)\b|\b(?:value|data|formula|information)s? (?:is |are )?(?:provided|given above)\s*[.?]?\s*$", re.I)


def orphan(q):
    """A stem that starts mid-sentence: lowercase opener, 'b)'/'c)' first part, or 'a) <lowercase continuation>' (its main clause was cut off)."""
    q = q.strip()
    if re.match(r"[b-d]\)\s", q) or re.match(r"(?![a-d]\)\s)[a-z]", q): return True
    m = re.match(r"a\)\s+([a-z])", q)
    return bool(m)


META = re.compile(r"\b(?:Grade|Class)\s*1[12]\b[^?]{0,40}\b(?:paper|exam|syllabus)\b|\b(?:carries|carry)\b[^?]{0,40}\bmarks?\b|\bshort[- ]answer question\b|\bentrance exam|\bwritten marks\b|\bpaper (?:has|contains|consists)\b|\bpast[- ]paper", re.I)
NUM = re.compile(r"\s*(-?\d+(?:\.\d+)?)(\s*(?:\\?%|[\\^/*(]|[A-Za-z]{1,2}\\b)?)")
OKCH = set("0123456789.+-*/() \t")


def arith_bad(text):
    """v14: every pure-number equation 'a \\times b + c = N' (maximal expression left of '=', no letters, balanced) is evaluated;
    a wrong sum/product (LLM teacher slip) kills the item. Percent results and partial expressions are skipped."""
    t = text.replace("\\times", "*").replace("\\cdot", "*").replace("\\div", "/").replace("\\left", "").replace("\\right", "").replace("\\,", "").replace("\\ ", " ").replace("\u00d7", "*").replace("\u2212", "-")
    for m in re.finditer(r"=", t):
        i = m.start(); j = i
        while j > 0 and t[j - 1] in OKCH: j -= 1
        left = t[j:i].strip()
        if j > 0 and (t[j - 1].isalnum() or t[j - 1] in "})^_{"): continue
        if not re.fullmatch(r"[\d(][\d.+*/() -]*", left) or not re.search(r"\d\s*[-+*/]\s*[\d(]", left) or left.count("(") != left.count(")") or len(left) > 60: continue
        rm = re.match(r"\s*(-?\d+(?:\.\d+)?)", t[i + 1:])
        if not rm: continue
        tail = t[i + 1 + rm.end(): i + 10 + rm.end()].lstrip()
        if tail and (tail[0] in "%^/(*" or tail.startswith("\\%") or re.match(r"[.]\d", tail) or re.match(r"[+-]\s*\d", tail)): continue
        try: v = eval(left.replace("^", "**"), {"__builtins__": {}}, {})
        except Exception: continue
        x = float(rm.group(1))
        if any(abs(v * k - x) <= 0.02 * max(1.0, abs(x)) or abs(v * k - x) <= 0.011 for k in (1, 1e3, 1e-3, 1e2, 1e-2, 1e6, 1e-6, 1e9, 1e-9)): continue  # unit-scaled results (J -> kJ, % ...)
        return True
    return False


def qa(it):
    r = []
    q, a = it.get("question", "").strip(), it.get("answer", "").strip()
    if orphan(q): r.append("orphan_stem")  # v13: chopped multi-part stems ('a) in series and b) in parallel. Find ...') have no main clause
    if LEAK.search(q): r.append("leaked_context")  # v13: 'using the provided formula' points at teacher anchor text the student never sees
    if len(q) < 12: r.append("empty_or_tiny_stem")
    if LEAKWHY.search(q + " " + a): r.append("leaked_context")
    if META.search(q): r.append("meta_exam_question")  # v14: questions about the exam format, not the subject
    if arith_bad(a + " " + it.get("why", "") + " " + q): r.append("arithmetic_error")  # v14: verified by evaluation
    if not a: r.append("no_answer")
    if FIG.search(q) or (re.search(r"\bpoints? [A-Z]\b", q) and not re.search(r"\bpoints? [A-Z]\b", it.get("anchor", ""))): r.append("needs_figure")  # the pack has no figures: a stem that points at one cannot be answered
    if not _tex_ok(q + " " + a + " " + it.get("why", "")): r.append("latex")
    if it["type"] == "mcq":
        d = it.get("distractors", [])
        opts = [a] + d
        if len(d) != 3: r.append("n_options")
        if any(DANGLE.search(o.strip()) for o in opts): r.append("dangling_pronoun_option")  # e.g. "equal to it" with no antecedent in the stem
        if len({_norm(o) for o in opts}) != len(opts): r.append("dup_option")
        if q.endswith("?") is False and "___" not in q and len(q) < 20: r.append("stem_fragment")
        if any(len(o.strip()) == 0 for o in opts): r.append("blank_option")
        lens = [len(o) for o in opts]
        if max(lens) > 6 * max(1, min(lens)) + 40: r.append("option_length_skew")
        if len(a) > 30 and len(a) > 1.8 * max(len(x) for x in d or [""]): r.append("answer_giveaway")  # v14: key is far longer than every distractor (test-wise giveaway)
    else:
        if len(a) < 40: r.append("truncated_answer")
        parts = {m.group(1) for m in PART.finditer(" " + q)}
        if len(parts) >= 2:
            got = set(ANSPART.findall(a))
            if not parts <= got: r.append("answer_misses_part")
        if re.search(r"(NEB|HSEB)\s*20\d\d", a): r.append("provenance_in_answer")
    return r


def run(pid):
    f = f"{R}/docs/packs/{pid}/bank.json"
    B = json.load(open(f, encoding="utf-8")); why = collections.Counter(); keep = []
    for it in B:
        it = repair(it); rs = qa(it)
        for x in rs: why[x] += 1
        if not rs: keep.append(it)
    json.dump(keep, open(f, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    rep = dict(pack=pid, bank_in=len(B), bank_kept=len(keep), dropped=len(B) - len(keep), reasons=dict(why.most_common()),
               mcq=sum(i["type"] == "mcq" for i in keep), written=sum(i["type"] != "mcq" for i in keep),
               units=len({i["unit"] for i in keep}))
    os.makedirs(f"{R}/packs/{pid}", exist_ok=True); json.dump(rep, open(f"{R}/packs/{pid}/bank_qa_report.json", "w"), indent=1)
    return rep


if __name__ == "__main__":
    ids = sys.argv[1:] or [p["pack_id"] for p in json.load(open(f"{R}/docs/packs/pack_registry.json"))["packs"]]
    for p in ids: print(json.dumps(run(p)))
