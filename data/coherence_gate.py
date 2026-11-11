#!/usr/bin/env python3
"""Coherence gate v2 for bank seeds (deterministic; complements eval/bank_audit.py).
Flags items a student could not answer or that contradict themselves:
  D  dangling deixis: stem points at a figure/table/passage/matrix/"given data" that is not in the stem
  L  explanation names a different option letter than the key ("option (b)", "answer is c")
  K  key option text is contradicted: explanation states 'not <key text>' / 'incorrect'
  O  duplicate / empty / self-referential options
  M  malformed math: unbalanced $, braces or \\left/\\right
  S  stem too short / unfinished (ends with a connector, <4 words, no question content)
usage: coherence_gate.py bank.json [out_bank.json] [report.json]   (out_bank drops flagged seeds; report lists them)"""
import json, re, sys, collections

DEIX = re.compile(r"\b(?:the\s+)?(?:given|following|above|below|shown|accompanying)\s+(?:figure|fig\.?|diagram|graph|table|chart|circuit|picture|image|passage|paragraph|poem|extract|text|data|matrix|map|photograph)\b"
                  r"|\b(?:figure|fig\.)\s*\(?\d|\bin the (?:figure|diagram|graph|table|circuit)\b|\bfrom the (?:graph|table|figure|diagram)\b"
                  r"|\bread the (?:passage|poem|paragraph|text)\b|\bbased on the (?:passage|table|figure|graph|diagram)\b", re.I)
HAS_DATA = re.compile(r"\\begin\{(?:array|matrix|pmatrix|bmatrix|tabular|cases)\}|\|[^|\n]+\|[^|\n]+\||\n\s*[-*] |\bx\s*[:|]\s*\d", re.I)
LETTER = re.compile(r"\b(?:(?:the )?(?:correct )?(?:answer|key)\s+is|correct (?:option|choice) is|hence option|so option|therefore option|thus option)\s*[\(\[]?([a-d])[\)\]]?(?![a-z])", re.I)
TAIL = re.compile(r"(?:\b(?:the|a|an|of|in|on|to|is|are|and|or|with|for|by|that|which|from|if|then)|[,:;\-(])\s*$", re.I)


def bal(s):
    # $ must pair up (ignoring escaped), braces/left-right must balance inside math
    t = s.replace("\\$", "")
    if t.count("$$") * 2 != 0:
        t = t.replace("$$", "")
    if t.count("$") % 2: return False
    for m in re.findall(r"\$([^$]*)\$", s.replace("$$", "$")):
        if m.count("{") != m.count("}") or len(re.findall(r"\\left(?![a-zA-Z])",m)) != len(re.findall(r"\\right(?![a-zA-Z])",m)): return False
    return True


def norm(s): return re.sub(r"[\s.,;:]+", "", s.lower())


def check(it):
    q = it.get("q", "") or ""; o = it.get("o") or []; w = it.get("w", "") or ""; k = it.get("k"); iss = []
    if DEIX.search(q) and not HAS_DATA.search(q): iss.append("D")
    if it.get("c") == "mcq":
        if k in "abcd" and len(o) == 4:
            ks = "abcd".index(k)
            for m in LETTER.finditer(w):
                if m.group(1).lower() != k: iss.append("L"); break
            kt = norm(o[ks])
            if len(kt) >= 4 and not re.search(r"\bnot\b|\bexcept\b|\bfalse\b", q, re.I) and re.search(r"\bnot\s+(?:the\s+)?" + re.escape(o[ks].strip().lower()) + r"\b", w.lower()): iss.append("K")
        ns = [norm(x) for x in o]
        if len(set(ns)) < len(ns) or any(not x for x in ns): iss.append("O")
        qn = norm(q)
        if any(len(x) > 25 and x in qn for x in ns): iss.append("O")
    for f in [q] + list(o) + [w]:
        if not bal(f): iss.append("M"); break
    wc = len(re.findall(r"[A-Za-z]{2,}", re.sub(r"\$[^$]*\$", " X ", q)))
    if not it.get("p") and it.get("c") != "mcq" and ((wc < 3 and "$" not in q) or TAIL.search(q.strip())): iss.append("S")
    if it.get("c") == "mcq" and wc < 2 and "$" not in q: iss.append("S")
    return sorted(set(iss))


def main():
    src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else None; rep = sys.argv[3] if len(sys.argv) > 3 else None
    b = json.load(open(src)); flagged = []; stats = collections.Counter(); tot = 0; keep = 0
    nb = dict(b); nb["seeds"] = {}
    for key, units in b["seeds"].items():
        nb["seeds"][key] = {}
        for u, items in units.items():
            good = []
            for it in items:
                tot += 1; iss = check(it)
                if iss:
                    for i in iss: stats[i] += 1
                    flagged.append(dict(board=key, unit=u, issues=iss, q=it.get("q", "")[:300], o=it.get("o"), k=it.get("k"), w=(it.get("w") or "")[:200]))
                else: good.append(it); keep += 1
            if good: nb["seeds"][key][u] = good
    r = dict(total=tot, kept=keep, flagged=len(flagged), by_rule=dict(stats))
    print(json.dumps(r))
    if rep: json.dump(dict(summary=r, flagged=flagged), open(rep, "w"), ensure_ascii=False, indent=1)
    if out: json.dump(nb, open(out, "w"), ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__": main()
