"""Stage A2: broad-domain pretraining corpus = textbook prose DECONTAMINATED against validation (any chunk containing a validation stem is dropped)
+ concept lines + verified gold.  v1 leaked: 46% of val stems occurred verbatim in the book corpus, so its val loss (2.02) was optimistic."""
import json, random, re, sys
g = "/tmp/paperlm/gold"; g2 = "/tmp/paperlm/gold2"; norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
keys = set()
for f in (f"{g}/val.txt", f"{g2}/val_clean.txt"):
    for l in open(f, encoding="utf-8"):
        m = re.search(r"<\|q\|>(.*?)(?:<\|oa\||<\|part\||<\|end\|)", l)
        if m and len(norm(m.group(1))) >= 30: keys.add(norm(m.group(1))[:60])
        for m in re.finditer(r"<\|(?:oa|part)\|>(.{40,}?)(?:<\||$)", l): keys.add(norm(m.group(1))[:60]) if len(norm(m.group(1))) >= 40 else None
book = [l.rstrip("\n") for l in open(f"{g}/book.txt", encoding="utf-8") if l.strip()]; keep = []; dropped = 0
for l in book:
    n = norm(l)
    if any(k in n for k in keys): dropped += 1; continue
    keep.append(l)
A = [l.rstrip("\n") for l in open(f"{g2}/stageA.txt", encoding="utf-8") if l.strip()]
out = keep + A; random.Random(3).shuffle(out); open(f"{g2}/stageA2.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
st = dict(val_keys=len(keys), book_chunks=len(book), dropped_contaminated=dropped, kept=len(keep), stageA_lines=len(A), stageA2_lines=len(out)); json.dump(st, open(f"{g2}/stageA2_stats.json", "w")); print(st)
