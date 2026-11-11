"""Rendering helpers for the PaperLM live Marimo dashboard (reads /tmp/paperlm_live_status.json)."""
import html as H, json, time
import marimo as mo

SRC = "/tmp/paperlm_live_status.json"

def load():
    try:
        return json.load(open(SRC))
    except Exception:
        return {}

def _fmt_s(s):
    s = int(max(0, s or 0)); h, r = divmod(s, 3600); m, sec = divmod(r, 60)
    return f"{h}h {m:02d}m {sec:02d}s" if h else f"{m}m {sec:02d}s"

def _n(x, d=0):
    try: return f"{float(x):,.{d}f}"
    except Exception: return "–"

CSS = """<style>
.pl-card{border:1px solid #d9dee7;border-radius:14px;padding:14px 16px;margin:6px 0;background:#fff;box-shadow:0 1px 3px #0001}
.pl-badge{display:inline-block;padding:3px 12px;border-radius:99px;font-weight:700;font-size:13px;color:#fff;background:#2563eb;margin-right:8px}
.pl-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.pl-k{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.06em}
.pl-v{font-size:22px;font-weight:700;color:#0f172a}
.pl-bar{height:9px;background:#e2e8f0;border-radius:6px;overflow:hidden}.pl-bar>div{height:100%;background:linear-gradient(90deg,#2563eb,#16a34a)}
.pl-q{background:#f8fafc;border-left:4px solid #2563eb;padding:8px 12px;margin:6px 0;border-radius:6px;white-space:pre-wrap;font-family:ui-monospace,monospace;font-size:12.5px}
</style>"""

def _stat(k, v):
    return f'<div><div class="pl-k">{H.escape(str(k))}</div><div class="pl-v">{H.escape(str(v))}</div></div>'

def _bar(frac):
    return f'<div class="pl-bar"><div style="width:{max(0,min(1,frac))*100:.1f}%"></div></div>'

def header():
    S = load(); g = S.get("gpu", {}); st = S.get("stage", {}); ka = S.get("keepalive", {})
    age = time.time() - S.get("updated", 0) if S else 9999
    live = "🟢 LIVE" if age < 15 else "🔴 STALE"
    vu, vt = g.get("vram_used_mb", 0), g.get("vram_total_mb", 1) or 1
    hb = ka.get("last"); hb_age = (time.time() - hb) if hb else None
    h = CSS + f"""<div class="pl-card"><div style="font-size:20px;font-weight:800">📜 PaperLM-Tiny — Board Setter Brain · live training console</div>
    <div style="margin:8px 0"><span class="pl-badge">{H.escape(str(st.get('name','IDLE')))}</span>
    <span style="font-weight:600">{H.escape(str(st.get('phase','waiting for pipeline…')))}</span> <span style="color:#64748b">{H.escape(str(st.get('detail','')))}</span> · {live}</div>
    <div class="pl-grid">{_stat('GPU', str(g.get('name','n/a')).replace('NVIDIA ','').replace(' Server Edition',''))}
    {_stat('VRAM', f"{vu/1024:.1f} / {vt/1024:.0f} GB")}{_stat('GPU util', f"{g.get('util',0):.0f}%")}
    {_stat('Temp / Power', f"{g.get('temp',0):.0f}°C · {g.get('power_w',0):.0f}W")}
    {_stat('Uptime', _fmt_s(S.get('uptime_s',0)))}{_stat('Keep-alive pings', f"{ka.get('count',0)} (last {_fmt_s(hb_age) if hb_age is not None else '–'} ago)")}</div>
    {_bar(vu/vt)}</div>"""
    return mo.Html(h)

def dataset():
    S = load(); d = S.get("dataset", {})
    lv = d.get("by_level", {})
    rows = "".join(f"<tr><td>{H.escape(k)}</td><td style='text-align:right'>{v.get('MCQ',0):,}</td><td style='text-align:right'>{v.get('WRITTEN',0):,}</td></tr>" for k, v in sorted(lv.items()))
    ty = d.get("by_type", {}); ty_s = " · ".join(f"{k}: {v:,}" for k, v in ty.items())
    h = CSS + f"""<div class="pl-card"><div style="font-weight:800;margin-bottom:6px">📚 Corpus & dataset</div>
    <div class="pl-grid">{_stat('Raw items extracted', _n(d.get('raw_items')))}{_stat('Gold (validated)', _n(d.get('gold_items')))}
    {_stat('Rejected by validator', _n(d.get('rejected')))}{_stat('Total tokens', _n(d.get('tokens')))}{_stat('Vocab', _n(d.get('vocab')))}
    {_stat('Past papers parsed', _n(d.get('papers')))}</div>
    <div style="margin-top:8px;font-size:13px;color:#475569">{H.escape(ty_s)}</div>
    <table style="margin-top:8px;font-size:13px;min-width:320px"><tr><th align=left>Level</th><th>MCQ</th><th>Written</th></tr>{rows}</table></div>"""
    return mo.Html(h)

