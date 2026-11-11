"""PaperLM Fact Bank (Python twin of docs/factbank.js).

The verified "fact" tier: closed-world tables of (key, value, definition) rows.  A question is a projection of one
row; its three distractors are the values (or keys) of other rows of the same class, chosen so that no two options
share a value.  Consequences, by construction and not by hope:

  * the key is the stored value of the row, so it is correct;
  * no distractor can also be correct, because a class is closed world and every option has a different value;
  * nothing is generated freely: the stem is a template with one substitution, the explanation is the row's own
    definition.  The 10M model is not involved at all.

Class selection is unit-aware: a class is matched to the requested unit by its keyword list, then by lexical overlap
with the unit name; when nothing matches, the item is marked `unit_matched = False` so the caller labels it with the
class topic instead of pretending it belongs to that unit.

Written items project two or three rows into labelled parts, taking each part from a *different* class when possible,
so a 6-mark question has three genuinely different verified answers.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, "..", "docs", "model", "facts.json")
STOP = {"the", "of", "and", "for", "with", "from", "that", "this", "which", "their", "there", "into", "than", "then",
        "were", "was", "are", "its", "his", "her", "has", "have", "had", "not", "all", "any", "each", "both", "one",
        "two", "three", "four", "five", "some", "more", "most", "other", "only", "over", "under", "between", "during",
        "using", "used", "use", "called", "known", "given", "state", "write", "find", "name", "explain", "define",
        "when", "where", "while", "whose", "whom", "how", "why", "does", "did", "does", "make", "makes", "made",
        "give", "gives", "must", "but", "because", "therefore", "thus", "hence", "about", "per", "via", "with", "also"}


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())


def words(s):
    return {w for w in re.findall(r"[a-z]{4,}", str(s).lower()) if w not in STOP}


def article(word):
    low = re.sub(r"^[^a-z]+", "", str(word).lower())
    return "an" if low[:1] in "aeiou" and not low.startswith(("uni", "use", "one", "eu")) else "a"


def fill(tpl, k, v):
    """Single-substitution template filling, with the indefinite article corrected for {k}."""
    if " a {k}" in tpl and article(k) == "an":
        tpl = tpl.replace(" a {k}", " an {k}")
    return tpl.replace("{k}", k).replace("{v}", v)


def shuffle(a, rand):
    for i in range(len(a) - 1, 0, -1):
        j = int(rand() * (i + 1))
        a[i], a[j] = a[j], a[i]


def stem6(w):
    return w[:6]


class FactBank:
    def __init__(self, doc=None):
        doc = doc if doc is not None else json.load(open(DOC, encoding="utf-8"))
        self.classes = doc["classes"]
        self.stats = doc.get("stats", {})
        self._rx = [(c, [re.compile(p, re.I) for p in c["subjects"]]) for c in self.classes]
        self._words = {}
        for c in self.classes:
            w = words(c["label"])
            for k, v, d in c["pairs"]:
                w |= words(k) | words(v)
            self._words[c["id"]] = w

    # ------------------------------------------------------------------ selection
    def classes_for(self, subject):
        return [c for c, rxs in self._rx if any(rx.search(subject or "") for rx in rxs)]

    def can_make(self, subject):
        return bool(self.classes_for(subject))

    def _relevance(self, cls, unit):
        u = words(unit)
        if not u:
            return 0
        cw = self._words[cls["id"]]
        return sum(1 for x in u if any(x == y or (len(x) >= 6 and (stem6(x) == stem6(y))) for y in cw))

    def pick_class(self, subject, unit="", rand=None, exclude=()):
        cs = [c for c in self.classes_for(subject) if c["id"] not in exclude]
        if not cs:
            return None, False
        rand = rand or (lambda: 0.5)
        if unit:
            ul = unit.lower()
            kw = [c for c in cs if any(k.lower() in ul for k in c.get("units") or [])]
            if kw:
                return kw[min(len(kw) - 1, int(rand() * len(kw)))], True
            # No lexical guessing: a class is either declared for this unit by its keyword list, or it is offered as a
            # topic-labelled item (unit_matched = False) that the caller may use as a last resort.
        return cs[min(len(cs) - 1, int(rand() * len(cs)))], False

    # ------------------------------------------------------------------ items
    def _mcq(self, cls, rows, i, rand):
        k, v, d = rows[i]
        cat = bool(cls.get("cat"))
        distinct_vals = len({norm(r[1]) for r in rows})
        reverse = bool(cls.get("qb")) and (distinct_vals < 4 or rand() < 0.35)
        if reverse:
            stem, answer, field = fill(cls["qb"], k, v), k, 0
            pool = [r for j, r in enumerate(rows) if j != i and norm(r[1]) != norm(v)]
        else:
            stem, answer, field = fill(cls["qa"], k, v), v, 1
            if cat:  # the key is a category: a distractor must belong to another category
                pool = [r for j, r in enumerate(rows) if j != i and norm(r[0]) != norm(k)]
            else:
                pool = [r for j, r in enumerate(rows) if j != i and norm(r[1]) != norm(v)]
        seen, opts = {norm(answer)}, []
        shuffle(pool, rand)
        for r in pool:
            t = norm(r[field])
            if t in seen:
                continue
            seen.add(t)
            opts.append(r[field])
            if len(opts) == 3:
                break
        if len(opts) < 3:
            return None
        options = opts + [answer]
        shuffle(options, rand)
        key = "abcd"[options.index(answer)]
        expl = d.strip()
        if not expl.endswith("."):
            expl += "."
        expl += " Therefore the correct answer is " + answer + "."
        return dict(source="fact", verified=True, kind="mcq", question=stem, options=options, key=key,
                    explanation=expl, topic=cls["label"], fact_id=cls["id"], fact_src=cls["src"],
                    fact_row=i, fact_dir="reverse" if reverse else "forward",
                    unit_matched=True, unit_label=None)

    def _written(self, cls, rows, marks, rand, subject, unit):
        need = 1 if marks <= 3 else 2 if marks < 6 else 3
        parts_meta, qs, defs = [], [], []
        pool = [cls] + [c for c in self.classes_for(subject) if c is not cls]
        used_ids = set()
        k0 = int(rand() * len(rows))
        parts_meta.append((cls, k0))
        used_ids.add(cls["id"])
        for _n in range(1, need):
            c2, matched = self.pick_class(subject, unit, rand, exclude=tuple(used_ids))
            if not matched:  # keep the written item inside one unit: fall back to the same class
                c2 = cls
            used_ids.add(c2["id"])
            parts_meta.append((c2, int(rand() * len(c2["pairs"]))))
        for c, i in parts_meta:
            k, v, d = c["pairs"][i]
            qs.append(fill(c["qo"], k, v))
            defs.append(d)
        meta = dict(source="fact", verified=True, kind="written", or_parts=[], topic=cls["label"],
                    fact_id=cls["id"], fact_src=cls["src"], fact_row=parts_meta[0][1],
                    fact_parts=[dict(fact_id=c["id"], fact_row=i, src=c["src"], topic=c["label"]) for c, i in parts_meta],
                    unit_matched=True, unit_label=None)
        if need == 1 or len(qs) == 1:
            return dict(meta, question=qs[0], parts=[], rubric=defs[0])
        base, extra = divmod(marks, len(qs))
        parts = [dict(label="abc"[x], text=t, marks=base + (1 if x < extra else 0)) for x, t in enumerate(qs)]
        rubric = " ".join(f"({p['label']}) {d} [{p['marks']}]" for p, d in zip(parts, defs))
        return dict(meta, question="Answer the following:", parts=parts, rubric=rubric)

    def make_item(self, subject, unit, marks, typ, rand):
        cls, matched = self.pick_class(subject, unit, rand)
        if not cls:
            return None
        rows = cls["pairs"]
        i = min(len(rows) - 1, int(rand() * len(rows)))
        if typ == "MCQ" or marks <= 1:
            it = self._mcq(cls, rows, i, rand)
            if it is not None:
                it["unit_matched"] = matched
            return it
        it = self._written(cls, rows, marks, rand, subject, unit)
        if it is not None:
            it["unit_matched"] = matched
        return it

    # ------------------------------------------------------------------ self check
    def audit_item(self, item, subject=""):
        """Independent check: every part's answer is the stored value of the row it claims to project."""
        issues = []
        if item.get("source") != "fact":
            return ["not a fact item"]
        by_id = {c["id"]: c for c in self.classes}
        if item["kind"] == "mcq":
            cls = by_id.get(item.get("fact_id"))
            if cls is None:
                return ["unknown fact class"]
            rows = cls["pairs"]
            i = item.get("fact_row")
            if i is None or not (0 <= i < len(rows)):
                return ["missing fact row"]
            k, v, _d = rows[i]
            want = k if item.get("fact_dir") == "reverse" else v
            if len(item["options"]) != 4:
                issues.append("not 4 options")
            if len({norm(o) for o in item["options"]}) != 4:
                issues.append("duplicate options")
            if item["key"] not in "abcd":
                return issues + ["bad key"]
            got = item["options"]["abcd".index(item["key"])]
            if norm(got) != norm(want):
                issues.append("key is not the stored value of the row")
            if re.search(r"\{[kv]\}", item["question"]):
                issues.append("unresolved template")
            return issues
        parts = item.get("fact_parts") or [dict(fact_id=item.get("fact_id"), fact_row=item.get("fact_row"))]
        for n, p in enumerate(parts):
            cls = by_id.get(p.get("fact_id"))
            if cls is None:
                issues.append(f"part {n}: unknown fact class")
                continue
            i = p.get("fact_row")
            if i is None or not (0 <= i < len(cls["pairs"])):
                issues.append(f"part {n}: missing fact row")
                continue
            if item.get("parts"):
                if n >= len(item["parts"]):
                    issues.append(f"part {n}: missing part text")
                    continue
                txt = item["parts"][n]["text"]
            else:
                txt = item.get("question")
            if not txt:
                issues.append(f"part {n}: empty text")
            elif re.search(r"\{[kv]\}", txt):
                issues.append(f"part {n}: unresolved template")
        if not item.get("rubric"):
            issues.append("no rubric")
        if item.get("parts") and item.get("marks") and sum(p["marks"] for p in item["parts"]) != item["marks"]:
            issues.append("part marks do not sum to the item marks")
        if not item.get("question"):
            issues.append("empty question")
        return issues
