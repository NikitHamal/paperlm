"""Concept-anchor retrieval over data/concept_bank.json (keyword overlap + unit match). Used to build the `<|concept=...|>` prefix
for PaperLM conditional generation and by eval/concept_eval.py.  Anchors are verified text; nothing is generated here."""
import json, re, os
_P = os.path.join(os.path.dirname(__file__), "..", "data", "concept_bank.json")
_W = re.compile(r"[a-z]{4,}")


class ConceptBank:
    def __init__(self, path=_P):
        d = json.load(open(path)); self.c = d["concepts"]; self.by_unit = {}
        for x in self.c: self.by_unit.setdefault(x["u"].lower(), []).append(x)

    def retrieve(self, board, level, subject, unit, k=3, kinds=("law", "fact", "exam")):
        ul = unit.lower(); pool = self.by_unit.get(ul, []) or [x for u, v in self.by_unit.items() if ul in u or u in ul for x in v]
        sk = f"{board}|{level}|{subject}"; q = set(_W.findall(ul + " " + subject.lower()))
        def score(x):
            s = len(q & set(x["kw"])) + (3 if x["b"] == sk else 0) + (1 if subject.lower() in x["b"].lower() else 0)
            return s + (0.5 if x["k"] == "law" else 0)
        return sorted([x for x in pool if x["k"] in kinds], key=score, reverse=True)[:k]

    def prefix(self, board, level, subject, unit, marks, typ):
        a = self.retrieve(board, level, subject, unit, 1)
        t = re.sub(r"\s+", " ", a[0]["t"])[:240] if a else ""
        return f"<|board={board}|><|level={level}|><|subject={subject}|><|unit={unit}|><|marks={marks}|><|type={typ}|><|concept={t}|>"
