#!/usr/bin/env python3
"""Build one subject pack's syllabus-pure corpus: syllabus_graph.json, anchors.jsonl (teacher prompts), gold_items.jsonl, book_lm.txt.
Strict boundary: only items/chunks with level == pack.level AND subject == pack.subject are read (no cross-grade/subject leakage).
usage: build_pack.py <pack_id> <out_dir> [gold.jsonl] [book.txt]"""
import collections, hashlib, json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, "..", "..", "data"), "/work/paperlm/data"]
import validator as V
SPECS = json.load(open(os.path.join(HERE, "..", "pack_specs.json")))
pid, out = sys.argv[1], sys.argv[2]; gold = sys.argv[3] if len(sys.argv) > 3 else "/tmp/gold/gold.jsonl"; book = sys.argv[4] if len(sys.argv) > 4 else "/tmp/gold/book.txt"
S = SPECS[pid]; LV, SUBJ = S["level"], S["subject"]; os.makedirs(out, exist_ok=True)
META = re.compile(r"\b(this chapter|this book|practice question|question bank|mark every|you should|read the|answer the ten|group [abc]\b|in the last week|original practice|key below|the key\b|paper \d{4})", re.I)
STOP = set("the of and a an to in is are was were be by for with on as at from that this which it its or their these those can has have into than then also not one two more most each other such when where what who how why".split())
toks = lambda s: [w for w in re.findall(r"[a-z][a-z0-9]{2,}", s.lower()) if w not in STOP]
sents = lambda s: [x.strip() for x in re.split(r"(?<=[.?!])\s+(?=[A-Z$\\(])", s or "") if x.strip()]
kind = lambda t: "formula" if re.search(r"\$|=", t) else "law" if re.search(r"\b(law|principle|theorem|states that|rule)\b", t, re.I) else "def" if re.search(r"\b(is defined as|is called|are called|is known as|refers to|is the)\b", t, re.I) else "fact"
def clean_title(t):
    t = re.sub(r"^[A-Za-z &/-]+:\s*", "", t.strip()); t = re.sub(r"\s*\(.*?\)\s*$", "", t); return t[:70].strip()
# ---- 1. textbook chunks of THIS pack only
chunks = []
for l in open(book, encoding="utf-8"):
    if f"<|level={LV}|>" in l and f"<|subj={SUBJ}|>" in l and "<|board=NEB|>" in l:
        m = re.search(r"<\|unit\|>(.*?)<\|book\|>(.*?)<\|end\|>", l, re.S)
        if m: chunks.append((clean_title(m.group(1)), m.group(2)))
METAU = re.compile(r"question bank|model question|pattern|strategy|predicted|practice|question sets|question set|grid", re.I)
units = collections.OrderedDict(); anchors = []; seen = set()
for title, text in sorted(chunks, key=lambda c: bool(METAU.search(c[0]))):
    meta = bool(METAU.search(title)); title = "?" if meta else title
    u = units.setdefault(title, dict(name=title, facts=[], n_items=collections.Counter()))
    ss = [s for s in sents(text) if 50 <= len(s) <= 300 and not META.search(s) and V.check_text(s) is None]
    for i, s in enumerate(ss):
        a = s if len(s) > 150 or i + 1 >= len(ss) or len(s + ss[i + 1]) > 330 or kind(s) != "fact" else s + " " + ss[i + 1]
        h = hashlib.md5(a.lower().encode()).hexdigest()[:10]
        if h in seen or len(toks(a)) < 6: continue
        seen.add(h); anchors.append(dict(aid=h, unit=title, anchor=a, kind=kind(a)))
# meta chapters (question banks / model sets): re-home each fact to the real unit with the best vocabulary overlap
real = {n: collections.Counter(w for a in anchors if a["unit"] == n for w in set(toks(a["anchor"]))) for n in units if n != "?"}
tot_df = collections.Counter(w for c in real.values() for w in c)
for a in anchors:
    if a["unit"] != "?": continue
    ws = set(toks(a["anchor"])); a["unit"] = max(real, key=lambda n: sum(real[n][w] / (1 + tot_df[w]) for w in ws) / (1 + sum(real[n].values()) ** 0.5))
