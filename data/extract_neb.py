#!/usr/bin/env python3
"""PaperLM NEB multi-branch exam corpus extractor.

Walks every cloned branch of NikitHamal/NEB (main, resources/past-papers-class12, claude/engineering,
claude/bsc-nursing, claude/bca-entrance-complete, polish/school-books-claude ... whatever is present) and extracts
raw exam items into JSONL:

  1. Past-paper markdown   notes/papers*/**/content/*.md   (@mcq/@opts/@q/@or/@s DSL, with worked solutions)
  2. Study-book JSON       backend_python/web/data/study/*/*.json (HTML question banks, MCQ w/ keys + reasons,
                           Group B/C written questions w/ model answers)

Usage: extract_neb.py <out.jsonl> <root_dir_containing_clones> [--status]
"""
import glob, hashlib, html as htmllib, json, os, re, sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ----------------------------------------------------------------------------- mini DOM
VOID = {"br", "img", "hr", "input", "meta", "link", "col"}

class Node:
    __slots__ = ("tag", "attrs", "kids", "parent")
    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.kids, self.parent = tag, dict(attrs or []), [], parent
    def cls(self):
        return (self.attrs.get("class") or "").split()
    def has(self, c):
        return c in self.cls()

class DOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root"); self.cur = self.root
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur); self.cur.kids.append(n)
        if tag not in VOID: self.cur = n
    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(Node(tag, attrs, self.cur))
    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag: n = n.parent
        if n is not None and n.parent is not None: self.cur = n.parent
    def handle_data(self, data):
        self.cur.kids.append(data)

def parse_html(s):
    d = DOM(); d.feed(s); return d.root

def iter_nodes(n):
    for k in n.kids:
        if isinstance(k, Node):
            yield k
            yield from iter_nodes(k)

def has_figure(n):
    return any(x.tag in ("img", "figure", "svg", "table") for x in iter_nodes(n))

SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")

def to_text(n, skip=()):
    """HTML node -> plain text with $...$ LaTeX preserved."""
    out = []
    def rec(x):
        if isinstance(x, str):
            out.append(x); return
        if x.tag in skip or any(c in skip for c in x.cls()): return
        if x.tag == "span" and x.has("m"):
            out.append("$" + "".join(flat(x)).strip() + "$"); return
        if x.tag == "div" and x.has("dm"):
            out.append(" $$" + "".join(flat(x)).strip() + "$$ "); return
        if x.tag == "sub": out.append("_{" + "".join(flat(x)) + "}"); return
        if x.tag == "sup": out.append("^{" + "".join(flat(x)) + "}"); return
        if x.tag == "br": out.append(" "); return
        if x.tag in ("li", "p", "div") and out and not out[-1].endswith((" ", "\n")): out.append(" ")
        for k in x.kids: rec(k)
    def flat(x):
        for k in x.kids:
            if isinstance(k, str): yield k
            else: yield from flat(k)
    rec(n)
    t = "".join(out)
    return re.sub(r"[ \t\r\n\u00a0]+", " ", t).strip()

# ----------------------------------------------------------------------------- level / board mapping
def classify_dir(dirname, branch=""):
    """study dir name (e.g. 12-physics / ioe-mathematics) -> (board, level, subject)."""
    d = dirname.lower()
    m = re.match(r"(\d+)-(.+)", d)
    if m:
        g = int(m.group(1)); subj = m.group(2)
        board = {8: "BLE", 10: "SEE"}.get(g, "NEB")
        return board, f"C{g}", subj
    for pre, board, lvl in (("ioe", "IOE", "IOE"), ("cee", "CEE", "CEE"), ("bca", "TU", "BCA"),
                            ("nurs", "CTEVT", "BSN"), ("bsn", "CTEVT", "BSN"), ("be-", "IOE", "BE"), ("eng", "IOE", "BE")):
        if d.startswith(pre):
            return board, lvl, re.sub(r"^[a-z]+-", "", d)
    return "NEB", "C12", d

# ----------------------------------------------------------------------------- past-paper markdown parser
FM = re.compile(r"^---\n(.*?)\n---\n", re.S)

