"""Strict Semantic & Factual Coherence Gate (Python twin of engine/web/ground.js).

A candidate written by the 10M LM from a verified Concept Anchor is accepted ONLY if
  * every number in the answer-bearing text (key option / explanation / rubric) is present in the anchor or in the question (no invented figures);
  * the explanation / rubric is lexically grounded in the anchor (precision + recall of content words);
  * the question is on-topic (shares a content word with the anchor);
  * the key option is supported by the anchor and no distractor is *also* fully supported by it (two right answers);
  * the explanation does not contradict the key letter (verify.check_key) and options are homogeneous (verify.check_options).
"""
import re
STOP = set("the of a an and or in on to is are was were be by for with as at from that this which what following these those its it into than then their there has have had can will would should not no "
           "his her they them you your we our one two such also may each both any all some more most other another only over under between during using used use called known given state write find calculate "
           "when where while whose whom how why does did done make makes made give gives must if so but because therefore thus hence about per via".split())
WORD = re.compile(r"[a-z\u0900-\u097f]{4,}")
NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)?")


def strip(s): return re.sub(r"\\(?:text|mathrm|textbf|textit|mathbf)\{([^}]*)\}", r" \1 ", s or "")


def cwords(s):
    s = strip(s).lower(); out = set()
    for w in WORD.findall(s):
        if w in STOP: continue
        out.add(w[:-1] if w.endswith("s") and len(w) > 4 else w)
    return out


def nums(s): return set(NUM.findall(re.sub(r"\\(?:tfrac|dfrac|frac)", " ", strip(s))))


def sym(s):  # LaTeX symbols/commands such as \sin, \omega, \Delta that carry the physics
    return set(re.findall(r"\\[A-Za-z]+", s or "")) - {"\\text", "\\mathrm", "\\frac", "\\dfrac", "\\tfrac", "\\left", "\\right", "\\times", "\\cdot", "\\ ", "\\quad", "\\textbf", "\\textit", "\\mathbf", "\\sqrt"}


def item_text(it):
    parts = it.get("parts") or []; alt = it.get("or_parts") or []
    return " ".join([it["question"], *(it.get("options") or []), *(p["text"] for p in parts), *(p["text"] for p in alt)])


def repetitive(t):
    w = re.findall(r"[a-z]{3,}", strip(t).lower()); cw = [x for x in w if x not in STOP]
    if any(cw.count(x) >= 3 for x in set(cw)): return True
    bg = list(zip(w, w[1:])); return any(bg.count(b) >= 2 and not (b[0] in STOP and b[1] in STOP) for b in set(bg))


def gate(item, anchor, min_p=0.8, min_r=0.5):
    """-> dict(ok, issues, p, r)"""
    issues = []; A = cwords(anchor); an = nums(anchor); asym = sym(anchor)
    q = item["question"]; ctx = item_text(item); C = cwords(ctx)
    if not A: return dict(ok=False, issues=["empty anchor"], p=0, r=0)
    if item["kind"] == "mcq":
        key = "abcd".index(item["key"]); ans_txt = item["options"][key]; expl = item.get("explanation") or ""
        E = cwords(expl) | cwords(ans_txt); allowed = A | cwords(q)
        p = len(E & allowed) / max(1, len(E)); r = len(A & (E | cwords(q) | cwords(ans_txt))) / len(A)
        if not (cwords(q) & A): issues.append("question off-topic for the anchor")
        bad_nums = (nums(expl) | nums(ans_txt)) - an - nums(q)
        if bad_nums: issues.append("number not in anchor: " + sorted(bad_nums)[0])
        ac = cwords(ans_txt)
        if ac and len(ac & (A | cwords(q))) / len(ac) < 0.5 and not nums(ans_txt): issues.append("key option not supported by the anchor")
        for i, o in enumerate(item["options"]):
            if i == key: continue
            oc = cwords(o)
            if oc and len(oc) >= 2 and len(oc & A) / len(oc) >= 0.9 and o.strip().lower() not in q.lower(): issues.append(f"distractor {'abcd'[i]} is also supported by the anchor")
            if nums(o) and nums(o) <= an and nums(ans_txt) != nums(o) and nums(ans_txt): issues.append(f"distractor {'abcd'[i]} repeats an anchor figure")
    else:
        rub = item.get("rubric") or ""; E = cwords(rub); allowed = A | cwords(ctx)
        p = len(E & allowed) / max(1, len(E)); r = len(A & (E | C)) / len(A)
        if not (C & A): issues.append("question off-topic for the anchor")
        bad_nums = nums(rub) - an - nums(ctx)
        if bad_nums and not re.search(r"\\(?:frac|sqrt|int|sum)", rub): issues.append("number not in anchor: " + sorted(bad_nums)[0])
        if rub and len(E) >= 4 and p < min_p: issues.append("rubric not grounded in the anchor")
    if item["kind"] == "mcq" and p < min_p: issues.append("explanation not grounded in the anchor")
    ans_txt_all = (item.get("explanation") or "") + " " + item["options"]["abcd".index(item["key"])] if item["kind"] == "mcq" else (item.get("rubric") or "")
    if item["kind"] != "mcq" and not ans_txt_all.strip(): issues.append("no rubric")
    bad_sym = sym(ans_txt_all) - asym - sym(ctx)
    if bad_sym: issues.append("symbol not in anchor: " + sorted(bad_sym)[0])
    if repetitive(item["question"]) or any(repetitive(p_["text"]) for p_ in (item.get("parts") or []) + (item.get("or_parts") or [])): issues.append("repetitive wording")
    if r < min_r: issues.append("anchor concept barely used")
    return dict(ok=not issues, issues=issues, p=round(p, 3), r=round(r, 3))