units.pop("?", None)
for a in anchors: units[a["unit"]]["facts"].append(dict(id=a["aid"], text=a["anchor"], kind=a["kind"]))
# ---- 2. gold items -> normalized schema, unit-mapped by term overlap
df = collections.Counter(w for a in anchors for w in set(toks(a["anchor"])))
N = max(1, len(anchors)); idf = lambda w: math.log(1 + N / (1 + df.get(w, 0)))
ATS = [set(toks(a["anchor"])) for a in anchors]
def best_fact(text):
    q = set(toks(text)); b, bs = None, 0
    for a, ts in zip(anchors, ATS):
        sc = sum(idf(w) for w in q & ts) / (1 + 0.02 * len(a["anchor"]))
        if sc > bs: b, bs = a, sc
    return b, bs
gold_items = []
for l in open(gold, encoding="utf-8"):
    g = json.loads(l)
    if g["board"] != "NEB" or g["level"] != LV or g["subject"] != SUBJ: continue
    if g["qtype"] == "MCQ":
        if not (g.get("key") and g.get("why")) or len(g["opts"]) != 4 or g["key"] not in "abcd": continue
        ans = g["opts"]["abcd".index(g["key"])]; ds = [o for o in g["opts"] if o != ans]
        txt = g["q"] + " " + g["why"]; it = dict(type="mcq", marks=1, question=g["q"], answer=ans, distractors=ds, why=g["why"])
    else:
        if not g.get("sol") or g.get("marks", 0) not in (2, 3, 4, 5): continue
        q = " ".join((p["label"] + ") " if p["label"] else "") + p["text"] for p in g["parts"]); sol = g["sol"]
        if len(sol) > 650 or len(q) > 480 or V.check_text(sol) is not None: continue
        txt = q + " " + sol; it = dict(type="short", marks=min(g["marks"], 5), question=q, answer=sol)
    b, sc = best_fact(txt)
    if not b or sc < 3.0: continue
    it.update(unit=b["unit"], anchor=g["why"] if it["type"] == "mcq" and 50 < len(g["why"]) < 300 else b["anchor"], src=g["src"], year=g.get("year_bs", "")); gold_items.append(it)
    units[b["unit"]]["n_items"][it["type"]] += 1
# ---- 3. syllabus graph (canonical facts, laws/formulas, key terms, mark weighting, sibling terms for distractor audit)
graph = dict(pack=pid, level=LV, subject=SUBJ, title=S["title"], units=[])
for u in units.values():
    if len(u["facts"]) < 3: continue
    tf = collections.Counter(w for f in u["facts"] for w in set(toks(f["text"])))
    terms = [w for w, c in sorted(tf.items(), key=lambda x: -x[1] * idf(x[0])) if c >= 2][:40]
    rank = {"law": 0, "formula": 0, "def": 1, "fact": 2}
    fs = sorted(u["facts"], key=lambda f: (rank[f["kind"]], -len(f["text"])))[:140]
    graph["units"].append(dict(id=hashlib.md5(u["name"].encode()).hexdigest()[:6], name=u["name"], terms=terms, facts=fs,
                               weight=sum(u["n_items"].values()) + 1, items=dict(u["n_items"])))
tot = sum(u["weight"] for u in graph["units"]); [u.update(share=round(u["weight"] / tot, 4)) for u in graph["units"]]
json.dump(graph, open(f"{out}/syllabus_graph.json", "w"), ensure_ascii=False, separators=(",", ":"))
with open(f"{out}/anchors.jsonl", "w") as f: [f.write(json.dumps(a, ensure_ascii=False) + "\n") for a in anchors]
with open(f"{out}/gold_items.jsonl", "w") as f: [f.write(json.dumps(a, ensure_ascii=False) + "\n") for a in gold_items]
with open(f"{out}/book_lm.txt", "w") as f: [f.write(f"<|bos|><|pack={pid}|><|unit|>{t}<|book|>{x}<|end|>\n") for t, x in chunks]
print(pid, dict(chunks=len(chunks), units=len(graph["units"]), anchors=len(anchors), gold=len(gold_items), mcq=sum(i["type"] == "mcq" for i in gold_items)))
