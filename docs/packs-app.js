import * as ort from "./vendor/ort/ort.wasm.min.mjs";
import { Pack, loadRegistry, planPaper, rng32 } from "./packlm.js";
import { Parametric } from "./parametric.js";
ort.env.wasm.numThreads = 1; ort.env.wasm.wasmPaths = new URL("vendor/ort/", location.href).href;
const $ = (id) => document.getElementById(id), esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const math = (s) => esc(s).replace(/\$([^$]+)\$/g, (m, t) => { try { return window.katex.renderToString(t.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">"), { throwOnError: true, strict: "ignore" }); } catch { return `<code>${t}</code>`; } });
let reg, pack = null, param = null, numIds = [], busy = false, mode = "one";
const setStatus = (t) => ($("status").textContent = t);
function renderChips() {
  $("packs").innerHTML = reg.packs.map((p) => `<button class="chip" role="radio" aria-checked="false" data-id="${p.pack_id}"><b>${esc(p.title)}</b><span>${p.pack_id} - ${(p.params / 1e6).toFixed(1)}M params - ${p.onnx_mb} MB INT8</span></button>`).join("");
  $("packs").onclick = (e) => { const b = e.target.closest(".chip"); if (b) selectPack(b.dataset.id); };
}
async function selectPack(id) {
  if (busy) return; busy = true; document.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-checked", c.dataset.id === id)); $("load").hidden = false; $("controls").hidden = true;
  try { if (pack) { await pack.session.release?.(); pack = null; }
    pack = await Pack.load(ort, id, "packs/", (f, w) => { $("loadbar").style.width = f * 100 + "%"; $("loadtxt").textContent = w; });
    $("unit").innerHTML = `<option value="*">All units (syllabus-weighted)</option>` + pack.graph.units.map((u) => `<option value="${u.id}">${esc(u.name)}</option>`).join("");
    const m = pack.meta; $("packinfo").innerHTML = `<b>${esc(m.title)}</b>: ${(m.params / 1e6).toFixed(2)}M parameters, ${m.onnx_mb} MB INT8 ONNX, 4096-token subject-pure BPE, ${pack.graph.units.length} syllabus units, validation loss ${m.val_loss}. Offline benchmark: ${(m.bench.strict_gate_rate * 100).toFixed(0)}% of best-of-4 samples pass the strict grounding gate.`;
    numIds = []; try { numIds = await (await fetch(`packs/${id}/numeric_templates.json`)).json(); } catch {}
    const lib = await (await fetch("model/templates.json")).json(); lib.templates = lib.templates.filter((t) => numIds.includes(t.id)); param = new Parametric(lib);
    $("type").querySelector('[value="num"]').disabled = !numIds.length; $("p-num").disabled = !numIds.length; if (!numIds.length) $("p-num").value = 0;
    $("controls").hidden = false; $("load").hidden = true;
  } catch (e) { $("packinfo").textContent = "Could not load pack: " + e.message; } busy = false;
}
const numUse = {};
function numeric(unit, rand) {
  // v13: prefer templates taught in this blueprint unit, then the least-used template (anti-duplication across a paper)
  const all = param.lib.templates, nm = (unit && unit.name || "").toLowerCase(), m = all.filter((x) => x.unit.toLowerCase() === nm), ts = m.length ? m : all;
  const least = Math.min(...ts.map((x) => numUse[x.id] || 0)), pool = ts.filter((x) => (numUse[x.id] || 0) === least), t = pool[Math.floor(rand() * pool.length)];
  numUse[t.id] = (numUse[t.id] || 0) + 1; const inst = param.instantiate(t, rand); if (!inst) return null; const r = param.render(inst, rand);
  return { kind: "mcq", numeric: true, marks: 1, unit: t.unit, question: r.stem, options: r.options, key: r.key, why: `${r.law} ${r.steps.join(" ")}`, anchor: r.law, score: 1, flags: { computed: 1 } };
}
function card(it, n) {
  const ans = it.kind === "mcq" ? `<b>Answer: (${it.key}) ${math(it.options["abcd".indexOf(it.key)])}</b><br>${math(it.why)}` : `<b>Model answer</b><br>${math(it.answer)}`;
  const opts = it.kind === "mcq" ? it.options.map((o, i) => `<div class="opt${"abcd"[i] === it.key ? " key" : ""}"><b>${"abcd"[i]})</b><span>${math(o)}</span></div>`).join("") : "";
  const prov = it.flags && it.flags.bank ? `<span class="tag ok">verified bank: ${it.src === "gold" ? "NEB gold item" : "teacher + blind-solve + entailment + distractor probes"}</span><span class="tag">unit: ${esc(it.unit)}</span>${it.scores ? `<span class="tag">solve ${it.scores.solve ?? "-"}</span><span class="tag">entail ${it.scores.entail ?? "-"}</span>` : ""}<br>Source fact: ${math(it.anchor.slice(0, 260))}` : it.numeric ? `<span class="tag ok">computed by exact solver</span>` : `<span class="tag ok">grounding ${it.score.toFixed(2)}</span><span class="tag">answer-in-anchor ${(it.flags.ans_ground * 100) | 0}%</span><span class="tag">unit: ${esc(it.unit)}</span><br>Anchor fact: ${math(it.anchor)}`;
  return `<div class="q"><h3>Q${n} - ${it.kind === "mcq" ? "MCQ, 1 mark" : it.marks + " marks"}</h3><p>${math(it.question)}</p>${opts}<div class="ans">${ans}</div><div class="prov">${prov}</div></div>`;
}
async function one(slot, rand, st) {
  if (slot.kind === "num") return numeric(slot.unit, rand);
  const src = $("src").value, bk = () => { const b = pack.bankItem(slot.unit, slot.kind, slot.marks, rand); if (b) st.bank++; return b; };
  if (src === "bank") return bk();
  // circuit breaker: if the first 6 neural attempts of this run were all rejected by the strict gate, stop spending CPU on the neural tier (hybrid only); the verified bank serves the rest
  if (src === "hybrid" && st.attempts >= 6 && st.ok === 0) { st.breaker = true; return bk(); }
  for (let tries = 0; tries < (src === "hybrid" ? 3 : 5); tries++) {
    const pool = slot.unit.facts, fact = tries === 0 && slot.fact ? slot.fact : pool[Math.floor(rand() * pool.length)]; st.attempts++;
    const it = await pack.makeItem(slot.unit, slot.kind, slot.marks, fact, { K: 3, rand }); if (it && !it.rejected) { st.ok++; st.score += it.score; return it; } st.rej++;
  } return src === "hybrid" ? bk() : null;
}
async function run() {
  if (busy || !pack) return; busy = true; $("go").disabled = true; $("out").innerHTML = ""; pack.used.clear(); const t0 = performance.now(), st = { attempts: 0, ok: 0, rej: 0, score: 0, bank: 0 }; let slots = [];
  if (mode === "one") { const n = +$("count").value, rand = rng32(+$("seed").value), t = $("type").value, uid = $("unit").value, us = pack.graph.units;
    for (let i = 0; i < n; i++) { const u = uid === "*" ? us[Math.floor(rand() * us.length)] : pack.units[uid], f = u.facts[Math.floor(rand() * u.facts.length)];
      slots.push(t === "num" ? { kind: "num", unit: u } : t === "mcq" ? { kind: "mcq", marks: 1, unit: u, fact: f } : { kind: "short", marks: +t.slice(5), unit: u, fact: f }); }
  } else { const sp = [{ kind: "mcq", marks: 1, n: +$("p-mcq").value }, { kind: "short", marks: 2, n: +$("p-s2").value }, { kind: "short", marks: 3, n: +$("p-s3").value }, { kind: "num", marks: 1, n: +$("p-num").value }];
    slots = planPaper(pack.graph, sp, +$("p-seed").value); }
  const rand = rng32(mode === "one" ? +$("seed").value + 99 : +$("p-seed").value + 99); let html = "", n = 0, last = "", cov = new Set();
  for (const s of slots) { setStatus(`Generating ${++n} of ${slots.length} ...`); const it = await one(s, rand, st); await new Promise((r) => setTimeout(r));
    if (mode === "paper" && s.kind !== last) { html += `<div class="sec">${s.kind === "mcq" ? "Group A: objective (1 mark each)" : s.kind === "num" ? "Numericals (computed)" : s.marks + "-mark questions"}</div>`; last = s.kind; }
    if (it) { html += card(it, n); cov.add(it.unit); } else html += `<div class="q"><h3>Q${n}</h3><p class="muted">No item passed the grounding gate for this slot (never shown unverified).</p></div>`;
    $("out").innerHTML = html; }
  setStatus("Done in " + ((performance.now() - t0) / 1000).toFixed(1) + " s"); $("stats").hidden = false;
  $("statsbody").innerHTML = `${st.breaker ? "Neural tier paused after 6 gate rejections (verified bank used for the remaining slots). " : ""}Neural attempts ${st.attempts}: accepted ${st.ok}, rejected ${st.rej}; verified-bank items ${st.bank}. Mean grounding of accepted ${(st.score / Math.max(1, st.ok)).toFixed(2)}. Units covered ${cov.size} of ${pack.graph.units.length}. Pack ${pack.meta.pack_id} stayed fully on-device.`;
  busy = false; $("go").disabled = false;
}
document.querySelectorAll(".tabs button").forEach((b) => (b.onclick = () => { mode = b.dataset.mode; document.querySelectorAll(".tabs button").forEach((x) => x.setAttribute("aria-selected", x === b)); $("one").hidden = mode !== "one"; $("paper").hidden = mode !== "paper"; }));
$("go").onclick = run; $("reveal").onclick = () => $("out").classList.toggle("show");
// export: plain text (question paper, then answer key) and print stylesheet; the DOM text already holds the rendered items
function paperText() {
  const withAns = $("out").classList.contains("show"), lines = [];
  document.querySelectorAll("#out .q, #out .sec").forEach((el) => {
    if (el.classList.contains("sec")) { lines.push("", el.textContent.toUpperCase()); return; }
    lines.push("", el.querySelector("h3").textContent, el.querySelector("p").textContent);
    el.querySelectorAll(".opt").forEach((o) => lines.push("  " + o.querySelector("b").textContent + " " + o.querySelector("span").textContent));
    if (withAns) { const a = el.querySelector(".ans"); if (a) lines.push("  " + a.textContent); }
  }); return lines.join("\n").trim();
}
$("copy").onclick = async () => { const t = paperText(); if (!t) return setStatus("Nothing to copy yet"); try { await navigator.clipboard.writeText(t); setStatus("Copied " + t.split("\n").length + " lines" + ($("out").classList.contains("show") ? " with answers" : " (answers hidden)")); } catch { setStatus("Clipboard blocked by the browser"); } };
$("print").onclick = () => { if (!$("out").children.length) return setStatus("Generate a paper first"); window.print(); };
loadRegistry().then((r) => { reg = r; renderChips(); const q = new URLSearchParams(location.search).get("pack"); if (q) selectPack(q); }).catch((e) => ($("packinfo").textContent = "No pack registry yet: " + e.message));