def clean_md(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"(?<![\*$\\])\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"\1", t)
    t = re.sub(r"<small>.*?</small>", "", t)
    return re.sub(r"[ \t]+", " ", t).strip()

def parse_paper_md(path, branch):
    s = open(path, encoding="utf-8", errors="ignore").read()
    m = FM.match(s)
    meta = {}
    if m:
        for ln in m.group(1).splitlines():
            if ":" in ln:
                k, v = ln.split(":", 1); meta[k.strip()] = v.strip()
        s = s[m.end():]
    base = os.path.basename(path)
    grade = meta.get("grade", "")
    subj = re.sub(r"[^a-z0-9]+", "-", (meta.get("subject") or base.split("-")[1]).lower()).strip("-")
    prog = meta.get("program") or meta.get("level") or ""
    stem = base.split("-")[0]
    is_be = meta.get("level", "").upper().startswith("BE") or base.startswith("ioe-")
    if is_be:
        board, level = "IOE", "BE"
    elif grade.isdigit():
        board, level = ("BLE" if grade == "8" else "SEE" if grade == "10" else "NEB"), f"C{grade}"
    else:
        board, level, _ = classify_dir(stem, branch)
        if stem == "12": board, level = "NEB", "C12"
        if "bca" in meta.get("grade", "").lower(): board, level = "TU", "BCA"
    year = meta.get("year_bs", "")
    items, sols = [], {}
    sec_marks, sec_name = 1, "A"
    cur, cur_kind = None, None
    lines = s.split("\n")
    blocks = []  # (kind, num, [lines], sec_marks, sec_name)
    for ln in lines:
        mg = re.match(r"^##\s+Group\s+'?([A-Za-z0-9]+)'?", ln)
        if mg:
            sec_name = mg.group(1); sec_marks = None
            cur = None; continue
        if cur is None and sec_marks is None:
            ms = re.search(r"\[(\d+)\s*[×x]\s*(\d+)\s*=\s*(\d+)\]", ln)
            if ms and "<small>" in ln: sec_marks = int(ms.group(2)); continue
        mk = re.match(r"^@(mcq|q|s)\s+(\d+)\s*$", ln)
        if mk:
            cur = [mk.group(1), int(mk.group(2)), [], sec_marks, sec_name]; blocks.append(cur); continue
        if ln.startswith("@or") and cur is not None:
            cur[2].append("@OR"); continue
        if cur is not None: cur[2].append(ln)
    for kind, num, body, sm, sn in blocks:
        txt = "\n".join(body).strip()
        if kind == "s":
            sols[num] = clean_md(txt); continue
        if "@img" in txt or "@opts-img" in txt or "```" in txt:
            continue  # figure-dependent: not safe for text-only generation
        if kind == "mcq":
            qm = re.split(r"\n@opts(?:-col)?\s+", txt, maxsplit=1)
            if len(qm) != 2: continue
            opts = [clean_md(o) for o in qm[1].split(" | ")]
            if len(opts) != 4: continue
            items.append(dict(kind="mcq", num=num, q=clean_md(qm[0]), opts=opts, marks=sm or 1, sec=sn))
        else:
            main, _, alt = txt.partition("@OR")
            def parts(t):
                ps = []
                for pl in t.strip().split("\n"):
                    pl = pl.strip()
                    if not pl: continue
                    mm = re.match(r"^\(?([a-z])\)\s*(.*?)\s*(?:\[\[([\d+]+)\]\])?$", pl)
                    if mm: ps.append(dict(label=mm.group(1), text=clean_md(mm.group(2)), marks=sum(int(x) for x in (mm.group(3) or "0").split("+") if x)))
                    elif ps: ps[-1]["text"] += " " + clean_md(pl)
                    else: ps.append(dict(label="", text=clean_md(pl), marks=0))
                return ps
            p1, p2 = parts(main), (parts(alt) if alt.strip() else [])
            mt = sum(p["marks"] for p in p1) or (sm or 5)
            items.append(dict(kind="q", num=num, parts=p1, alt_parts=p2, marks=mt, sec=sn))
    out = []
    for it in items:
        rec = dict(src=f"paper:{branch}:{base}", board=board, level=level, subject=subj, year_bs=year,
                   unit=f"Paper {year} {meta.get('code','') if is_be else meta.get('stream','')}".strip(), group=it["sec"])
        if it["kind"] == "mcq":
            rec.update(qtype="MCQ", marks=1, q=it["q"], opts=it["opts"], key="", why="")
        else:
            rec.update(qtype="WRITTEN", marks=it["marks"], parts=it["parts"], alt_parts=it["alt_parts"],
                       sol=sols.get(it["num"], ""))
        out.append(rec)
    return out

# ----------------------------------------------------------------------------- study JSON html parser
GROUP_RE = re.compile(r"Group\s+([A-Z])\s*[—\-–:]?\s*(.*?)(?:\((\d+)\s*marks?\s*each\))?$", re.I)

def li_marks(li):
    for x in iter_nodes(li):
        if x.tag == "span" and x.has("marks"):
            m = re.search(r"\d+", to_text(x))
            if m: return int(m.group())
    return 0

def parse_study_json(path, branch):
    d = json.load(open(path, encoding="utf-8"))
    if not isinstance(d, dict) or not d.get("html"): return []
    parent = os.path.basename(os.path.dirname(path))
    board, level, subj = classify_dir(parent, branch)
    root = parse_html(d["html"])
    unit_title = str(d.get("title", "")).strip()
    cur_unit, grp_marks, grp_name = unit_title, 0, ""
    out, last = [], None
    def walk(n):
        nonlocal cur_unit, grp_marks, grp_name, last
        for k in n.kids:
            if isinstance(k, str): continue
            if k.tag in ("h2", "h3", "h4"):
                t = to_text(k)
                tl = t.lower()
                if "practice question" in tl or "chapter summary" in tl: cur_unit = unit_title
                elif t and not re.match(r"^(answers?|key)\b", tl): cur_unit = t
                continue
            if k.tag == "p":
                st = next((x for x in k.kids if isinstance(x, Node) and x.tag == "strong"), None)
                if st is not None:
                    t = to_text(st)
                    if t.lower().startswith("group"):
                        gm = GROUP_RE.match(t)
                        grp_name = gm.group(1) if gm else ""
                        grp_marks = int(gm.group(3)) if gm and gm.group(3) else (1 if "objective" in t.lower() else 0)
                continue
            if k.tag == "ol":
                items = [x for x in k.kids if isinstance(x, Node) and x.tag == "li"]
                kind = "mcq" if k.has("mcq") else "written"
                batch = []
                for li in items:
                    if has_figure(li): batch.append(None); continue
                    if kind == "mcq":
                        opts_n = next((x for x in iter_nodes(li) if x.tag == "span" and x.has("opts")), None)
                        if opts_n is None: batch.append(None); continue
                        opts = []
                        for o in [x for x in opts_n.kids if isinstance(x, Node) and x.has("opt")]:
                            opts.append(to_text(o, skip=("i",)) if False else strip_label(o))
                        q = to_text(li, skip=("opts", "marks"))
                        q = re.sub(r"\s*\(NEB[^)]*\)\s*$", "", q).strip()
                        src = ""
                        batch.append(dict(qtype="MCQ", marks=1, q=q, opts=opts, key=li.attrs.get("data-key", "")))
                    else:
                        parts_n = next((x for x in iter_nodes(li) if x.tag == "span" and x.has("parts")), None)
                        mk = li_marks(li)
                        if parts_n is not None:
                            stem = to_text(li, skip=("parts", "marks"))
                            ps = []
                            for pn in [x for x in parts_n.kids if isinstance(x, Node) and x.has("part")]:
                                pt = to_text(pn, skip=("marks",))
                                mm = re.match(r"^\(?([a-z])[\).]\s*(.*)$", pt)
                                ps.append(dict(label=mm.group(1) if mm else "", text=mm.group(2) if mm else pt, marks=li_marks(pn)))
                            batch.append(dict(qtype="WRITTEN", marks=mk or grp_marks, stem=stem, parts=ps))
                        else:
                            batch.append(dict(qtype="WRITTEN", marks=mk or grp_marks, stem=to_text(li, skip=("marks",)), parts=[]))
                try: start = int(k.attrs.get("start") or 1)
                except ValueError: start = 1
                last = dict(kind=kind, batch=batch, unit=cur_unit, group=grp_name, gm=grp_marks, start=start)
                for b in batch:
                    if b is None: continue
                    b.update(unit=cur_unit, group=grp_name)
                    out.append(b)
                continue
            if k.tag == "details" and k.has("ans") and last is not None:
                attach_answers(k, last); last = None
                continue
            walk(k)
    walk(root)
    res = []
    for b in out:
        b.update(src=f"study:{branch}:{parent}/{os.path.basename(path)}", board=board, level=level, subject=subj)
        res.append(b)
    return res

def strip_label(opt):
    kids = [x for x in opt.kids if not (isinstance(x, Node) and x.tag == "i" and len(to_text(x)) == 1)]
    n = Node("span"); n.kids = kids
    return to_text(n)

def attach_answers(det, last):
    body = next((x for x in iter_nodes(det) if x.tag == "div" and x.has("ans-body")), None)
    if body is None: return
    ans = {}
    for p in [x for x in body.kids if isinstance(x, Node) and x.tag == "p"]:
        t = to_text(p)
        m = re.match(r"^(\d+)\.\s*(.*)$", t)
        if m: ans[int(m.group(1))] = m.group(2).strip()
    batch = last["batch"]
    for i, b in enumerate(batch):
        if b is None: continue
        a = ans.get(i + last.get("start", 1))
        if not a: continue
        if last["kind"] == "mcq":
            m = re.match(r"^\(([a-d])\)\s*[—\-–:]*\s*(.*)$", a)
            if m and (not b.get("key") or m.group(1) == b["key"]):
                b["key"] = m.group(1); b["why"] = m.group(2).strip()
        else:
            b["sol"] = a

# ----------------------------------------------------------------------------- numbered MCQ markdown (BCA entrance, nursing practice)
OPT_SPLIT = re.compile(r"\(([a-d])\)\s")
ANS_A = re.compile(r"^\*\*(\d+)\.\*\*\s*\(([a-d])\)\s*[—\-–:.]*\s*(.*)$")
ANS_B = re.compile(r"^\*\*(\d+)\.\s*\(([a-d])\)\.?\*\*\s*(.*)$")

def parse_numbered_md(path, branch):
    s = open(path, encoding="utf-8", errors="ignore").read()
    meta = {}
    m = FM.match(s)
    if m:
        for ln in m.group(1).splitlines():
            if ":" in ln:
                k, v = ln.split(":", 1); meta[k.strip()] = v.strip()
        s = s[m.end():]
    low = path.lower()
    if "/bca/" in low: board, level = "TU", "BCA"
    elif "nursing" in low: board, level = "CTEVT", "BSN"
    else: return []
    parts = path.split("/")
    subj = re.sub(r"[^a-z0-9]+", "-", (parts[-2] if "nursing" in low else "bca-" + parts[-3] if len(parts) > 3 else "bca").lower()).strip("-")
    if "nursing" in low and parts[-2] in ("README.md",): subj = "nursing"
    title = meta.get("title") or ""
    pending, out, unit, in_ans, qs_block = [], [], title, False, None
    lines = s.split("\n")
    def flush():
        nonlocal qs_block
        if qs_block is None: return
        num, txt = qs_block; qs_block = None
        txt = re.sub(r"\s+", " ", txt).strip()
        sp = OPT_SPLIT.split(txt)
        if len(sp) != 9 or [sp[1], sp[3], sp[5], sp[7]] != ["a", "b", "c", "d"]: return
        q = clean_md(sp[0]); opts = [clean_md(sp[2]), clean_md(sp[4]), clean_md(sp[6]), clean_md(sp[8])]
        if "```" in txt or not q: return
        pending.append(dict(num=num, rec=dict(qtype="MCQ", marks=1, q=q, opts=opts, key="", why="", unit=unit, group="")))
    for ln in lines:
        h = re.match(r"^#{2,3}\s+(.*)$", ln)
        if h and not in_ans:
            flush(); unit = re.sub(r"^\d+(\.\d+)*\s*", "", h.group(1)).strip()[:80] or unit; continue
        if re.match(r"^:{3,4}\s+note\s+Answers", ln): flush(); in_ans = True; continue
        if in_ans:
            if ln.strip() == ":::" or ln.strip() == "::::":
                in_ans = False; continue
            ma = ANS_A.match(ln.strip()) or ANS_B.match(ln.strip())
            if ma:
                n = int(ma.group(1))
                for pq in reversed(pending):
                    if pq["num"] == n and not pq["rec"]["key"]:
                        pq["rec"]["key"] = ma.group(2); pq["rec"]["why"] = clean_md(ma.group(3)); break
            continue
        mq = re.match(r"^\s{0,3}(\d+)\.\s+(.*)$", ln)
        if mq:
            flush()
            if pending and pending[-1]["num"] >= int(mq.group(1)) and any(p["rec"]["key"] for p in pending):
                out.extend(p["rec"] for p in pending if p["rec"]["key"]); pending.clear()
            qs_block = (int(mq.group(1)), mq.group(2)); continue
        if qs_block is not None:
            if ln.strip() == "" or ln.startswith(("#", ":::", "```")): flush()
            else: qs_block = (qs_block[0], qs_block[1] + " " + ln.strip())
    flush()
    out.extend(p["rec"] for p in pending if p["rec"]["key"])
    for r in out:
        r.update(src=f"book:{branch}:{'/'.join(parts[-3:])}", board=board, level=level, subject=subj)
    return out

# ----------------------------------------------------------------------------- main
def main():
    out_path, root = sys.argv[1], sys.argv[2]
    try:
        import live_status as LS
    except Exception:
        sys.path.insert(0, "/tmp/paperlm")
        try: import live_status as LS
        except Exception: LS = None
    seen, n = set(), 0
    stats = {}
    clones = sorted(d for d in glob.glob(os.path.join(root, "*")) if os.path.isdir(d))
    if LS: LS.update("stage", name="DATA", phase="extracting corpus from NEB branches", detail=f"{len(clones)} branch clones")
    with open(out_path, "w", encoding="utf-8") as fo:
        for cl in clones:
            branch = os.path.basename(cl)
            files = []
            for p in glob.glob(cl + "/**/notes/papers*/**/content/*.md", recursive=True) + glob.glob(cl + "/notes/papers*/**/*.md", recursive=True):
                if "/content/" in p and p not in files: files.append(p)
            studies = sorted(glob.glob(cl + "/backend_python/web/data/study/*/*.json"))
            books = sorted(glob.glob(cl + "/bca/entrance/**/*.md", recursive=True) + glob.glob(cl + "/nursing/course/**/*.md", recursive=True))
            for p in books:
                try: recs = parse_numbered_md(p, branch)
                except Exception as e: print("ERR", p, e); continue
                for r in recs: n += emit(fo, r, seen, stats)
            for p in sorted(files):
                try: recs = parse_paper_md(p, branch)
                except Exception as e: print("ERR", p, e); continue
                for r in recs: n += emit(fo, r, seen, stats)
            for p in studies:
                try: recs = parse_study_json(p, branch)
                except Exception as e: print("ERR", p, e); continue
                for r in recs: n += emit(fo, r, seen, stats)
            print(f"[{branch}] papers={len(files)} study_files={len(studies)} total_unique_so_far={n}", flush=True)
            if LS: LS.update("dataset", raw_items=n, by_level=stats, branches_done=branch)
    print("TOTAL unique raw items:", n); print(json.dumps(stats, indent=1))
    if LS: LS.update("dataset", raw_items=n, by_level=stats)

def norm_key(r):
    if r["qtype"] == "MCQ":
        t = r["q"] + "|" + "|".join(r["opts"])
    else:
        t = (r.get("stem", "") + "|" + "|".join(p["text"] for p in r.get("parts", []))) or ""
    return hashlib.md5(re.sub(r"[^a-z0-9]", "", t.lower()).encode()).hexdigest()

def emit(fo, r, seen, stats):
    k = norm_key(r)
    if k in seen: return 0
    seen.add(k)
    r["id"] = k[:12]
    fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    s = stats.setdefault(r["level"], {"MCQ": 0, "WRITTEN": 0})
    s[r["qtype"]] += 1
    return 1

if __name__ == "__main__":
    main()
