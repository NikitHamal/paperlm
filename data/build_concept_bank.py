#!/usr/bin/env python3
"""Build data/concept_bank.json: verified syllabus concept / formula / definition anchors.
Sources (all already audited, no free-form LM output):
  law      : 139 parametric templates (engine/param_templates.json): law text + formula-bearing worked solution
  fact     : 52 closed-world fact classes (docs/model/facts.json): (subject, key, value, one-line explanation)
  exam     : explanation sentences of gold exam MCQs (bank seeds) -> the exact fact the question tests
Each concept: {id, k:kind, b:board|level|subject, u:unit, t:text, f:formula(latex)|null, kw:[keywords]}.
The file is the retrieval index used to prefix `<|concept=...|>` for PaperLM conditional generation and to ground the gate."""
import json, re, sys, hashlib

bank = json.load(open("docs/model/bank.json")); tpl = json.load(open("docs/model/templates.json")); facts = json.load(open("docs/model/facts.json"))
STOP = set("the of a an and or in on to is are was were be by for with as at from that this which what following these those its it into than then their there has have had can will would should not no".split())
kw = lambda s: sorted({w for w in re.findall(r"[a-z]{4,}", re.sub(r"\$[^$]*\$", " ", s.lower())) if w not in STOP})[:12]
out = []; seen = set()


def add(kind, b, u, t, f=None):
    t = re.sub(r"\s+", " ", t).strip()
    h = hashlib.md5((kind + b + u + t).encode()).hexdigest()[:10]
    if len(t) < 40 or h in seen: return
    seen.add(h); out.append(dict(id=h, k=kind, b=b, u=u, t=t, f=f, kw=kw(t + " " + u)))


for t in tpl["templates"]:
    f = next((s for s in t.get("sol", []) if "=" in s), None)
    add("law", f"*|{t['lv']}|{t['dom']}", t["unit"], t.get("law", ""), f)
for c in facts["classes"]:
    subj = (c.get("subjects") or ["*"])[0]; u = (c.get("units") or [c["label"]])[0]
    for p in c["pairs"]:
        if len(p) >= 3: add("fact", f"*|*|{subj}", c["label"], f"{p[0]}: {p[1]}. {p[2]}")
for sk, us in bank["seeds"].items():
    for u, its in us.items():
        for it in its:
            if it.get("c") == "mcq" and it.get("w") and len(it["w"]) >= 40:
                ko = it["o"]["abcd".index(it["k"])] if it.get("k") in "abcd" and len(it.get("o") or []) == 4 else ""
                if ko: add("exam", sk, u, f"{it['q'].strip()} Answer: {ko}. {it['w'].strip()}")
for sk, us in bank["seeds"].items():
    for u, its in us.items():
        for it in its:
            if it.get("c") != "mcq" and it.get("r") and len(it["r"]) >= 60:
                qq = (it.get("q") or "").strip() or " ".join(p[1] for p in (it.get("p") or [])[:2])
                if len(qq) >= 15: add("exam", sk, u, f"{qq[:220]} Model answer: {it['r'].strip()[:320]}")
json.dump(dict(version="concept_bank_v1", n=len(out), kinds={k: sum(1 for c in out if c["k"] == k) for k in ("law", "fact", "exam")}, concepts=out), open("data/concept_bank.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(out), {k: sum(1 for c in out if c["k"] == k) for k in ("law", "fact", "exam")})
