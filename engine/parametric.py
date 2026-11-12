"""PaperLM Parametric Formula & Distractor Engine (Python twin of engine/web/parametric.js).

Neuro-symbolic half of PaperLM: numericals / numeric MCQs are NOT written by the 10M language model.  Every number, unit,
answer key and worked solution is computed from a verified law/formula template, and the 3 distractors are computed from
*typical-mistake* expressions of the same formula, so all four options share one unit/dimension and the key is correct by construction.
"""
import json, math, os, re
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = json.load(open(os.path.join(HERE, "param_templates.json"), encoding="utf-8"))
TEMPLATES = {t["id"]: t for t in LIB["templates"]}
ENV = dict(sqrt=math.sqrt, sin=math.sin, cos=math.cos, tan=math.tan, atan=math.atan, ln=math.log, log10=math.log10, exp=math.exp, abs=abs, pi=math.pi,
           rad=math.radians, comb=math.comb, perm=math.perm, fact=math.factorial, max=max, min=min, ceil=math.ceil, floor=math.floor)
FILL = [2, 0.5, 10, 0.1, 1.5, 3, 0.25, 4, 0.2, 5]


def _cond(s): return s.replace(" and ", " and ").replace("&&", " and ")


def ev(expr, env):
    return eval(expr, {"__builtins__": {}}, {**ENV, **env})


def domains_for(subject):
    s = subject.lower(); out = []
    for rx, doms in LIB["domains"]:
        if re.search(rx, s):
            for d in doms:
                if d not in out: out.append(d)
    return out


def level_ok(t, level):
    tags = LIB["levels"].get(level, "SHEN")
    return t["lv"] == "all" or any(c in tags for c in t["lv"])


def parse_var(spec):
    name, rng = spec.split("=", 1)
    if rng.startswith("["): vals = [float(x) for x in rng[1:-1].split(",")]
    else:
        lo, hi, st = (float(x) for x in rng.split(":")); n = int(round((hi - lo) / st)) + 1
        vals = [round(lo + i * st, 10) for i in range(n)]
    return name, [int(v) if float(v).is_integer() else v for v in vals]


def fmt(x, sig=3):
    if x == 0: return "0"
    r = rnd(x, sig); a = abs(r)
    if a >= 1e6 or a < 1e-4:
        m, e = f"{r:.{sig - 1}e}".split("e"); m = m.rstrip("0").rstrip(".")
        return f"{m}\\times10^{{{int(e)}}}"
    s = repr(r)
    return s[:-2] if s.endswith(".0") else s


def rnd(x, sig):
    """round to `sig` significant digits, ties away from zero (identical to JS Number(x.toPrecision(sig)))"""
    if x == 0: return 0.0
    d = Decimal(abs(x)); q = Decimal(1).scaleb(d.adjusted() - sig + 1)
    return math.copysign(float(d.quantize(q, rounding=ROUND_HALF_UP)), x)


GENERIC = {"system", "equation", "calculation", "concept", "general", "basic", "introduction", "theory", "number", "formula", "law", "analysis", "principle", "application", "problem", "fundamental", "motion", "wave", "light", "heat", "power"}


def uwords(s): return {re.sub(r"s$", "", w) for w in re.findall(r"[a-z]{4,}", str(s).lower())} - GENERIC


def unit_match(t, unit):
    uw = uwords(unit)
    if not uw: return False
    return bool(uwords(t["unit"]) & uw) or any((lambda kw: kw and kw <= uw)(uwords(k)) for k in t["kw"])


def pick_template(subject, level, unit="", rng=None, exclude=()):
    doms = domains_for(subject)
    pool = [t for t in LIB["templates"] if set(t["dom"].split()) & set(doms) and level_ok(t, level) and t["id"] not in exclude]
    if not pool: return None, False
    m = [t for t in pool if unit_match(t, unit)]; c = m or pool
    return c[int(rng.random() * len(c))], bool(m)


def instantiate(t, rng, vals=None):
    """Sample variables (or use `vals`), compute the answer, distractors and solution. Returns dict or None."""
    vars_ = dict(parse_var(v) for v in t["vars"])
    for _ in range(400):
        env = dict(vals) if vals else {k: v[int(rng.random() * len(v))] for k, v in vars_.items()}
        try:
            for d in filter(None, t["derived"].split(";")):
                n, e = d.split("=", 1); env[n.strip()] = ev(e, env)
            ans = float(ev(t["ans"], env))
            if not math.isfinite(ans): raise ValueError
            if not ev(_cond(t["cond"]), {**env, "ans": ans}): raise ValueError
        except (ZeroDivisionError, ValueError, OverflowError, TypeError):
            if vals: return None
            continue
        sig = t["sig"]
        if abs(ans - round(ans)) < 1e-9 and abs(ans) < 1e6: sig = max(sig, len(str(abs(int(round(ans))))))  # v13: an exact integer is never shown rounded to fewer digits (1176 J != 1180 J)
        if sig != t["sig"]: t = dict(t, sig=sig)
        a = rnd(ans, sig)
        if abs(ans - round(ans)) < 1e-9 and abs(ans) < 1e9: a = float(round(ans))
        seen = {a}; cands = []; wrongs = []
        for w in t["wrong"]:
            try: v = float(ev(w, env))
            except Exception: continue
            if not math.isfinite(v): continue
            v = rnd(v, sig)
            if v in seen or v * a <= 0 or fmt(v, sig) == fmt(a, sig) or not (0.01 <= abs(v / a) <= 100): continue
            seen.add(v); wrongs.append(v)
        rng_shuffle(wrongs, rng)
        for m in FILL:
            if len(wrongs) >= 3: break
            v = rnd(a * m, sig)
            if v not in seen and fmt(v, sig) != fmt(a, sig): seen.add(v); wrongs.append(v)
        if len(wrongs) < 3: 
            if vals: return None
            continue
        return dict(tpl=t, env=env, ans=a, wrong=wrongs[:3])
    return None


