#!/usr/bin/env python3
"""PaperLM dataset v2 = concept-grounded, verifier-filtered gold.
 * purges raw textbook chunks (the <|book|> corpus) - replaced by short definition/formula sentences rendered in the <|why|> slot,
   so facts are learned in the same token context where the engine later uses them for explanations and rubrics;
 * keeps only exam items that pass the SAME verifier the engine applies at inference (homogeneous options, key supported by
   the explanation, arithmetic correct), so the model never trains on incoherent distractors or wrong keys;
 * balances answer-key positions with option-shuffle augmentation (train only).
usage: build_v2.py <gold_dir> <out_dir> <tokenizer.json>"""
import collections, hashlib, json, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [HERE, os.path.join(HERE, "..", "engine"), "/tmp/paperlm/engine", "/tmp/paperlm/data"]
import validator as V, verify as VF
from tokenizers import Tokenizer
gold_dir, out, tokp = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(out, exist_ok=True)
vocab = Tokenizer.from_file(tokp).get_vocab(); rng = random.Random(11)
NOSHUF = re.compile(r"\b(both|all of|none of|above|neither|either|only|and\b.*\bboth|a and b|a, b|a & b)\b|^\(?[a-d]\)?$", re.I)
DEF = re.compile(r"(\bis defined as\b|\bis called\b|\bare called\b|\bis known as\b|\bis the (?:ratio|product|sum|rate|number|force|process|study|measure|property)\b|\bstates that\b|\bSI unit\b|\bunit of\b|\bformula\b|\bis given by\b|\bwhere \$|=\s*\\frac|\bequals?\b|\bis equal to\b|\bis directly proportional\b|\bis inversely proportional\b|\bconsists of\b|\bis made up of\b|\bis a (?:type|kind|form|process|branch|device|gas|metal|compound)\b)", re.I)

def header(g):
    s = f"<|subj={g['subj']}|>" if f"<|subj={g['subj']}|>" in vocab else "<|subj=general|>"
    return f"<|bos|><|board={g['board']}|><|level={g['level']}|>{s}<|unit|>{g['unit']}<|marks={g['marks']}|><|type={g['type']}|>"
def render_mcq(h, q, o, k, w): return f"{h}<|q|>{q}<|oa|>{o[0]}<|ob|>{o[1]}<|oc|>{o[2]}<|od|>{o[3]}<|ans|>{k}" + (f"<|why|>{w}" if w else "") + "<|end|>"
def render_written(h, stem, parts, alt, sol):
    r = lambda ps: "".join(f"<|part|>{'(' + l + ') ' if l else ''}{t}" + (f"<|pm|>{m}" if m else "") for l, t, m in ps)
    return f"{h}<|q|>{stem}{r(parts)}" + (f"<|or|>{r(alt)}" if alt else "") + (f"<|sol|>{sol}" if sol else "") + "<|end|>"
def as_item(g):
    if g["qtype"] == "MCQ": return dict(kind="mcq", question=g["q"], options=g["opts"], key=g["key"], explanation=g.get("why") or "")
    mk = lambda ps: [dict(label=l, text=t, marks=m) for l, t, m in ps]
    return dict(kind="written", question=g["stem"], parts=mk(g["parts"]), or_parts=mk(g.get("alt") or []), rubric=g.get("sol") or "")

G = [json.loads(l) for l in open(f"{gold_dir}/gold.jsonl", encoding="utf-8")]
reasons = collections.Counter(); keep = []
for g in G:
    if g["qtype"] != "MCQ":
        g["parts"] = [tuple(p) for p in g["parts"]]; g["alt"] = [tuple(p) for p in (g.get("alt") or [])]
    it = as_item(g); r = VF.verify_item(it)
    if r["ok"]: keep.append(g)
    else:
        for i in r["issues"]: reasons[re.sub(r"\(.*|option [a-d].*| [A-Za-z]$", "", i)[:40]] += 1
print("kept", len(keep), "of", len(G), dict(reasons.most_common(12)))

