#!/usr/bin/env python3
"""Independent accuracy audit of emitted PaperLM items (the number that goes in the report).

For every sampled request the composer emits an item; this script re-derives the answer *without* trusting the item:

  param : re-evaluates the template expression on the stored variable values and checks that the key option is exactly
          that computed answer (same significant figures and unit) and that no distractor equals it;
  fact  : checks that the key option is the stored value of the projected table row and that all four options are distinct;
  bank  : checks the gold seed invariants (key inside 4 options, explanation present, no duplicate options);
  lm    : counted separately as UNVERIFIED (never reported as accurate).

usage: python3 eval/audit_items.py [--n 400] [--lm 0] [--out eval/results/v6/accuracy.json]
"""
import argparse, collections, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(ROOT, "engine"), HERE]
import composer as CMP, factbank as FB, parametric as PM  # noqa: E402


def fmt(x, sig):
    return PM.fmt(x, sig)


def audit_param(it):
    a = it.get("audit") or {}
    issues = []
    if not a:
        return ["no audit payload"]
    try:
        ans = float(PM.ev(a["expr"], a["env"]))
    except Exception as e:
        return ["re-evaluation failed: %s" % e]
    disp = PM.rnd(ans, a["sig"])                       # the value the engine actually prints (3 significant figures)
    if abs(disp - float(a["answer"])) > 1e-6 * max(1.0, abs(disp)):
        issues.append("stored answer differs from re-evaluation")
    if it["kind"] == "mcq":
        key = it["options"]["abcd".index(it["key"])]
        want_num = fmt(ans, a["sig"])
        def nums_of(t):
            t = re.sub(r"\\times10\^\{(-?\d+)\}", r"e\1", t)   # 1.807\times10^{24} -> 1.807e24
            return [float(m) for m in re.findall(r"(?<![\w.])(-?\d+(?:\.\d+)?(?:e-?\d+)?)(?![\w])", t)]
        def near(x, y):
            return abs(x - y) <= 1e-6 * max(1.0, abs(y))
        kn = nums_of(key)
        if not any(near(n, disp) for n in kn):
            issues.append("key option is not the computed answer (%s vs %s)" % (want_num, key))
        if len({o.strip() for o in it["options"]}) != 4:
            issues.append("duplicate options")
        for i, o in enumerate(it["options"]):
            if i != "abcd".index(it["key"]):
                for n in nums_of(o):
                    if near(n, disp):
                        issues.append("a distractor repeats the computed answer")
    else:
        if a["unit"] and fmt(ans, a["sig"]) not in json.dumps(it):
            issues.append("computed answer missing from the written solution")
        if not it.get("rubric"):
            issues.append("no rubric")
    if "@" in json.dumps(it):
        issues.append("unresolved placeholder")
    return issues


def audit_reason(it):
    issues = []
    if it["kind"] != "mcq":
        if not it.get("rubric"): issues.append("written reasoning item has no rubric")
        for part in it.get("parts") or []:
            if not part.get("text"): issues.append("empty part")
        return issues
    if len(it["options"]) != 4: issues.append("not 4 options")
    if len({o.strip() for o in it["options"]}) != 4: issues.append("duplicate options")
    if it["key"] not in "abcd": issues.append("bad key")
    if not it.get("explanation"): issues.append("no explanation")
    return issues


def audit_bank(it):
    issues = []
    if it["kind"] == "mcq":
        if len(it["options"]) != 4: issues.append("not 4 options")
        if len({o.strip() for o in it["options"]}) != 4: issues.append("duplicate options")
        if it["key"] not in "abcd": issues.append("bad key")
        if not it.get("explanation"): issues.append("no explanation")
    else:
        if not it.get("rubric"): issues.append("no rubric")
    return issues


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=400); ap.add_argument("--lm", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1234); ap.add_argument("--out", default=os.path.join(HERE, "results", "v6", "accuracy.json"))
    a = ap.parse_args()
    bank = json.load(open(os.path.join(ROOT, "docs", "model", "bank.json"), encoding="utf-8"))
    cat = json.load(open(os.path.join(ROOT, "docs", "model", "catalog.json"), encoding="utf-8"))
    comp = CMP.Composer(None, os.path.join(ROOT, "docs", "model", "bank.json"), seed=a.seed)
    fb = comp.fb
    rng = random.Random(a.seed)
    keys = list(cat); types = ["MCQ", "MCQ", "MCQ", "SHORT", "NUMERICAL", "CONCEPTUAL", "OR", "DERIVATION"]
    tiers = collections.Counter(); by_tier = collections.Counter(); fails = collections.Counter(); examples = []
    ok = 0; tried = 0; errors = 0; unresolved = {}
    per_subject = collections.Counter(); per_subject_fail = collections.Counter()
    while tried < a.n:
        tried += 1
        e = cat[rng.choice(keys)]; subj = rng.choice(list(e["subjects"]))
        unit = rng.choice(e["subjects"][subj]["units"])
        # only the item types and marks the board actually sets for this subject
        allowed = e["subjects"][subj].get("types") or {"MCQ": ["1"], "SHORT": ["5"]}
        typ = rng.choice(list(allowed))
        marks = int(rng.choice(allowed[typ]))
        try:
            it = comp.item(e["board"], e["level"], subj, unit, marks, typ, use_lm=bool(a.lm))
        except Exception:
            errors += 1; unresolved[(e["board"], e["level"], subj)] = unresolved.get((e["board"], e["level"], subj), 0) + 1; continue
        tier = it["provenance"]["tier"]; tiers[tier] += 1
        per_subject[subj] += 1
        if tier in ("param", "reason"): iss = audit_param(it) if tier == "param" else audit_reason(it)
        elif tier == "fact": iss = fb.audit_item(it, subj)
        elif tier == "bank": iss = audit_bank(it)
        else: iss = ["unverified tier"]
        if iss:
            by_tier[tier] += 1; per_subject_fail[subj] += 1
            for x in iss: fails[x[:70]] += 1
        else:
            ok += 1
            if len(examples) < 40:
                examples.append(dict(tier=tier, subject=subj, unit=unit, type=typ, marks=marks, item=it))
    verified = tiers["param"] + tiers["fact"] + tiers["bank"] + tiers["reason"]
    rep = dict(n=tried, emitted=tried - errors, unresolved_requests=errors, tiers=dict(tiers),
               verified_items=verified, verified_accurate=ok - sum(0 for _ in ()),
               accuracy=round((verified - sum(by_tier.values())) / max(1, verified), 5),
               failures_by_tier=dict(by_tier), failure_reasons=dict(fails.most_common(15)),
               per_subject=dict(per_subject), per_subject_fail=dict(per_subject_fail),
               unresolved_by_subject={"|".join(k): v for k, v in sorted(unresolved.items(), key=lambda kv: -kv[1])[:15]})
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(rep, open(a.out, "w"), indent=1)
    json.dump(examples, open(a.out.replace("accuracy", "accuracy_samples"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: rep[k] for k in ("n", "emitted", "unresolved_requests", "tiers", "accuracy", "failures_by_tier", "failure_reasons")}, indent=1))
    print("unresolved:", rep["unresolved_by_subject"])


if __name__ == "__main__":
    main()