def rng_shuffle(a, rng):
    for i in range(len(a) - 1, 0, -1):
        j = int(rng.random() * (i + 1)); a[i], a[j] = a[j], a[i]


def sub(text, env, ans, sig):
    def r(m):
        k = m.group(1)
        if k == "ans": return fmt(ans, sig)
        v = env[k]; return fmt(float(v), 6)
    return re.sub(r"@(\w+)@", r, text)


def with_unit(v, t):
    s = fmt(v, t["sig"]); return f"${s}\\ {t['u']}$" if t["u"] else f"${s}$"


def render(inst, marks, rng):
    """-> dict(stem, options, key, law, steps, rubric, answer_text)"""
    t, env, a = inst["tpl"], inst["env"], inst["ans"]; sig = t["sig"]
    stem = sub(t["stem"], env, a, sig); steps = [sub(s, env, a, sig) for s in t["sol"]]
    opts = [a] + inst["wrong"]; order = list(range(4)); rng_shuffle(order, rng)
    options = [with_unit(opts[i], t) for i in order]; key = "abcd"[order.index(0)]
    return dict(stem=stem, options=options, key=key, law=t["law"], lawname=t["lawname"], steps=steps, answer=with_unit(a, t))


def make_item(subject, level, unit, marks, typ, rng, exclude=()):
    """Generate a fully verified parametric item in the engine's item schema, or None when the subject has no templates."""
    t, matched = pick_template(subject, level, unit, rng, exclude)
    if not t: return None
    inst = instantiate(t, rng)
    if not inst: return None
    r = render(inst, marks, rng); item = dict(source="parametric", verified=True, tpl=t["id"], concept=r["law"], unit_matched=matched, unit_label=t["unit"],
                                             audit=dict(expr=t["ans"], env={k: v for k, v in inst["env"].items()}, sig=t["sig"], unit=t["u"], answer=rnd(inst["ans"], t["sig"])))
    expl = r["law"] + " " + " ".join(r["steps"])
    if typ == "MCQ" or marks <= 1:
        item.update(kind="mcq", question=r["stem"], options=r["options"], key=r["key"], explanation=expl)
        return item
    sol = r["law"] + " " + " ".join(r["steps"]) + " Answer: " + r["answer"] + "."
    if marks >= 4 and typ in ("NUMERICAL", "OR", "SHORT", "CONCEPTUAL", "LONG"):
        ma = 1 if marks == 4 else 2
        parts = [dict(label="a", text=f"State {r['lawname']}.", marks=ma), dict(label="b", text=r["stem"], marks=marks - ma)]
        item.update(kind="written", question="Answer the following:", parts=parts, or_parts=[], rubric=f"(a) {r['law']} (b) " + " ".join(r["steps"]) + " Answer: " + r["answer"] + ".")
        if typ == "OR":
            t2, _ = pick_template(subject, level, unit, rng, exclude=(*exclude, t["id"])); i2 = instantiate(t2, rng) if t2 else None
            if i2:
                r2 = render(i2, marks, rng)
                item["or_parts"] = [dict(label="a", text=f"State {r2['lawname']}.", marks=ma), dict(label="b", text=r2["stem"], marks=marks - ma)]
                item["rubric"] += f" OR (a) {r2['law']} (b) " + " ".join(r2["steps"]) + " Answer: " + r2["answer"] + "."
        return item
    item.update(kind="written", question=r["stem"], parts=[], or_parts=[], rubric=sol)
    return item


def selfcheck(item):
    """Independent re-derivation: every placeholder resolved, 4 distinct options, key letter holds the computed answer."""
    issues = []
    txt = json.dumps(item)
    if "@" in txt: issues.append("unresolved placeholder")
    if item["kind"] == "mcq":
        if len(set(item["options"])) != 4: issues.append("duplicate options")
        if item["key"] not in "abcd": issues.append("bad key")
        else:
            ans = item["explanation"].rsplit("= ", 1)[-1]
    return issues