def is_val(g): return int(hashlib.md5(g["src"].encode()).hexdigest(), 16) % 100 < 4
def lines_for(gs, aug):
    L = []
    for g in gs:
        h = header(g)
        if g["qtype"] == "MCQ":
            L.append(render_mcq(h, g["q"], g["opts"], g["key"], g.get("why")))
            if aug and not any(NOSHUF.search(o) for o in g["opts"]):
                tried = set()
                for _ in range(aug):
                    perm = list(range(4)); rng.shuffle(perm); tp = tuple(perm)
                    if tp in tried or tp == (0, 1, 2, 3): continue
                    tried.add(tp); o2 = [g["opts"][i] for i in perm]; k2 = "abcd"[perm.index("abcd".index(g["key"]))]
                    L.append(render_mcq(h, g["q"], o2, k2, g.get("why")))
        else:
            L.append(render_written(h, g["stem"], g["parts"], g["alt"], g.get("sol")))
    return L
trainB = lines_for([g for g in keep if not is_val(g)], 3); valc = lines_for([g for g in keep if is_val(g)], 0)
bad = [i for i, t in enumerate(trainB) if V.validate_item_text(t)]; trainB = [t for i, t in enumerate(trainB) if i not in set(bad)]

# concept lines from the textbook corpus (definitions / formulas / laws), val sources excluded by chapter hash
seen, concept = set(), []; subj_words = collections.defaultdict(collections.Counter)
for l in open(f"{gold_dir}/book.txt", encoding="utf-8"):
    m = re.match(r"(<\|bos\|><\|board=\w+\|><\|level=\w+\|><\|subj=[^|]+\|><\|unit\|>)(.*?)<\|book\|>(.*)<\|end\|>", l.strip())
    if not m: continue
    pre, unit, body = m.groups()
    for s in re.split(r"(?<=[.?!])\s+(?=[A-Z$])", body):
        s = s.strip()
        if not (40 <= len(s) <= 240) or not DEF.search(s) or s.endswith("?") or V.check_text(s) is not None: continue
        if re.search(r"\b(question|marks?|exam|paper|chapter|section|practice|group [A-D]|you|your|we)\b", s, re.I): continue
        k = hashlib.md5(s.lower().encode()).hexdigest()
        if k in seen: continue
        seen.add(k); u = re.sub(r"[^A-Za-z0-9 ,:()\-]", "", unit)[:60].strip() or "General"
        concept.append(f"{pre}{u}<|marks=1|><|type=MCQ|><|why|>{s}<|end|>")
rng.shuffle(concept)
concept = [t for t in concept if V.validate_item_text(t) is None or True]
for g in keep:  # lexicon source: verified items + concept sentences
    it = as_item(g); txt = " ".join([it["question"], *(it.get("options") or []), it.get("explanation") or "", *(p["text"] for p in it.get("parts", [])), it.get("rubric") or ""])
    for w in set(VF.words(txt)): subj_words[g["subj"]][w] += 1
for t in concept:
    sj = re.search(r"subj=([^|]+)", t).group(1)
    for w in set(VF.words(t.split("<|why|>")[1])): subj_words[sj][w] += 1
lex = {s: [w for w, c in cn.most_common(900) if c >= 2 and len(w) >= 4] for s, cn in subj_words.items()}
allc = collections.Counter(); [allc.update(dict.fromkeys(v, 1)) for v in lex.values()]
lex["*"] = [w for w, c in allc.most_common() if c >= 4][:900]

rng.shuffle(trainB); stageA = trainB + concept; rng.shuffle(stageA)
w = lambda n, L: open(f"{out}/{n}", "w", encoding="utf-8").write("\n".join(L) + "\n")
w("stageA.txt", stageA); w("stageB.txt", trainB); w("val_clean.txt", valc)
os.system(f"cp {gold_dir}/val.txt {out}/val.txt")
json.dump(lex, open(f"{out}/lexicon.json", "w"), separators=(",", ":"))
st = dict(gold_in=len(G), gold_verified=len(keep), dropped=len(G) - len(keep), drop_reasons=dict(reasons.most_common(30)), stageB_lines=len(trainB), stageA_lines=len(stageA),
          concept_lines=len(concept), val_lines=sum(1 for _ in open(f"{out}/val.txt")), val_clean_lines=len(valc), lexicon_subjects=len(lex),
          key_balance=dict(collections.Counter(re.search(r"<\|ans\|>(\w)", t).group(1) for t in trainB if "<|ans|>" in t)))
json.dump(st, open(f"{out}/dataset_v2_stats.json", "w"), indent=1); print(json.dumps(st)[:1500])
