"""Live auto-refreshing cards for the v6 work: semantic verifier, verified content library, item audit and live items.

Installed into the MoLab notebook by molab/install_dashboard.py (or install_v6.py).  Every card reads files that the
running jobs write, so the console shows real progress: verifier training curves, rejection-sampling rounds, the size of
the verified content library and the accuracy of the items the composer emits right now.
"""
import glob
import html as H
import json
import os
import random
import sys
import time

import marimo as mo

REPO = "/tmp/paperlm/repo"
sys.path[:0] = [REPO + "/engine", REPO]

CSS = """<style>
.plx-card{border:1px solid #d9dee7;border-radius:14px;padding:14px 16px;margin:6px 0;background:#fff;box-shadow:0 1px 3px #0001;font-family:ui-sans-serif,system-ui,sans-serif}
.plx-h{font-weight:800;margin-bottom:8px;font-size:15px;color:#0f172a}
.plx-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:10px}
.plx-k{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.06em}
.plx-v{font-size:20px;font-weight:700;color:#0f172a}
.plx-bar{height:9px;background:#e2e8f0;border-radius:6px;overflow:hidden;margin-top:8px}.plx-bar>div{height:100%;background:linear-gradient(90deg,#2563eb,#16a34a)}
.plx-q{background:#f8fafc;border-left:4px solid #2563eb;padding:10px 12px;margin:8px 0;border-radius:6px;white-space:pre-wrap;font-size:13px;color:#0f172a}
.plx-tag{display:inline-block;padding:2px 9px;border-radius:99px;font-size:11px;font-weight:700;color:#fff;margin-right:6px}
.plx-mono{font-family:ui-monospace,monospace;font-size:12px;color:#475569}
</style>"""


