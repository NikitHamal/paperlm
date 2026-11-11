"""PaperLM verification layer (Python twin of engine/web/verify.js): symbol cleanup, MCQ homogeneity, key consistency,
arithmetic self-consistency, concept anchoring.  Used by the engine, the benchmark, dataset filtering and rejection sampling."""
import re
WORD = re.compile(r"[A-Za-z\u0900-\u097F]{2,}")
STOP = set("the of a an and or in on to is are was were be by for with as at from that this which what following these those its it into than then their there has have had can will would should not no all any each one two three four give write state define explain find calculate prove show using used use following correct incorrect true false value values".split())

def clean_symbols(t):
    if not t: return t
    out, i = [], 0
    while i < len(t):
        if t[i] == "$":
            d = "$$" if t.startswith("$$", i) else "$"; k = t.find(d, i + len(d))
            if k < 0: out.append(t[i:]); break
            m = t[i + len(d):k]
            m = re.sub(r"\\leqslant|\\leq(?![A-Za-z])|\\le(?![A-Za-z])", r"\\leq", m); m = re.sub(r"\\geqslant|\\geq(?![A-Za-z])|\\ge(?![A-Za-z])", r"\\geq", m)
            m = m.replace("<=", "\\leq ").replace(">=", "\\geq ").replace("!=", "\\neq "); m = re.sub(r"\s{2,}", " ", m).strip()
            out.append(d + m + d); i = k + len(d)
        else:
            j = t.find("$", i); j = len(t) if j < 0 else j
            out.append(t[i:j].replace("<=", "\u2264").replace(">=", "\u2265").replace("!=", "\u2260")); i = j
    s = "".join(out); s = re.sub(r" {2,}", " ", s); s = re.sub(r"\$ +\$", " ", s); s = re.sub(r" +([,.;:?])", r"\1", s); return s.strip()

def strip_math(s): return s.replace("$$", "").replace("$", "")
NUM = r"-?\d+(?:\.\d+)?(?:\s*\\times\s*10\^\{?-?\d+\}?)?"
def units(s):
    u = [re.sub(r"\s+", "", m.group(1)).lower() for m in re.finditer(r"\\(?:text|mathrm)\{\s*([^}]*)\}", s)]
    nu = re.search(r"\d\s*\}?\s*(?:\\,|\\ |\s)*([A-Za-z]{1,3}(?:/[A-Za-z]{1,3})?(?:\^\{?-?\d\}?)?)\s*$", strip_math(s).strip())
    if nu and not re.match(r"^(and|or|is|a)$", nu.group(1), re.I): u.append(nu.group(1).lower())
    if "^\\circ" in s or "\u00b0" in s: u.append("deg")
    if "%" in s: u.append("%")
    return "|".join(u)
def shape(opt):
    raw = opt.strip(); no_m = re.sub(r"\s+", " ", re.sub(r"\$[^$]*\$", " ", raw)).strip(); words = len(WORD.findall(no_m))
    has_math = "$" in raw; body = strip_math(raw).strip(); digits = bool(re.search(r"\d", body))
    numeric = digits and bool(re.match(r"^[^A-Za-z]*" + NUM + r"[^A-Za-z]*(?:\\(?:text|mathrm)\{[^}]*\})?[^A-Za-z]*[A-Za-z%/^{}\-\d\\ ,]*$", body)) and words <= 1
    cls = "text" if words >= 3 else "num" if numeric else "expr" if has_math or re.search(r"[=+\-*/^]", body) else "word"
    return dict(cls=cls, words=words, len=len(raw), unit=units(raw), digits=digits, numeric=numeric, body=body)
def num_val(s):
    m = re.search(r"(-?\d+(?:\.\d+)?)", re.sub(r",(?=\d{3})", "", strip_math(s))); return float(m.group(1)) if m else None
def norm_t(s): return re.sub(r"[^a-z0-9\u0900-\u097F]+", "", s.lower())

def check_options(opts, question=""):
    issues = []; sh = [shape(o) for o in opts]
    classes = {("math" if s["cls"] in ("num", "expr") else "text" if s["cls"] in ("text", "word") else s["cls"]) for s in sh}
    if len(classes) > 1: issues.append("option kinds differ (" + "/".join(sorted(classes)) + ")")
    nums = [s for s in sh if s["cls"] == "num"]
    if len(nums) >= 2 and len({s["unit"] for s in nums}) > 1 and len(nums) == 4: issues.append("option units differ")
    with_u = sum(1 for s in sh if s["unit"])
    if with_u and with_u < 4 and all(s["digits"] for s in sh): issues.append("some options lack the unit")
    lens = [max(1, s["len"]) for s in sh]
    if max(lens) / min(lens) > (6 if "text" in classes else 12): issues.append("option length mismatch")
    if all(s["cls"] == "num" for s in sh):
        v = [num_val(s["body"]) for s in sh]
        if len({str(x) for x in v}) < 4: issues.append("numeric duplicates")
    sub = [set(m[0] + m[1] for m in re.findall(r"([A-Za-z])_\{?(\w)\}?", o)) for o in opts]
    qs = set(m[0] + m[1] for m in re.findall(r"([A-Za-z])_\{?(\w)\}?", question))
    for i, s in enumerate(sub):
        for sym in s:
            if sym not in qs and not any(sym in x for j, x in enumerate(sub) if j != i) and any(len(x) == 0 for j, x in enumerate(sub) if j != i): issues.append("foreign symbol " + sym)
    if sum(1 for o in opts if re.search(r"(all|none) of the above", o, re.I)) > 1: issues.append("duplicate catch-all")
    return issues

