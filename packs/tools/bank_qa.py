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


def repair(it):
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


def qa(it):
    r = []
    q, a = it.get("question", "").strip(), it.get("answer", "").strip()
    if len(q) < 12: r.append("empty_or_tiny_stem")
    if not a: r.append("no_answer")
    if not _tex_ok(q + " " + a + " " + it.get("why", "")): r.append("latex")
    if it["type"] == "mcq":
        d = it.get("distractors", [])
        opts = [a] + d
        if len(d) != 3: r.append("n_options")
        if len({_norm(o) for o in opts}) != len(opts): r.append("dup_option")
        if q.endswith("?") is False and "___" not in q and len(q) < 20: r.append("stem_fragment")
        if any(len(o.strip()) == 0 for o in opts): r.append("blank_option")
        lens = [len(o) for o in opts]
        if max(lens) > 6 * max(1, min(lens)) + 40: r.append("option_length_skew")
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
