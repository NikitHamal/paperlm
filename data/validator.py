"""PaperLM validator — the SINGLE source of truth for "no mess" guarantees.

Used by (1) the gold dataset builder (reject dirty training items) and (2) the PaperSetterEngine
(reject / repair generated items).  A JS and Kotlin port with identical rules ships in engine/web and engine/android.
"""
import re, unicodedata

ALLOWED_EXTRA = set("°×÷±≤≥≠≈≡∝πΩμαβγδεζηθλρστφχψωΔΘΛΣΦΨΓΠ√∞∂∫∑∈∉∪∩⊂⊆⊄→←↔⇒⇌↑↓∴∵·•′″‰℃℉Å²³⁴⁵⁶⁷⁸⁹⁰¹⁻⁺₀₁₂₃₄₅₆₇₈₉ₙ½¼¾€£₹ʹ…–—§")
DEV = range(0x0900, 0x0980)

def char_ok(c):
    o = ord(c)
    return (32 <= o < 127) or c in ALLOWED_EXTRA or o in DEV or c in "éèêçñüöäÉ"

QUOTE_MAP = {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u00a0": " ", "\u2009": " ", "\u202f": " ",
             "\u2212": "-", "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u200b": "", "\ufeff": "", "\u2022": "·", "\u00b5": "μ",
             "\u03bc": "μ", "\u2032": "′", "\u2033": "″", "\u2264": "≤", "\u2265": "≥"}

def normalize(t):
    t = unicodedata.normalize("NFC", t)
    for k, v in QUOTE_MAP.items(): t = t.replace(k, v)
    t = re.sub(r"\s+", " ", t).strip()
    return t

KNOWN_CMDS = set(r"""frac dfrac tfrac sqrt text textbf textit mathrm mathbf mathbb mathcal mathit left right cdot times div pm mp
leq geq neq approx equiv propto infty partial nabla int iint oint sum prod lim log ln sin cos tan cot sec csc sinh cosh tanh arcsin arccos arctan
alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta lambda mu nu xi pi rho sigma tau phi varphi chi psi omega
Gamma Delta Theta Lambda Xi Pi Sigma Phi Psi Omega vec hat bar overline underline dot ddot tilde
rightarrow leftarrow Rightarrow Leftarrow leftrightarrow Leftrightarrow rightleftharpoons to implies iff uparrow downarrow
degree circ angle perp parallel triangle therefore because in notin subset subseteq cup cap emptyset setminus forall exists neg land lor
ldots cdots dots quad qquad ce begin end hline binom choose mid lt gt le ge ne
displaystyle boxed cancel underbrace overbrace operatorname ang bigg Big big Bigg lbrace rbrace langle rangle lceil rceil lfloor rfloor
max min det mathrm sgn gcd lcm hbar ell Re Im prime star ast oplus otimes odot sim simeq cong mapsto
arg exp deg dim ker""".split())

TWO_ARG = {"frac", "dfrac", "tfrac", "binom"}
DISALLOWED_HTML = re.compile(r"</?[a-zA-Z][^>]*>|&[a-z]+;|&#\d+;")
MD_JUNK = re.compile(r"\*\*|__|`|^#{1,6}\s|\[\[|\]\]|@mcq|@opts|@q\b|@s\b|:::")

def _split_math(t):
    """Return (outside_text_chunks, math_chunks) or raise ValueError on unbalanced $."""
    outs, maths, i, n, buf = [], [], 0, len(t), []
    while i < n:
        c = t[i]
        if c == "\\" and i + 1 < n and t[i + 1] == "$":
            buf.append("$"); i += 2; continue
        if c == "$":
            disp = t.startswith("$$", i)
            d = "$$" if disp else "$"
            j = i + len(d)
            k = j
            while True:
                k = t.find(d, k)
                if k < 0: raise ValueError("unbalanced $")
                if t[k - 1] == "\\": k += 1; continue
                break
            outs.append("".join(buf)); buf = []
            maths.append(t[j:k]); i = k + len(d); continue
        buf.append(c); i += 1
    outs.append("".join(buf))
    return outs, maths

def check_math(m):
    """Validate a single math segment; return error string or None."""
    s = m.strip()
    if not s: return "empty math"
    depth, i, n = 0, 0, len(s)
    stack_env, left, right = [], 0, 0
    while i < n:
        c = s[i]
        if c == "\\":
            mm = re.match(r"\\([A-Za-z]+)", s[i:])
            if mm:
                cmd = mm.group(1)
                if cmd not in KNOWN_CMDS: return f"unknown cmd \\{cmd}"
                j = i + len(mm.group(0))
                if cmd == "left": left += 1
                elif cmd == "right": right += 1
                elif cmd in ("begin", "end"):
                    e = re.match(r"\{([A-Za-z*]+)\}", s[j:])
                    if not e: return "bad begin/end"
                    if cmd == "begin": stack_env.append(e.group(1))
                    else:
                        if not stack_env or stack_env.pop() != e.group(1): return "env mismatch"
                    j += len(e.group(0))
                elif cmd in TWO_ARG:
                    r = _need_groups(s, j, 2)
                    if r is None: return f"\\{cmd} needs 2 args"
                    j = r
                elif cmd in ("sqrt",):
                    r2 = j
                    if r2 < n and s[r2] == "[":
                        e = s.find("]", r2)
                        if e < 0: return "sqrt bracket"
                        r2 = e + 1
                    r = _need_groups(s, r2, 1)
                    if r is None: return "\\sqrt needs arg"
                    j = r2
                elif cmd in ("vec", "hat", "bar", "overline", "underline", "dot", "ddot", "tilde", "text", "textbf", "textit", "mathrm", "mathbf", "mathbb", "mathcal", "mathit", "operatorname", "boxed", "cancel", "ce"):
                    if _need_groups(s, j, 1) is None: return f"\\{cmd} needs arg"
                i = j; continue
            else:
                if i + 1 >= n: return "dangling backslash"
                if s[i + 1] not in "\\{}%&_#,;:! ^'\"|.()[]/<>=-+0123456789": return "bad escape"
                i += 2; continue
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth < 0: return "brace underflow"
        i += 1
    if depth != 0: return "unbalanced braces"
    if left != right: return "left/right mismatch"
    if stack_env: return "unclosed env"
    if re.search(r"(?<!\\)[\^_]\s*$", s): return "dangling ^/_"
    if re.search(r"(?<!\\)[\^_]\s*[\^_]", s) : return "double ^/_"
    if re.search(r"\^\{\}|_\{\}", s): return "empty script"
    if re.search(r"\\frac\s*\{\s*\}|\{\s*\}\s*\{\s*\}", s): return "empty group"
    return None

