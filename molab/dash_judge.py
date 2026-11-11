"""Live cards (3 s refresh): 32B LLM-judge audit of the gold bank + GPU-grounded generation pipeline. Reads status_judge.json / status_gen.json / judge_summary.json."""
import html as H, json, os, time
import marimo as mo

def _j(p):
    try: return json.load(open(p))
    except Exception: return {}

def _bar(f, col="#6750a4"):
    f = max(0, min(1, f)); return f"<div style='background:#eee;border-radius:8px;height:12px;width:100%'><div style='width:{100*f:.1f}%;background:{col};height:12px;border-radius:8px'></div></div>"

def _card(title, body):
    return mo.Html(f"<div style='font-family:Poppins,system-ui,sans-serif;border:1px solid #cac4d0;border-radius:16px;padding:16px;margin:6px 0'><div style='font-weight:800;margin-bottom:8px'>{title}</div>{body}</div>")

def judge():
    s = _j("/tmp/paperlm/status_judge.json"); sm = _j("/tmp/paperlm/judge_summary.json")
    age = time.time() - s.get("ts", 0); tot = max(1, s.get("total", 1)); dn = s.get("done", 0)
    body = (f"<div style='font-size:13px'>stage <b>{H.escape(str(s.get('stage','-')))}</b> · {H.escape(str(s.get('msg','')))} · elapsed {s.get('elapsed','-')} s · updated {age:.0f}s ago</div>"
            f"<div style='margin:8px 0'>{_bar(dn/tot)}<div style='font-size:12px'>{dn} / {s.get('total','-')} ({100*dn/tot:.1f}%)</div></div>")
    if sm:
        rows = "".join(f"<tr><td>{H.escape(str(k))}</td><td align=right><b>{H.escape(str(v))}</b></td></tr>" for k, v in sm.items())
        body += f"<table style='font-size:13px'>{rows}</table>"
    return _card("⚖️ Qwen2.5-32B judge audit of the gold bank (independent solve + correctness judge)", body)

def gen():
    s = _j("/tmp/paperlm/status_gen.json")
    if not s: return _card("🧪 Teacher generation + self-consistency verification", "<div style='font-size:13px'>not started</div>")
    tot = max(1, s.get("total", 1)); dn = s.get("done", 0)
    rows = "".join(f"<tr><td>{H.escape(str(k))}</td><td align=right><b>{H.escape(str(v))}</b></td></tr>" for k, v in s.get("counts", {}).items())
    body = (f"<div style='font-size:13px'>{H.escape(str(s.get('msg','')))} · elapsed {s.get('elapsed','-')} s</div><div style='margin:8px 0'>{_bar(dn/tot,'#2e7d32')}<div style='font-size:12px'>{dn} / {s.get('total','-')}</div></div>"
            f"<table style='font-size:13px'>{rows}</table>")
    ex = s.get("last")
    if ex: body += f"<pre style='white-space:pre-wrap;font-size:12px;background:#f6f2fa;border-radius:10px;padding:8px;margin-top:8px'>{H.escape(str(ex))[:900]}</pre>"
    return _card("🧪 Teacher generation + self-consistency verification", body)
