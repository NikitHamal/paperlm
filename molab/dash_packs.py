"""Live 3 s cards: GPU/keep-alive, teacher distillation progress, specialist pack training losses + real generated samples."""
import glob, html as H, json, os, time
import marimo as mo
def _j(p):
    try: return json.load(open(p))
    except Exception: return {}
def _bar(f, col="#386a20"):
    f = max(0, min(1, f)); return f"<div style='background:#e1e4d8;border-radius:8px;height:10px'><div style='width:{100*f:.1f}%;background:{col};height:10px;border-radius:8px'></div></div>"
def _card(title, body):
    return mo.Html(f"<div style='font-family:system-ui,sans-serif;border:1px solid #c4c8bb;border-radius:20px;padding:16px 18px;margin:6px 0;background:#fdfdf5'><div style='font-weight:700;margin-bottom:8px;color:#1a1c16'>{title}</div>{body}</div>")
def _spark(vals, w=360, h=60, col="#386a20"):
    if len(vals) < 2: return ""
    lo, hi = min(vals), max(vals); pts = " ".join(f"{i*w/(len(vals)-1):.1f},{h-(v-lo)/(hi-lo+1e-9)*(h-6)-3:.1f}" for i, v in enumerate(vals))
    return f"<svg width='{w}' height='{h}'><polyline fill='none' stroke='{col}' stroke-width='2' points='{pts}'/></svg>"
def gpu():
    S = _j("/tmp/paperlm_live_status.json"); g = S.get("gpu", {}); ka = S.get("keepalive", {}); hb = ""
    try: hb = open("/tmp/paperlm/heartbeat.txt").read().strip()
    except Exception: pass
    body = f"<div style='font-size:13px'>{H.escape(str(g.get('name','')))} - util {g.get('util','-')}% - VRAM {g.get('vram_used_mb',0)/1024:.1f}/{g.get('vram_total_mb',0)/1024:.0f} GB - {g.get('temp','-')} C - {g.get('power_w','-')} W</div>{_bar(g.get('util',0)/100)}<div style='font-size:12px;margin-top:6px'>keep-alive (60 s): {H.escape(hb)}</div>"
    return _card("GPU and keep-alive", body)
def teacher():
    s = _j("/tmp/paperlm/status_packs.json"); tot = max(1, s.get("total", 1)); age = time.time() - s.get("t", 0)
    body = f"<div style='font-size:13px'>pack <b>{s.get('pack','-')}</b> stage <b>{s.get('stage','-')}</b> - kept {s.get('kept','-')} of raw {s.get('raw','-')} - eta {s.get('eta_min','-')} min - updated {age:.0f}s ago</div>{_bar(s.get('done',0)/tot)}"
    return _card("Teacher distillation with verification (Qwen2.5-32B: blind solve, entailment, distractor probe)", body)
def training():
    rows = ""
    for p in sorted(glob.glob("/tmp/paperlm/status_train_*.json")):
        s = _j(p); c = s.get("curve", []); v = [x["val"] for x in c]; b = s.get("bench", {}) or {}
        rows += (f"<div style='margin:8px 0;padding-top:8px;border-top:1px solid #e1e4d8'><b>{s.get('pack')}</b> - {s.get('stage')} step {s.get('step','')} - params {s.get('params',0)/1e6:.2f}M"
                 f"<div style='font-size:12px'>val loss {v[-1] if v else '-'} - strict-gate {b.get('strict_gate_rate','-')} - grounding {round(b.get('mean_grounding',0),3) if b else '-'}</div>{_spark(v)}</div>")
    return _card("Specialist pack training (val loss curves)", rows or "waiting for first pack")
def samples():
    out = ""
    for p in sorted(glob.glob("/tmp/packs/*/out/samples.json")):
        pid = p.split("/")[3]; ss = _j(p)
        for x in (ss[:3] if isinstance(ss, list) else []):
            g = x["segs"]; txt = (f"Q: {g[1]}\n  key: {g[0]}\n  distractors: {' | '.join(g[2:5])}\n  why: {g[5]}" if x["type"] == "mcq" and len(g) >= 6 else f"Q: {g[1] if len(g)>1 else ''}\n  A: {g[0] if g else ''}")
            out += f"<div style='font-size:12px;margin:6px 0;white-space:pre-wrap;font-family:ui-monospace,monospace;background:#f1f1e8;border-radius:10px;padding:8px'>[{pid}] {H.escape(x['unit'])} (score {x['score']}, gate {x['gate']})\n{H.escape(txt)}</div>"
    return _card("Real generated questions (verbatim, by the specialist 10M models)", out or "none yet")
def chain():
    """wave7 pipeline card: verified teacher items per pack, stage flags, and the live bank-QA reports of the shipped packs."""
    ids = "bio12 phy11 bio11 phy12 chem11 chem12 math11 math12 cs11 cs12".split(); rows = ""
    for p in ids:
        n = 0
        for f in glob.glob(f"/tmp/packs/{p}/verified*.jsonl"):
            try: n += sum(1 for _ in open(f))
            except Exception: pass
        done = os.path.exists(f"/tmp/paperlm/TRAINED_{p}")
        rows += f"<div style='font-size:12px;margin:3px 0'><b>{p}</b> verified teacher items {n} {_bar(min(1, n/300))} {'trained + exported' if done else ''}</div>"
    fl = [("TEACHER7_DONE", "teacher rounds"), ("WAVE7_DONE", "train + export + publish + push")]
    st = " - ".join(f"{t}: {'done' if os.path.exists('/tmp/paperlm/'+f) else 'pending'}" for f, t in fl)
    qa = ""
    for p in sorted(glob.glob("/work/paperlm/packs/*/bank_qa_report.json")):
        r = _j(p); qa += f"<div style='font-size:12px'>{r.get('pack')}: bank {r.get('bank_in')} -> {r.get('bank_kept')} ({r.get('mcq')} MCQ, {r.get('written')} written) drops {H.escape(json.dumps(r.get('reasons')))}</div>"
    return _card("wave7 chain (teacher -> train -> TFLite -> publish -> push) and bank QA", f"<div style='font-size:13px;margin-bottom:6px'>{st}</div>{rows}<div style='margin-top:8px;font-weight:600;font-size:12px'>Bank QA gate</div>{qa}")
