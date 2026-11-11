"""Live card: PaperLM v5 composed system (symbolic engine + grounded LM behind strict gate + verified bank). Reads /tmp/paperlm/status_system.json."""
import html as H, json, os
import marimo as mo


def _j(p):
    try: return json.load(open(p))
    except Exception: return {}


def system():
    s = _j("/tmp/paperlm/status_system.json"); pt = _j("/tmp/paperlm/param_test.json"); lm = s.get("lm_tier", [])
    rows = "".join(f"<tr><td>copy-bias β={H.escape(str(r['beta']))}</td><td align=right>{r['gate_pass']}/{r['tries']}</td><td align=right><b>{100*r['gate_pass']/max(1,r['tries']):.1f}%</b></td><td align=right>{r['structurally_valid']}</td></tr>" for r in lm)
    tiers = s.get("tiers", {}); tot = max(1, sum(tiers.values()))
    bars = "".join(f"<div style='margin:3px 0;font-size:12.5px'><span style='display:inline-block;width:150px'>{H.escape(k)}</span><span style='display:inline-block;height:10px;width:{int(220*v/tot)}px;background:#6750a4;border-radius:5px;vertical-align:middle'></span> {v} ({100*v/tot:.0f}%)</div>" for k, v in tiers.items())
    pts = f"{pt.get('templates', '-')} templates · {pt.get('instances', '-')} instances · self-check failures <b>{pt.get('self_check_failures', '-')}</b> · known-value failures <b>{pt.get('known_value_failures', '-')}</b> · py↔js parity failures <b>{pt.get('parity_failures', '-')}</b>"
    return mo.Html(f"<div style='font-family:Poppins,system-ui,sans-serif;border:1px solid #cac4d0;border-radius:16px;padding:16px;margin:6px 0'><div style='font-weight:800;margin-bottom:6px'>⚙️ PaperLM v5 composed system (live)</div>"
                   f"<div style='font-size:13px;margin-bottom:8px'>{pts}</div><div style='font-size:13px;font-weight:600;margin:6px 0'>Node end-to-end tier mix ({s.get('n', '-')} items, failures {s.get('fail', '-')})</div>{bars}"
                   f"<div style='font-size:13px;font-weight:600;margin:8px 0 2px'>LM-tier strict-gate yield</div><table style='font-size:13px'><tr><th align=left>decoding</th><th align=right>pass</th><th align=right>rate</th><th align=right>valid</th></tr>{rows}</table>"
                   f"<div style='font-size:12px;opacity:.7;margin-top:6px'>{H.escape(s.get('note', ''))}</div></div>")
