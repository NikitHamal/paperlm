#!/usr/bin/env python3
"""Build docs/model/facts.json from the curated closed-world tables in data/facts_*.py.

Every emitted question is a row of a table:
  forward  : asks for the value, given the key        (answer = value)
  reverse  : asks for the key, given the value        (answer = key, only when the class defines qb)
  written  : asks the open question qo, answered by the row's definition
Distractors are always the values (or keys) of *other* rows of the same class, chosen so that no two options
share a value: two options can therefore never both be correct.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fact_classes import CLASSES  # noqa: E402
from fact_units import UNIT_KEYWORDS  # noqa: E402

DOCS = os.path.join(HERE, "..", "docs", "model", "facts.json")


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())


def latex_ok(s):
    if s.count("$") % 2:
        return False
    depth = 0
    for ch in s:
        depth += ch == "{"
        depth -= ch == "}"
        if depth < 0:
            return False
    return depth == 0


def main():
    out = []
    problems = []
    seen_ids = set()
    for c in CLASSES:
        cid = c["id"]
        if cid in seen_ids:
            problems.append(f"{cid}: duplicate class id")
        seen_ids.add(cid)
        rows = c["pairs"]
        if len(rows) < 4:
            problems.append(f"{cid}: needs at least 4 rows for 4 options (has {len(rows)})")
        ks = [norm(r[0]) for r in rows]
        if c.get("qb") and len(set(ks)) != len(ks):
            problems.append(f"{cid}: duplicate keys (needed for reverse questions)")
        vs = [norm(r[1]) for r in rows]
        if len(set(vs)) != len(vs) and not c.get("qb"):
            pass  # forward-only classes may repeat a value; distractors still come from other values
        for k, v, d in rows:
            for name, txt in (("key", k), ("value", v), ("definition", d)):
                if not str(txt).strip():
                    problems.append(f"{cid}/{k}: empty {name}")
                if not latex_ok(str(txt)):
                    problems.append(f"{cid}/{k}: unbalanced LaTeX in {name}")
            if "{" in str(v) and re.search(r"\{(k|v)\}", str(v)):
                problems.append(f"{cid}/{k}: placeholder inside value")
        for tpl_name in ("qa", "qb", "qo"):
            tpl = c.get(tpl_name)
            if not tpl:
                continue
            if "{k}" not in tpl and "{v}" not in tpl and tpl_name != "qb":
                problems.append(f"{cid}: {tpl_name} has no {{k}} placeholder")
            if tpl_name == "qb" and "{v}" not in tpl:
                problems.append(f"{cid}: qb has no {{v}} placeholder")
            if not tpl.rstrip().endswith(("?", ".")):
                problems.append(f"{cid}: {tpl_name} does not end with ? or .")
        out.append(dict(id=cid, subjects=c["subjects"], units=UNIT_KEYWORDS.get(cid, c["units"]), label=c["label"],
                        qa=c["qa"], qb=c["qb"], qo=c["qo"], src=c["src"],
                        pairs=[[str(k), str(v), str(d)] for k, v, d in rows]))
    if problems:
        print("REFUSING TO BUILD — %d problem(s):" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    doc = dict(version=1, classes=out,
               stats=dict(classes=len(out), rows=sum(len(c["pairs"]) for c in out),
                          mcq_forward=sum(len(c["pairs"]) for c in out),
                          mcq_reverse=sum(len(c["pairs"]) for c in out if c["qb"]),
                          written=sum(len(c["pairs"]) for c in out)))
    os.makedirs(os.path.dirname(DOCS), exist_ok=True)
    with open(DOCS, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"), indent=0)
    print("wrote", os.path.normpath(DOCS), doc["stats"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
