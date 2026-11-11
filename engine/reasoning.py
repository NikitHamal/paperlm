"""PaperLM Reasoning Engine (Python twin of docs/reasoning.js): mental-agility number/letter series.

Like the parametric engine, nothing here is written by the language model: the series is generated from a rule, the
answer is the rule's next term, and the three distractors are the terms produced by the *typical wrong rules*
(one step extra, one step fewer, off-by-one), so every option is computed and provably distinct from the answer.
"""
import re


def _shuffle(a, rand):
    for i in range(len(a) - 1, 0, -1):
        j = int(rand() * (i + 1))
        a[i], a[j] = a[j], a[i]


def _mcq(stem, answer, distractors, law, rand):
    opts = [str(x) for x in distractors][:3]
    if len(set(opts)) < 3 or str(answer) in opts:
        return None
    options = opts + [str(answer)]
    _shuffle(options, rand)
    return dict(source="reasoning", verified=True, kind="mcq", question=stem, options=options,
                key="abcd"[options.index(str(answer))], explanation=law + " So the answer is " + str(answer) + ".",
                topic="Reasoning series", unit_matched=True, unit_label=None)


def make_item(subject, unit, marks, typ, rand):
    if not (typ == "MCQ" or marks <= 1):
        return _written(marks, rand)
    r = rand()
    if r < 0.30:  # arithmetic progression
        a = int(1 + rand() * 12); d = int(1 + rand() * 9)
        t = [a + i * d for i in range(5)]
        ans = a + 5 * d
        stem = "Find the next term of the series: " + ", ".join(map(str, t)) + ", ?"
        law = "Each term increases by " + str(d) + ", so the next term is " + str(t[-1]) + "+" + str(d) + "=" + str(ans) + "."
        return _mcq(stem, ans, [ans + d, ans - d, ans + 2 * d], law, rand)
    if r < 0.50:  # geometric progression
        a = int(1 + rand() * 4); g = int(2 + rand() * 2)
        t = [a * g ** i for i in range(4)]
        ans = a * g ** 4
        stem = "Find the next term of the series: " + ", ".join(map(str, t)) + ", ?"
        law = "Each term is multiplied by " + str(g) + ", so the next term is " + str(t[-1]) + "x" + str(g) + "=" + str(ans) + "."
        return _mcq(stem, ans, [a * g ** 3, a * g ** 5, ans + g], law, rand)
    if r < 0.70:  # squares
        n = int(3 + rand() * 6)
        t = [i * i for i in range(n, n + 4)]
        ans = (n + 4) ** 2
        stem = "Find the next term of the series: " + ", ".join(map(str, t)) + ", ?"
        law = "The terms are consecutive squares " + str(n) + "^2 to " + str(n + 3) + "^2, so the next term is " + str(n + 4) + "^2=" + str(ans) + "."
        return _mcq(stem, ans, [(n + 5) ** 2, ans + 1, ans - 1], law, rand)
    if r < 0.85:  # difference grows by a constant second difference
        a = int(1 + rand() * 6); d = int(1 + rand() * 4); k = int(1 + rand() * 2)
        t = [a]
        step = d
        for _ in range(4):
            t.append(t[-1] + step); step += k
        ans = t[-1] + step
        stem = "Find the next term of the series: " + ", ".join(map(str, t)) + ", ?"
        law = "The difference between consecutive terms increases by " + str(k) + " each time, so the next term is " + str(t[-1]) + "+" + str(step) + "=" + str(ans) + "."
        return _mcq(stem, ans, [ans - k, ans + k, t[-1]], law, rand)
    # letter series with a constant step
    start = int(65 + rand() * 8); step = int(2 + rand() * 3)
    letters = [chr(start + i * step) for i in range(4)]
    ans = chr(start + 4 * step)
    stem = "Find the next letter of the series: " + ", ".join(letters) + ", ?"
    law = "The letters advance by " + str(step) + " places in the alphabet, so the next letter is " + ans + "."
    return _mcq(stem, ans, [chr(start + 3 * step), chr(start + 5 * step), chr(start + 4 * step + 1)], law, rand)


def _series_mcq(rand):
    """One verified series question as (stem, answer, [distractors], law)."""
    it = make_item("", "", 1, "MCQ", rand)
    return it


def _written(marks, rand):
    need = 1 if marks <= 3 else 2 if marks < 6 else 3
    qs, laws = [], []
    for _ in range(need):
        for _try in range(40):
            it = make_item("", "", 1, "MCQ", rand)
            if it and it["question"] not in qs:
                break
        qs.append(it["question"])
        laws.append(it["explanation"])
    base, extra = divmod(marks, need)
    parts = [dict(label="abc"[x], text=t, marks=base + (1 if x < extra else 0)) for x, t in enumerate(qs)]
    rubric = " ".join(f"({p['label']}) {l} [{p['marks']}]" for p, l in zip(parts, laws))
    return dict(source="reasoning", verified=True, kind="written", question="Answer the following." if need == 1 else "Answer the following:", parts=parts if need > 1 else [], or_parts=[],
                rubric=rubric, topic="Reasoning series", unit_matched=True, unit_label=None)


def can_make(subject):
    toks = set(re.split(r"[^a-z]+", (subject or "").lower()))
    return bool(toks & {"mental", "reasoning", "aptitude"})