def _jl(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return {}


def _lines(p):
    out = []
    try:
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    except Exception:
        pass
    return out


def _stat(k, v):
    return f"<div><div class='plx-k'>{H.escape(str(k))}</div><div class='plx-v'>{H.escape(str(v))}</div></div>"


def _bar(frac, colour=None):
    pct = max(0.0, min(1.0, frac or 0)) * 100
    style = f"width:{pct:.1f}%" + (f";background:{colour}" if colour else "")
    return f"<div class='plx-bar'><div style='{style}'></div></div>"


def _spark(vals, w=520, h=90, colour="#2563eb"):
    if len(vals) < 2:
        return "<i class='plx-mono'>waiting for data…</i>"
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-9:
        hi = lo + 1e-9
    pts = " ".join(f"{20 + i / (len(vals) - 1) * (w - 30):.1f},{8 + (1 - (v - lo) / (hi - lo)) * (h - 24):.1f}" for i, v in enumerate(vals))
    return (f"<svg width='{w}' height='{h}' xmlns='http://www.w3.org/2000/svg'>"
            f"<polyline fill='none' stroke='{colour}' stroke-width='2' points='{pts}'/>"
            f"<text x='2' y='14' font-size='10' fill='#64748b'>{hi:.3f}</text>"
            f"<text x='2' y='{h-4}' font-size='10' fill='#64748b'>{lo:.3f}</text></svg>")


# ------------------------------------------------------------------ 1. verifier
def verifier():
    log = _lines("/tmp/paperlm/vf/verifier_log.jsonl")
    st = _jl("/tmp/paperlm/vf/stats.json")
    steps = [r for r in log if "step" in r]
    epochs = [r for r in log if r.get("event") == "epoch"]
    losses = [r["loss"] for r in steps][-120:]
    aucs = [r["val_auc"] for r in epochs]
    done = _jl("/tmp/paperlm/vf/done.json")
    last = epochs[-1] if epochs else {}
    running = len(steps) > 0 and not done
    badge = ("🟢 TRAINING" if running else "✅ DONE") if steps else "⏳ NOT STARTED"
    body = CSS + f"""<div class='plx-card'><div class='plx-h'>🧪 Semantic verifier — trained on verified items vs the LM's gate-passing junk
    <span class='plx-tag' style='background:{'#2563eb' if running else '#16a34a'}'>{badge}</span></div>
    <div class='plx-grid'>{_stat('params', '3.5M (char cross-encoder)')}{_stat('train pairs', f"{st.get('train', 0):,}")}
    {_stat('positives (verified)', f"{st.get('positive', 0):,}")}{_stat('negatives (junk/mismatch)', f"{st.get('negative', 0):,}")}
    {_stat('hard LM negatives', f"{st.get('kinds', {}).get('lm_gate_pass', 0):,}")}
    {_stat('epoch', f"{last.get('epoch', 0) + 1}/{len(epochs) or 3}")}{_stat('val AUC', f"{last.get('val_auc', float('nan')):.4f}" if last else '–')}
    {_stat('val precision', f"{last.get('val_precision', 0):.3f}" if last else '–')}</div>
    <div style='margin-top:8px'><div class='plx-k'>training loss</div>{_spark(losses)}</div>
    <div><div class='plx-k'>validation AUC per epoch</div>{_spark(aucs, colour='#16a34a')}</div>
    <div class='plx-mono'>steps logged: {len(steps)} · last: {H.escape(json.dumps(steps[-1]) if steps else '–')}</div></div>"""
    return mo.Html(body)


# ------------------------------------------------------------------ 2. library
def library():
    facts = _jl(os.path.join(REPO, "docs", "model", "facts.json"))
    templates = _jl("/tmp/paperlm/engine/param_templates.json") or _jl(os.path.join(REPO, "engine", "param_templates.json"))
    bank = _jl(os.path.join(REPO, "docs", "model", "bank.json"))
    cat = _jl(os.path.join(REPO, "docs", "model", "catalog.json"))
    classes = facts.get("classes", [])
    rows = sum(len(c.get("pairs", [])) for c in classes)
    mcq = sum(len(c.get("pairs", [])) for c in classes) + sum(len(c.get("pairs", [])) for c in classes if c.get("qb"))
    seeds = sum(len(v) for s in bank.get("seeds", {}).values() for v in s.values())
    subjects = sum(len(e.get("subjects", {})) for e in cat.values())
    units = sum(len(s.get("units", [])) for e in cat.values() for s in e.get("subjects", {}).values())
    # which catalog subjects have at least one verified fact class
    import re
    covered = 0
    tot = 0
    for e in cat.values():
        for subj in e.get("subjects", {}):
            tot += 1
            if any(any(re.search(p, subj, re.I) for p in c.get("subjects", [])) for c in classes):
                covered += 1
    rowshtml = "".join(
        f"<tr><td style='padding-right:8px'>{H.escape(c['label'])}</td><td align=right>{len(c['pairs'])}</td>"
        f"<td style='padding-left:10px' class='plx-mono'>{H.escape(c['id'])}</td></tr>"
        for c in sorted(classes, key=lambda c: -len(c["pairs"]))[:14])
    body = CSS + f"""<div class='plx-card'><div class='plx-h'>📚 Verified content library (knowledge that cannot be hallucinated)</div>
    <div class='plx-grid'>{_stat('fact classes', len(classes))}{_stat('fact rows', rows)}{_stat('derivable MCQs', f"{mcq:,}")}
    {_stat('formula templates', len(templates.get('templates', [])))}{_stat('gold bank seeds', f"{seeds:,}")}
    {_stat('boards', len(cat))}{_stat('subjects', subjects)}{_stat('units', units)}</div>
    <div style='margin-top:10px' class='plx-k'>subjects with a verified fact class: {covered}/{tot}</div>{_bar(covered / max(1, tot))}
    <table style='margin-top:10px;font-size:12.5px'><tr><th align=left>class</th><th align=right>rows</th><th align=left>id</th></tr>{rowshtml}</table></div>"""
    return mo.Html(body)


# ------------------------------------------------------------------ 3. audit
def audit():
    a = _jl("/tmp/paperlm/status_audit.json")
    if not a:
        return mo.Html(CSS + "<div class='plx-card'><div class='plx-h'>🔍 Item accuracy audit</div><i>audit not run yet…</i></div>")
    tiers = a.get("tiers", {})
    t = "".join(f"<span class='plx-tag' style='background:#475569'>{H.escape(k)} {v}</span>" for k, v in sorted(tiers.items(), key=lambda kv: -kv[1]))
    acc = a.get("accuracy", 0)
    body = CSS + f"""<div class='plx-card'><div class='plx-h'>🔍 Independent item audit — every answer re-derived, not trusted
    <span class='plx-tag' style='background:{"#16a34a" if acc >= 0.999 else "#d97706"}'>{acc*100:.2f}% accurate</span></div>
    <div class='plx-grid'>{_stat('requests', f"{a.get('n', 0):,}")}{_stat('emitted', f"{a.get('emitted', 0):,}")}
    {_stat('unresolved', a.get('unresolved_requests', 0))}{_stat('verified items', f"{a.get('verified_items', 0):,}")}
    {_stat('failures', sum(a.get('failures_by_tier', {}).values()))}</div>
    {_bar(acc)}
    <div style='margin-top:8px'>{t}</div>
    <div class='plx-mono'>reasons: {H.escape(json.dumps(a.get('failure_reasons', {}))[:400])}</div></div>"""
    return mo.Html(body)


# ------------------------------------------------------------------ 4. live items
def items(n=3):
    """Freshly composed verified items, regenerated on every refresh (seeded by the clock)."""
    import factbank
    import parametric as PM
    try:
        fb = factbank.FactBank(os.path.join(REPO, "docs", "model", "facts.json"))
    except Exception:
        return mo.Html(CSS + "<div class='plx-card'>fact bank unavailable</div>")
    rng = random.Random(int(time.time() // 3))
    reqs = [("NEB", "C12", "physics", "Kinematics", 1, "MCQ"), ("NEB", "C12", "biology", "Human Biology", 1, "MCQ"),
            ("NEB", "C12", "chemistry", "Chemical equilibrium", 4, "NUMERICAL"), ("SEE", "C10", "science", "Pressure", 1, "MCQ"),
            ("IOE", "IOE", "mental-agility-test", "Numerical Reasoning", 1, "MCQ"), ("CTEVT", "BSN", "fundamentals-of-nursing", "General", 1, "MCQ"),
            ("SEE", "C10", "social-studies", "Unit 1: Our Society and We", 1, "MCQ"), ("NEB", "C12", "english", "On Libraries", 5, "SHORT")]
    blocks = []
    for _ in range(n):
        board, level, subj, unit, marks, typ = reqs[rng.randrange(len(reqs))]
        it = None
        if typ == "MCQ" or marks <= 1:
            it = fb.make_item(subj, unit, marks, typ, rng.random)
        if it is None:
            it = PM.make_item(subj, level, unit, marks, typ, rng)
            tier = "computed"
        else:
            tier = "fact"
        if not it:
            continue
        colour = "#16a34a" if tier == "fact" else "#2563eb"
        q = it["question"]
        opts = ""
        if it.get("options"):
            opts = "<div style='margin-top:6px'>" + "".join(
                f"<div style='font-size:12.5px'><b>{'abcd'[i].upper()}.</b> {H.escape(str(o))}"
                f"{' <span class=plx-tag style=background:#16a34a>key</span>' if 'abcd'[i] == it['key'] else ''}</div>"
                for i, o in enumerate(it["options"])) + "</div>"
        else:
            opts = f"<div class='plx-mono'>answer: {H.escape((it.get('rubric') or '')[:260])}</div>"
        blocks.append(f"<div class='plx-q'><span class='plx-tag' style='background:{colour}'>{tier}</span>"
                      f"<span class='plx-mono'>{H.escape(board)} · {H.escape(subj)} · {H.escape(unit)} · {marks}m</span>\n"
                      f"{H.escape(q)}{opts}</div>")
    return mo.Html(CSS + f"<div class='plx-card'><div class='plx-h'>🧾 Live verified items — recomposed every refresh</div>{''.join(blocks)}</div>")


# ------------------------------------------------------------------ 5. GPU / keepalive
def system():
    try:
        import subprocess
        q = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10).stdout.strip().split(",")
        name, used, total, util, temp, power = [x.strip() for x in q]
    except Exception:
        name, used, total, util, temp, power = "n/a", 0, 1, 0, 0, 0
    hb = {}
    try:
        hb = json.loads(open("/tmp/paperlm/heartbeat.txt").read().strip().split("\n")[-1].split(" ", 1)[1].replace("count=", "{\"count\":").replace(" local", ",\"local\":").replace(" public", ",\"public\":") + "}")
    except Exception:
        hb = {}
    procs = ""
    try:
        import subprocess
        out = subprocess.run(["bash", "-lc", "ps -eo comm,args --no-headers | grep -E 'rft4|verifier|train_v2|pipeline' | grep -v grep | awk '{print $1}' | sort | uniq -c"], capture_output=True, text=True, timeout=10).stdout.strip()
        procs = out.replace("\n", " · ") or "none"
    except Exception:
        pass
    ver = _lines("/tmp/paperlm/vf/verifier_log.jsonl")
    last = ver[-1] if ver else {}
    body = CSS + f"""<div class='plx-card'><div class='plx-h'>🖥️ GPU & keep-alive</div>
    <div class='plx-grid'>{_stat('GPU', name.replace('NVIDIA ', ''))}{_stat('VRAM', f"{float(used)/1024:.1f} / {float(total)/1024:.0f} GB")}
    {_stat('util', f"{util}%")}{_stat('temp', f"{temp} °C")}{_stat('power', f"{power} W")}
    {_stat('keep-alive pings', hb.get('count', '–'))}</div>
    {_bar(float(used) / max(1.0, float(total)))}
    <div class='plx-mono'>running: {H.escape(procs)} · last log: {H.escape(json.dumps(last)[:200])}</div></div>"""
    return mo.Html(body)


def vstack():
    return mo.vstack([verifier(), library(), audit(), items(), system()])
