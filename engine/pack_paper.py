#!/usr/bin/env python3
"""Paper-level blueprint planner for a subject pack (Python twin of planPaper in docs/packlm.js, bank tier only).
 * unit quotas proportional to the syllabus share (largest remainder), shuffled over slots
 * anti-duplication coverage tracker: no repeated question, no near-duplicate (token Jaccard >= 0.6), no repeated anchor
 * written answers get a marking scheme: the model answer is split into steps and the marks are spread over them
usage: pack_paper.py <pack_id> [n_mcq=10] [n_short=4] [seed=7] > paper.md"""
import json, os, random, re, sys
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
W = lambda s: set(re.findall(r"[a-z0-9]{3,}", s.lower()))
jac = lambda a, b: len(a & b) / max(1, len(a | b))


def quotas(units, total):
    q = [u["share"] * total for u in units]; base = [int(x) for x in q]
    for i in sorted(range(len(q)), key=lambda i: q[i] - base[i], reverse=True)[: total - sum(base)]: base[i] += 1
    return base


def scheme(ans, marks):
    tg = re.split(r"\s*\[(\d+)\]\s*\|?\s*", ans.strip())  # answers that already carry step marks "... [2] ... [1]" keep them
    if len(tg) >= 3:
        st = [(tg[i].strip(), int(tg[i + 1])) for i in range(0, len(tg) - 1, 2) if tg[i].strip()]
        if st and sum(m for _, m in st) == marks: return st
    steps = [s.strip() for s in re.split(r"(?<=[.;])\s+(?=[A-Z(\\$])", ans) if len(s.strip()) > 8] or [ans]
    k = max(1, min(len(steps), marks * 2)); steps = steps[:k]; mk = [marks // k] * k
    for i in range(marks - sum(mk)): mk[i % k] += 1
    return [(s, m) for s, m in zip(steps, mk) if m]


def plan(pid, n_mcq=10, n_short=4, seed=7):
    d = f"{R}/docs/packs/{pid}"; g = json.load(open(f"{d}/syllabus_graph.json")); bank = json.load(open(f"{d}/bank.json")); rnd = random.Random(seed)
    spec = [("mcq", 1)] * n_mcq + [("short", 3)] * (n_short // 2) + [("short", 5)] * (n_short - n_short // 2)
    us = g["units"]; slots = [u for u, c in zip(us, quotas(us, len(spec))) for _ in range(c)]; rnd.shuffle(slots)
    used, seen_w, anchors, out, miss = set(), [], set(), [], 0
    for (kind, marks), u in zip(spec, slots):
        order = [u] + sorted((x for x in us if x is not u), key=lambda x: -x["share"])
        for uu in order:  # fall back to the next-heaviest unit if this one has no unused item of that kind
            pool = [b for b in bank if b["unit"] == uu["name"] and b["type"] == kind and b["question"] not in used and b["anchor"] not in anchors
                    and (kind == "mcq" or abs(b["marks"] - marks) <= 1) and all(jac(W(b["question"]), w) < 0.6 for w in seen_w)]
            if pool: break
        else: miss += 1; continue
        b = rnd.choice(pool); used.add(b["question"]); anchors.add(b["anchor"]); seen_w.append(W(b["question"])); out.append((kind, marks, b))
    return g, out, miss


def render(pid, n_mcq, n_short, seed):
    g, items, miss = plan(pid, n_mcq, n_short, seed); rnd = random.Random(seed + 1); L = [f"# {g['title']} - mock paper (seed {seed})", ""]
    key = []; n = 0
    for sec, kind in (("Group A: objective, 1 mark each", "mcq"), ("Group B: written", "short")):
        L += [f"## {sec}", ""]
        for k, marks, b in items:
            if k != kind: continue
            n += 1
            if k == "mcq":
                o = [b["answer"]] + b["distractors"]; rnd.shuffle(o); L += [f"{n}. {b['question']}"] + [f"   {'abcd'[i]}) {t}" for i, t in enumerate(o)] + [""]
                key.append(f"{n}. ({'abcd'[o.index(b['answer'])]}) {b['answer']} - {b.get('why', '')}")
            else:
                key.append(f"{n}. [{b['marks']} marks] " + " | ".join(f"{s} [{m}]" for s, m in scheme(b["answer"], b["marks"])))
                L += [f"{n}. {b['question']} [{b['marks']}]", ""]
    L += ["## Answer key and marking scheme", ""] + key + ["", f"Units covered: {len({b['unit'] for _, _, b in items})} of {len(g['units'])}; slots without a unique verified item: {miss}; every item comes from the verified bank (provenance: gold NEB or teacher+verifier)."]
    return "\n".join(L)


if __name__ == "__main__":
    a = sys.argv[1:]; print(render(a[0], int(a[1]) if len(a) > 1 else 10, int(a[2]) if len(a) > 2 else 4, int(a[3]) if len(a) > 3 else 7))