def _need_groups(s, j, k):
    n = len(s)
    for _ in range(k):
        while j < n and s[j] == " ": j += 1
        if j >= n: return None
        if s[j] == "{":
            d = 0
            while j < n:
                if s[j] == "{": d += 1
                elif s[j] == "}":
                    d -= 1
                    if d == 0: j += 1; break
                elif s[j] == "\\": j += 1
                j += 1
            else:
                return None
        elif s[j] == "\\":
            mm = re.match(r"\\[A-Za-z]+", s[j:])
            j += len(mm.group(0)) if mm else 2
        else:
            j += 1
    return j

def check_text(t, allow_empty=False):
    """Return None if clean, else short reason string."""
    if not t.strip(): return None if allow_empty else "empty"
    if "\ufffd" in t or "\x00" in t: return "replacement char"
    for c in t:
        if not char_ok(c): return f"bad char U+{ord(c):04X}"
    if DISALLOWED_HTML.search(t): return "html residue"
    if MD_JUNK.search(t): return "markdown residue"
    try:
        outs, maths = _split_math(t)
    except ValueError:
        return "unbalanced $"
    for m in maths:
        e = check_math(m)
        if e: return "math: " + e
    outside = " ".join(outs)
    if re.search(r"[\\{}^_]", outside.replace("_", "") if False else re.sub(r"\w_\w", "", outside)): return "stray tex outside math"
    if outside.count("(") != outside.count(")") and abs(outside.count("(") - outside.count(")")) > 0 and not re.search(r"\b[a-d]\)|\([a-d]\b|\b[ivx]+\)", outside):
        return "unbalanced parens"
    if re.search(r"(.{3,}?)\1{4,}", t): return "repetition"
    words = t.split()
    for i in range(0, max(0, len(words) - 24)):
        pass
    grams = {}
    for i in range(len(words) - 5):
        g = " ".join(words[i:i + 6]); grams[g] = grams.get(g, 0) + 1
        if grams[g] >= 3: return "ngram loop"
    return None

VISUAL_REF = re.compile(r"\b(in|from|of|using|see|refer to) (the )?(given |above |following |adjoining )?(figure|fig\.?|diagram|graph|table|circuit|picture|image|map|chart)\b|\b(figure|fig\.?)\s*\(?\d|\bshown (in|below|above)\b|\b(given|following|adjoining) (figure|diagram|graph|table|circuit|picture|map|chart|data)\b|\b(below|above) (figure|diagram|graph|table|circuit)\b|\bpassage\b|\bparagraph (below|above)\b|\bpoem\b|\bread the (following|text)", re.I)

def needs_visual(t):
    return bool(VISUAL_REF.search(t))

ANS_OK = set("abcd")

def check_mcq(q, opts, key, why=""):
    e = check_text(q)
    if e: return "q:" + e
    if len(opts) != 4: return "opts!=4"
    norm = []
    for o in opts:
        e = check_text(o)
        if e: return "opt:" + e
        if len(o) > 160: return "opt too long"
        norm.append(re.sub(r"\W+", "", o.lower()))
    if len(set(norm)) != 4: return "duplicate options"
    if key not in ANS_OK: return "bad key"
    if why:
        e = check_text(why)
        if e: return "why:" + e
    if len(q) < 8 or len(q) > 600: return "q length"
    return None

def check_written(stem, parts, alt_parts, marks, sol=""):
    texts = [stem] + [p[1] for p in parts] + [p[1] for p in alt_parts]
    if not any(t.strip() for t in texts): return "empty"
    for t in texts:
        e = check_text(t, allow_empty=True)
        if e: return "q:" + e
    if sol:
        e = check_text(sol)
        if e: return "sol:" + e
    body = " ".join(texts)
    if len(body) < 12 or len(body) > 1400: return "q length"
    for plist in (parts, alt_parts):
        labels = [p[0] for p in plist if p[0]]
        if labels and labels != [chr(ord("a") + i) for i in range(len(labels))]: return "part labels"
    if marks < 1 or marks > 20: return "marks"
    return None

def validate_item_text(item_text):
    """Final structural check on a rendered training/generated item string (special tokens as <|..|>)."""
    if not item_text.startswith("<|bos|>") or not item_text.endswith("<|end|>"): return "frame"
    if item_text.count("<|q|>") != 1: return "q tag"
    segs = re.split(r"(<\|[a-z0-9_=.\-]+\|>)", item_text)
    for s in segs:
        if s and not s.startswith("<|"):
            e = check_text(s, allow_empty=True)
            if e: return e
    return None
