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


def plan(pid, n_mcq=10, n_short=4, seed=7, n_num=2):
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
    nbp = f"{d}/numeric_bank.json"  # v13: computed numericals replace the lowest-priority bank MCQs (key + distractors derived from a formula, exact by construction)
    if n_num and os.path.exists(nbp):
        nb = json.load(open(nbp)); by = {}
        for b in nb: by.setdefault(b["tpl"], []).append(b)
        share = {u["name"]: u["share"] for u in us}; tpls = sorted(by, key=lambda t: (-share.get(by[t][0]["unit"], 0), t)); picks = []; seen_u = set()
        for t in tpls:  # heaviest syllabus unit first, one template per unit before a unit repeats
            if len(picks) >= n_num: break
            if by[t][0]["unit"] in seen_u and len(seen_u) < len({by[x][0]["unit"] for x in tpls}): continue
            picks.append(rnd.choice(by[t])); seen_u.add(by[t][0]["unit"])
        mc = [i for i, (k, m, b) in enumerate(out) if k == "mcq"]
        for pk in picks:
            same = [i for i in mc if out[i][2]["unit"] == pk["unit"] and out[i][2].get("src") != "computed"]
            j = (same or mc[::-1])[0]; mc.remove(j); out[j] = ("mcq", 1, pk)
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
    L += ["## Answer key and marking scheme", ""] + key + ["", f"Units covered: {len({b['unit'] for _, _, b in items})} of {len(g['units'])}; slots without a unique verified item: {miss}; every item comes from the verified bank (provenance: gold NEB, teacher+verifier, or computed by the parametric solver)."]
    return "\n".join(L)


if __name__ == "__main__":
    a = sys.argv[1:]; print(render(a[0], int(a[1]) if len(a) > 1 else 10, int(a[2]) if len(a) > 2 else 4, int(a[3]) if len(a) > 3 else 7))