def loss_svg(hist, w=720, hgt=220):
    if len(hist) < 2: return "<i>waiting for first evaluations…</i>"
    xs = [p[0] for p in hist]; ys = [v for p in hist for v in (p[1], p[2]) if v is not None]
    x0, x1 = min(xs), max(xs) or 1; y0, y1 = min(ys), max(ys)
    if y1 - y0 < 1e-6: y1 = y0 + 1
    def X(x): return 40 + (x - x0) / max(1e-9, (x1 - x0)) * (w - 55)
    def Y(y): return 12 + (1 - (y - y0) / (y1 - y0)) * (hgt - 38)
    def line(i, col):
        pts = " ".join(f"{X(p[0]):.1f},{Y(p[i]):.1f}" for p in hist if p[i] is not None)
        return f'<polyline fill="none" stroke="{col}" stroke-width="2" points="{pts}"/>'
    grid = "".join(f'<line x1="40" x2="{w-15}" y1="{Y(y0+(y1-y0)*t/4):.1f}" y2="{Y(y0+(y1-y0)*t/4):.1f}" stroke="#e2e8f0"/><text x="2" y="{Y(y0+(y1-y0)*t/4)+4:.1f}" font-size="10" fill="#64748b">{y0+(y1-y0)*t/4:.2f}</text>' for t in range(5))
    return f'<svg width="{w}" height="{hgt}" xmlns="http://www.w3.org/2000/svg">{grid}{line(1,"#2563eb")}{line(2,"#dc2626")}<text x="50" y="{hgt-6}" font-size="11" fill="#2563eb">● train loss</text><text x="140" y="{hgt-6}" font-size="11" fill="#dc2626">● val loss</text><text x="{w-110}" y="{hgt-6}" font-size="11" fill="#64748b">step {int(x1):,}</text></svg>'

def training():
    S = load(); t = S.get("train", {})
    if not t: return mo.Html(CSS + '<div class="pl-card">🏋️ Training not started yet.</div>')
    st, tot = t.get("step", 0), t.get("total_steps", 1) or 1
    h = CSS + f"""<div class="pl-card"><div style="font-weight:800;margin-bottom:6px">🏋️ Live training telemetry — {H.escape(str(t.get('model','PaperLM-Tiny')))} · {_n(t.get('params'))} params</div>
    <div class="pl-grid">{_stat('Step', f'{st:,} / {tot:,}')}{_stat('Epoch', _n(t.get('epoch'),2))}{_stat('Train loss', _n(t.get('train_loss'),4))}
    {_stat('Val loss', _n(t.get('val_loss'),4))}{_stat('Perplexity', _n(t.get('ppl'),2))}{_stat('LR', f"{t.get('lr',0):.2e}")}
    {_stat('Tokens/s', _n(t.get('tok_s')))}{_stat('ETA', _fmt_s(t.get('eta_s')))}{_stat('Best val', _n(t.get('best_val'),4))}</div>
    <div style="margin:8px 0">{_bar(st/tot)}</div>{loss_svg(t.get('history', []))}</div>"""
    return mo.Html(h)

def samples():
    S = load(); sm = S.get("samples", {})
    items = sm.get("items", [])
    if not items: return mo.Html(CSS + '<div class="pl-card">✍️ No generated samples yet — they appear at each checkpoint.</div>')
    body = "".join(f'<div class="pl-q">{H.escape(x)}</div>' for x in items[-6:])
    return mo.Html(CSS + f'<div class="pl-card"><div style="font-weight:800">✍️ Latest board-setter output @ step {sm.get("step","?")} — validator pass-rate {_n(sm.get("valid_rate",0)*100,1)}%</div>{body}</div>')

def eval_card():
    S = load(); e = S.get("eval", {})
    if not e: return mo.Html("")
    rows = "".join(f"<tr><td>{H.escape(str(k))}</td><td>{H.escape(str(v))}</td></tr>" for k, v in e.items() if k != "_t")
    return mo.Html(CSS + f'<div class="pl-card"><div style="font-weight:800">📏 Evaluation</div><table style="font-size:13px">{rows}</table></div>')
