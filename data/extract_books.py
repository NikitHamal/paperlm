#!/usr/bin/env python3
"""Textbook prose corpus (lesson chapters of the NEBians study books) -> gold/book.txt, used to teach PaperLM fluent,
correct subject language before/alongside exam items.  Every paragraph must pass the same validator (LaTeX, charset, no residue)."""
import glob, hashlib, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_neb as E, validator as V

def main():
    root, out = sys.argv[1], sys.argv[2]
    seen, nchunk, nchar, rej = set(), 0, 0, 0
    with open(out, "w", encoding="utf-8") as fo:
        for cl in sorted(glob.glob(root + "/*")):
            for p in sorted(glob.glob(cl + "/backend_python/web/data/study/*/*.json")):
                try: d = json.load(open(p, encoding="utf-8"))
                except Exception: continue
                if not isinstance(d, dict) or not d.get("html"): continue
                parent = os.path.basename(os.path.dirname(p)); board, level, subj = E.classify_dir(parent)
                subj = re.sub(r"^(course-|bca-)", "", subj)
                title = V.normalize(str(d.get("title", ""))); title = re.sub(r"^\d+(\.\d+)*\s*", "", title)[:60]
                root_n = E.parse_html(d["html"]); paras = []
                def walk(n, skip):
                    for k in n.kids:
                        if isinstance(k, str): continue
                        if k.tag in ("table", "figure", "svg", "pre", "code", "script", "style", "details", "summary") or k.has("mcq") or k.has("box") and False: continue
                        if k.has("ans") or k.has("opts") or k.has("photokey"): continue
                        if k.tag == "ol" and k.has("mcq"): continue
                        if k.tag in ("p", "li", "h2", "h3"):
                            t = E.to_text(k, skip=("marks",))
                            t = V.normalize(t)
                            if k.tag in ("h2", "h3"): t = t + "."
                            paras.append(t); continue
                        walk(k, skip)
                walk(root_n, False)
                good = []
                for t in paras:
                    if len(t) < 40 or V.check_text(t) is not None or V.needs_visual(t) and False: rej += 1; continue
                    h = hashlib.md5(t.lower().encode()).hexdigest()
                    if h in seen: continue
                    seen.add(h); good.append(t)
                chunk = ""
                def emit(c):
                    nonlocal nchunk, nchar
                    if len(c) < 200: return
                    line = f"<|bos|><|board={board}|><|level={level}|><|subj={subj}|><|unit|>{title}<|book|>{c.strip()}<|end|>"
                    fo.write(line + "\n"); nchunk += 1; nchar += len(line)
                for t in good:
                    if len(chunk) + len(t) > 1400: emit(chunk); chunk = ""
                    chunk += t + " "
                emit(chunk)
    print("book chunks", nchunk, "chars", nchar, "rejected paragraphs", rej)
    try:
        sys.path.insert(0, "/tmp/paperlm"); import live_status as LS; LS.update("dataset", book_chunks=nchunk, book_chars=nchar)
    except Exception: pass
main()