def check_key(opts, key, why):
    issues = []; k = "abcd".find(key)
    if k < 0: return ["bad key"]
    if not why: return issues
    wn = norm_t(strip_math(why)); hits = [len(norm_t(strip_math(o))) >= 2 and norm_t(strip_math(o)) in wn for o in opts]
    if any(hits) and not hits[k]: issues.append("explanation names a different option than the key")
    nums = [float(m) for m in re.findall(r"=\s*(-?\d+(?:\.\d+)?)", re.sub(r",(?=\d{3})", "", strip_math(why)))]
    if nums:
        last = nums[-1]; ov = [num_val(o) for o in opts]
        hit = [i for i, v in enumerate(ov) if v is not None and abs(v - last) <= 1e-9 + 1e-6 * abs(last)]
        if len(hit) == 1 and hit[0] != k and all(shape(o)["digits"] for o in opts): issues.append(f"computed value matches option {'abcd'[hit[0]]}, key is {key}")
    return issues

_ARITH = re.compile(r"(?<![A-Za-z0-9_^{.\\])(-?\d+(?:\.\d+)?(?:\s*(?:\\times|\\cdot|\\div|\+|-|\*|/)\s*\d+(?:\.\d+)?)+)\s*=\s*(-?\d+(?:\.\d+)?)(?![\d.]*[A-Za-z\^_/{])")
def _eval(expr):
    e = expr.replace("\\times", "*").replace("\\cdot", "*").replace("\\div", "/")
    if not re.fullmatch(r"[\d.\s+\-*/]+", e): return None
    try: return eval(e, {"__builtins__": {}}, {})
    except Exception: return None
def check_arith(text):
    """every 'a op b ... = c' chain made only of plain numbers must be numerically right (2% tolerance for rounding)"""
    bad = []; t = strip_math(text); t = re.sub(r"\\(?:text|mathrm)\{[^}]*\}", " ", t)
    for m in _ARITH.finditer(t):
        v = _eval(m.group(1)); c = float(m.group(2))
        if v is None: continue
        if abs(v - c) > max(0.02 * abs(v), 0.0105): bad.append(f"{m.group(1).strip()} = {m.group(2)} (is {v:.4g})")
    return bad

def words(s): return [w for w in WORD.findall(strip_math(s).lower()) if w not in STOP]
def anchor_score(text, unit, lexicon):
    ws = set(words(text))
    if not ws: return dict(score=0, hits=0, lex=0)
    uw = [w for w in words(unit or "") if not re.match(r"^(unit|paper|model|question|set|general|stream|chapter)$", w)]
    hits = sum(1 for w in uw if w in ws); lex = sum(1 for w in ws if lexicon and w in lexicon)
    return dict(score=(0.5 if hits else 0) + min(1, lex / 3) * 0.5, hits=hits, lex=lex)

def verify_item(item, unit="", lexicon=None, strict_anchor=False):
    issues = []; score = 1.0
    parts = item.get("parts") or []; alt = item.get("or_parts") or []
    text = " ".join([item["question"], *(item.get("options") or []), item.get("explanation") or "", *(p["text"] for p in parts), *(p["text"] for p in alt), item.get("rubric") or ""])
    if item["kind"] == "mcq":
        if len(words(item["question"])) < 2: issues.append("question too short")
        issues += check_options(item["options"], item["question"]); issues += check_key(item["options"], item["key"], item.get("explanation"))
        if not item.get("explanation"): score -= 0.15
    else:
        if len(words(item["question"] + " " + " ".join(p["text"] for p in parts))) < 3: issues.append("written item too short")
        if any(len(p["text"]) < 8 for p in parts): issues.append("part too short")
        if len(parts) > 6: issues.append("too many parts")
    bad = check_arith(text)
    if bad: issues.append("arithmetic error: " + bad[0])
    a = anchor_score(text, unit, lexicon); score = score * 0.6 + a["score"] * 0.4
    if strict_anchor and lexicon and len(lexicon) > 50 and a["lex"] == 0 and len(words(text)) > 8: issues.append("no syllabus concept in item")
    if re.search(r"(.)\1{5,}", text): issues.append("character run")
    return dict(ok=not issues, issues=issues, score=round(score, 3), anchor=a)

def parse_schema(txt):
    """schema line (<|..|> tags) -> item dict for verify_item; None if it does not parse"""
    m = re.search(r"<\|marks=(\d+)\|><\|type=(\w+)\|><\|q\|>(.*?)(?:<\|end\|>|$)", txt, re.S)
    if not m: return None
    body = m.group(3)
    if "<|oa|>" in body:
        mm = re.match(r"(.*?)<\|oa\|>(.*?)<\|ob\|>(.*?)<\|oc\|>(.*?)<\|od\|>(.*?)<\|ans\|>([abcd])(?:<\|why\|>(.*))?$", body, re.S)
        if not mm: return None
        return dict(kind="mcq", question=mm.group(1).strip(), options=[mm.group(i).strip() for i in (2, 3, 4, 5)], key=mm.group(6), explanation=(mm.group(7) or "").strip())
    sol = ""
    if "<|sol|>" in body: body, sol = body.split("<|sol|>", 1)
    alt = []
    if "<|or|>" in body: body, a = body.split("<|or|>", 1); alt = a
    def parts(s):
        out = []
        for seg in s.split("<|part|>")[1:]:
            t, _, pm = seg.partition("<|pm|>"); t = re.sub(r"^\([a-z]\)\s*", "", t.strip()); out.append(dict(label="", text=t, marks=int(pm) if pm.strip().isdigit() else 0))
        return out
    stem, _, rest = body.partition("<|part|>")
    return dict(kind="written", question=stem.strip(), parts=parts("<|part|>" + rest) if rest else [], or_parts=parts(alt) if alt else [], rubric=sol.strip())
