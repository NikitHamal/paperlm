import * as ort from "./vendor/ort/ort.wasm.min.mjs";
import { PaperLM, BLUEPRINTS, ItemGenerationError } from "./paperlm.js";
import { Composer } from "./composer.js";

const $ = (id) => document.getElementById(id);
const TYPE_LABEL = { MCQ: "Multiple choice", CONCEPTUAL: "Conceptual", SHORT: "Short answer", NUMERICAL: "Numerical", DERIVATION: "Derivation", LONG: "Long answer", OR: "Long answer with Or" };
const S = { engine: null, cat: null, meta: null, mode: "single", abort: null, busy: false, score: { right: 0, total: 0 } };

// ---------------------------------------------------------------- helpers
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
function math(s) {
  let out = "", i = 0;
  while (i < s.length) {
    if (s[i] === "$") {
      const d = s.startsWith("$$", i) ? "$$" : "$"; const k = s.indexOf(d, i + d.length);
      if (k > 0) { const tex = s.slice(i + d.length, k); try { out += window.katex.renderToString(tex, { throwOnError: true, displayMode: d === "$$", strict: "ignore" }); } catch { out += `<code>${esc(tex)}</code>`; } i = k + d.length; continue; }
    }
    let j = s.indexOf("$", i + 1); if (j < 0) j = s.length; out += esc(s.slice(i, j)); i = j;
  }
  return out;
}
const h = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html !== undefined) e.innerHTML = html; return e; };
function loadScript(src) { return new Promise((res, rej) => { const s = document.createElement("script"); s.src = src; s.onload = res; s.onerror = rej; document.head.appendChild(s); }); }
const setLoad = (p, msg) => { $("load-bar").style.width = Math.round(p * 100) + "%"; $("load-msg").textContent = msg; };

// ---------------------------------------------------------------- rendering
const TIER = { param: ["Computed and verified", "Every number, unit, key and solution is computed by the symbolic engine from a verified law."], fact: ["Verified fact", "Built from a closed-world fact table: the key is the stored value of an audited row and the three distractors are other rows of the same class, so no distractor can also be correct."], bank: ["Gold exam bank", "A verified past-paper style item from the syllabus bank."], teacher: ["Teacher-verified", "Written by a 32B teacher model from the syllabus unit, then kept only after (1) structural checks, (2) an independent blind re-solve that picked the same key with high confidence, (3) a chain-of-thought re-solve for numeric items, (4) duplicate filtering. Strong, but not a formal proof: spot-check before high-stakes use."], lm: ["Neural draft (experimental)", "Written by the 10M model from a verified concept anchor. It passes the lexical grounding gate but its meaning is NOT verified: review before use."] };
const tierChip = (it) => { const t = (it.provenance && it.provenance.tier) || "lm"; const c = h("span", "chip t", esc(TIER[t][0])); c.title = TIER[t][1]; return c; };
const provNote = (it) => { const p = it.provenance || {}; if (p.tier === "lm") return h("div", "prov", `<b>Concept anchor:</b> ${math(esc(p.anchor))}`); if (p.tier === "param") return h("div", "prov", `<b>Law used:</b> ${math(p.law || "")}`); if (p.tier === "fact") return h("div", "prov", `<b>Topic:</b> ${esc(p.topic || "")} &middot; <b>Source:</b> ${esc(p.src || "")}`); return null; };
function mcqCard(it, { interactive = true, onAnswer } = {}) {
  const card = h("article", "item");
  const head = h("div", "item-h");
  head.append(h("span", "chip", `${it.marks} mark${it.marks > 1 ? "s" : ""}`), h("span", "chip", esc(it.unit)), tierChip(it));
  card.append(head, h("p", "q", `${it.no ? it.no + ". " : ""}${math(it.question)}`));
  const box = h("div", "opts");
  it.options.forEach((o, i) => {
    const b = h("button", "opt" + ("abcd"[i] === it.key ? " key" : ""), `<span class="l">${"abcd"[i].toUpperCase()}</span><span>${math(o)}</span>`); b.type = "button";
    if (interactive) b.addEventListener("click", () => {
      if (card.dataset.done) return; card.dataset.done = "1";
      const right = "abcd"[i] === it.key; b.classList.add(right ? "right" : "wrong"); box.querySelectorAll(".opt").forEach((x, j) => { x.disabled = true; if ("abcd"[j] === it.key) x.classList.add("right"); });
      ex.hidden = false; onAnswer && onAnswer(right);
    });
    box.append(b);
  });
  card.append(box);
  const ex = h("div", "expl", `<h4>Answer ${it.key.toUpperCase()}</h4>${it.explanation ? math(it.explanation) : "No explanation generated."}`);
  if (interactive) ex.hidden = true; card.append(ex);
  { const pn = provNote(it); if (pn) card.append(pn); }
  return card;
}
function partsList(ps) {
  const ul = h("ul", "parts");
  ps.forEach((p) => ul.append(h("li", "", `<span class="pl">(${p.label})</span><span>${math(p.text)}</span>${p.marks ? `<span class="pm">${p.marks}</span>` : "<span></span>"}`)));
  return ul;
}
function writtenCard(it) {
  const card = h("article", "item"); const head = h("div", "item-h");
  head.append(h("span", "chip", `${it.marks} marks`), h("span", "chip", TYPE_LABEL[it.type] || it.type), h("span", "chip", esc(it.unit)), tierChip(it));
  card.append(head, h("p", "q", `${it.no ? it.no + ". " : ""}${math(it.question)}`));
  if (it.parts.length) card.append(partsList(it.parts));
  if (it.or_parts && it.or_parts.length) { card.append(h("div", "or", "OR"), partsList(it.or_parts)); }
  if (it.rubric) card.append(h("div", "expl rub", `<h4>Marking rubric</h4>${math(it.rubric)}`));
  { const pn = provNote(it); if (pn) card.append(pn); }
  return card;
}
const itemCard = (it, o) => (it.kind === "mcq" ? mcqCard(it, o) : writtenCard(it));

function updateStats() {
  const s = S.engine.stats; $("s-ms").textContent = s.tokens ? (s.ms / s.tokens).toFixed(1) : "-"; $("s-tok").textContent = s.tokens; $("s-att").textContent = s.attempts; $("s-items").textContent = s.items;
  const rej = Object.entries(s.rejects).sort((a, b) => b[1] - a[1]); $("s-rej").textContent = rej.reduce((a, [, n]) => a + n, 0);
  $("s-why").textContent = rej.length ? "Rejected: " + rej.slice(0, 5).map(([k, n]) => `${k} (${n})`).join(", ") : "No rejections yet.";
  if (S.comp) { const t = S.comp.stats; $("s-why").textContent += ` | Tiers: computed ${t.param}, fact ${t.fact || 0}, bank ${t.bank}, neural ${t.lm} (gate ${t.lm_gate_pass}/${t.lm_tries})`; }
}

// ---------------------------------------------------------------- controls
function cur() { const [b, l] = $("f-preset").value.split("|"); return { board: b, level: l, entry: S.cat[`${b}|${l}`], subject: $("f-subject").value }; }
function fillSelect(sel, opts, keep) { const v = keep && sel.value; sel.innerHTML = ""; opts.forEach(([val, lab]) => { const o = document.createElement("option"); o.value = val; o.textContent = lab; sel.append(o); }); if (v && opts.some(([x]) => x === v)) sel.value = v; }
const prettySubject = (s) => s.replace(/-/g, " ").replace(/^./, (c) => c.toUpperCase());
function refreshSubjects() { const { entry } = cur(); fillSelect($("f-subject"), Object.keys(entry.subjects).map((s) => [s, prettySubject(s)]), true); refreshUnits(); }
function refreshUnits() {
  const { entry, subject } = cur(); const d = entry.subjects[subject]; fillSelect($("f-unit"), [["", "Any unit"], ...d.units.map((u) => [u, u])], true);
  let types = Object.keys(d.types).filter((t) => t !== "SHORT" || true); if (S.mode === "or") types = ["OR"]; if (S.mode === "mcq") types = ["MCQ"];
  if (!types.length) types = ["MCQ"]; fillSelect($("f-type"), types.map((t) => [t, TYPE_LABEL[t] || t]), true); refreshMarks();
}
function refreshMarks() {
  const { entry, subject } = cur(); const d = entry.subjects[subject], t = $("f-type").value; let m = (d.types[t] || []).slice();
  const def = { MCQ: [1], OR: [8, 10], CONCEPTUAL: [2, 4, 5], SHORT: [2, 5], NUMERICAL: [4, 5], DERIVATION: [5, 8], LONG: [5, 8] }[t] || [1]; if (S.mode === "or") m = [...new Set([...m, ...def])].sort((a, b) => a - b);
  if (!m.length) m = def; fillSelect($("f-marks"), m.map((x) => [String(x), `${x} mark${x > 1 ? "s" : ""}`]), true);
}
function setMode(m) {
  S.mode = m; const tabs = [...document.querySelectorAll("#modes button")]; tabs.forEach((t) => t.setAttribute("aria-selected", String(t.dataset.mode === m)));
  document.querySelector(".seg-ind").style.transform = `translateX(${tabs.findIndex((t) => t.dataset.mode === m) * 100}%)`;
  const paper = m === "paper"; $("w-type").hidden = paper; $("w-marks").hidden = paper; $("w-unit").hidden = paper; $("w-count").hidden = !(paper && ["IOE", "CEE", "BCA", "BSN"].includes(cur().level)) ;
  $("keytoggle").hidden = !paper; $("print").hidden = !paper; $("go").textContent = { single: "Generate question", or: "Generate Or pair", mcq: "Start MCQ practice", paper: "Generate model paper" }[m];
  refreshUnits(); $("out").innerHTML = ""; $("out").className = "out"; if (paper) paperInfo();
}
function paperInfo() {
  const { level, entry, subject } = cur(); const bp = bpFor(level); const total = bp.reduce((a, [, , m, c]) => a + m * c, 0);
  $("out").innerHTML = `<div class="empty">${entry.label}, ${prettySubject(subject)}: ${bp.map(([g, t, m, c]) => `Group ${g} ${c} x ${m}`).join(", ")}. Full marks ${total}.</div>`;
  $("w-count").hidden = !["IOE", "CEE", "BCA", "BSN"].includes(level);
}
function bpFor(level) {
  const bp = BLUEPRINTS[level].map((x) => x.slice()); if (["IOE", "CEE", "BCA", "BSN"].includes(level)) bp[0][3] = Math.max(1, Math.min(200, +$("f-count").value || 10)); return bp;
}
function busy(b) { S.busy = b; $("go").disabled = b || !S.engine; $("stop").hidden = !b; $("go").hidden = b; }
function opts() { return { temperature: +$("f-temp").value, lm: +$("f-cand").value, rubric: $("f-rubric").checked }; }
function newEngine() { S.engine.rand = (function (a) { return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; })(+$("f-seed").value || 1); }
function pickUnit(c) { const u = $("f-unit").value; if (u) return u; const us = c.entry.subjects[c.subject].units; return us[Math.floor(S.engine.rand() * us.length)]; }
const showErr = (msg) => { const e = h("div", "err", esc(msg)); $("out").prepend(e); };

async function genOne(c, extra = {}) {
  const o = opts(); const type = $("f-type").value, marks = +$("f-marks").value;
  return S.comp.item({ board: c.entry.board, level: c.entry.level, subject: c.subject, unit: pickUnit(c), marks, type, rubric: o.rubric, temperature: o.temperature, lmBudget: o.lm, signal: S.abort.signal, ...extra });
}
async function composedPaper(c, bp, o, onItem) {
  const b = c.entry.board, l = c.entry.level, units = S.engine.unitsFor(b, l, c.subject).slice(); const R = S.engine.rand;
  for (let i = units.length - 1; i > 0; i--) { const j = Math.floor(R() * (i + 1)); [units[i], units[j]] = [units[j], units[i]]; }
  let k = 0; const seen = new Set();
  for (const [g, typ, marks, count] of bp) {
    let n = 0, fails = 0;
    while (n < count) {
      if (S.abort.signal.aborted) throw new Error("aborted"); const unit = units[k++ % units.length]; const t = typ === "SHORT" ? ["CONCEPTUAL", "NUMERICAL", "DERIVATION", "SHORT"][n % 4] : typ; let it;
      try { it = await S.comp.item({ board: b, level: l, subject: c.subject, unit, marks, type: t, rubric: o.rubric, temperature: o.temperature, lmBudget: o.lm, signal: S.abort.signal }); }
      catch (e) { if (e.message === "aborted") throw e; if (++fails > 8 * count + 12) throw e; continue; }
      const key = (it.question + (it.options || []).join("")).replace(/\s+/g, "").slice(0, 90); if (seen.has(key)) { if (++fails > 8 * count + 12) throw new Error("not enough distinct verified items for this subject"); continue; } seen.add(key); it.no = ++n; onItem(g, it);
    }
  }
}

async function run() {
  if (S.busy || !S.engine) return; S.abort = new AbortController(); busy(true); newEngine(); const c = cur(); const out = $("out"); const o = opts();
  try {
    if (S.mode === "single" || S.mode === "or") { out.innerHTML = ""; const it = await genOne(c); out.append(itemCard(it, { interactive: it.kind === "mcq" })); }
    else if (S.mode === "mcq") { out.innerHTML = ""; S.score = { right: 0, total: 0 }; await mcqLoop(c); }
    else await paper(c, o);
  } catch (e) { if (e.message !== "aborted") showErr(e instanceof ItemGenerationError ? "The model could not produce a verified item for this combination. Try another unit or type. " + e.message : "Error: " + e.message); }
  busy(false); updateStats();
}
async function mcqLoop(c) {
  const out = $("out"); const bar = h("div", "score", ""); const next = h("button", "btn filled", "Next question"); next.type = "button"; const tally = h("span", "chip", "Score 0 / 0");
  bar.append(tally, next); out.append(bar); let slot = h("div"); out.append(slot);
  const make = async () => {
    next.disabled = true; slot.innerHTML = '<div class="empty">Generating</div>'; busy(true); S.abort = new AbortController();
    try { const it = await genOne(c, { type: "MCQ", marks: 1 }); it.no = S.score.total + 1; slot.innerHTML = ""; slot.append(mcqCard(it, { onAnswer: (r) => { S.score.total++; if (r) S.score.right++; tally.textContent = `Score ${S.score.right} / ${S.score.total}`; next.disabled = false; next.textContent = "Next question"; } })); }
    catch (e) { slot.innerHTML = ""; if (e.message !== "aborted") showErr(e.message); next.disabled = false; }
    busy(false); $("go").hidden = true; updateStats();
  };
  next.addEventListener("click", make); await make();
}
async function paper(c, o) {
  const out = $("out"); out.innerHTML = ""; out.classList.add("hidden-ans"); $("keytoggle").textContent = "Show answers";
  const bp = bpFor(c.level); const total = bp.reduce((a, [, , m, n]) => a + m * n, 0);
  const head = h("div", "paper-h", `<h2>${esc(c.entry.label)}: ${esc(prettySubject(c.subject))} model paper</h2><p>Full marks ${total}. Composed in your browser by PaperLM-Tiny ${esc(S.meta.version)}: every item is computed by the symbolic engine or taken from the verified gold bank (neural drafts only if you enable them).</p>`); out.append(head);
  const secEls = {}; let n = 0; const totalQ = bp.reduce((a, [, , , k]) => a + k, 0); const prog = h("div", "empty", "Generating 0 / " + totalQ); out.append(prog);
  for (const [g, typ, marks, count] of bp) {
    const sh = h("div", "sec-h", `<h2>Group ${g}</h2><span>${count} x ${marks} = ${count * marks} marks, ${esc(TYPE_LABEL[typ] || typ)}</span>`); const body = h("div", "out"); secEls[g] = body; out.insertBefore(sh, prog); out.insertBefore(body, prog);
  }
  const t0 = performance.now(); let lastG = null;
  await composedPaper(c, bp, o, (g, it) => { n++; secEls[g].append(itemCard(it, { interactive: false })); prog.textContent = `Generating ${n} / ${totalQ}, ${((performance.now() - t0) / 1000).toFixed(0)} s`; updateStats(); });
  prog.textContent = `Done: ${totalQ} questions, ${total} marks, ${((performance.now() - t0) / 1000).toFixed(0)} s on this device.`;
}

function renderQuality(meta) {
  const q = meta.benchmark; if (!q || !q.current) return; const el = $("quality"); el.hidden = false; const prev = q.previous || {}, cur = q.current;
  const better = { "raw verifier pass rate": 1, "concept-anchor rate": 1, "distinct stems": 1, "full-engine success rate": 1 };
  const pct = (k, v) => (typeof v === "number" && v <= 1 && !/seconds|attempts/.test(k) ? (v * 100).toFixed(1) + "%" : v);
  const rows = Object.keys(cur).map((k) => `<tr><td>${esc(k)}</td><td>${prev[k] === undefined ? "-" : pct(k, prev[k])}</td><td><b>${pct(k, cur[k])}</b></td></tr>`).join("");
  el.innerHTML = `<h2>Model quality by iteration</h2><p class="note">${esc(meta.notes || "")}</p><div class="tw"><table><thead><tr><th>Metric (raw first sample, verifier off)</th><th>${esc(q.previous_label || "previous")}</th><th>${esc(meta.version)}</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

// ---------------------------------------------------------------- boot
async function fetchModel(url) {
  const r = await fetch(url); const len = +r.headers.get("content-length") || 10434064; const rd = r.body.getReader(); const chunks = []; let got = 0;
  for (;;) { const { done, value } = await rd.read(); if (done) break; chunks.push(value); got += value.length; setLoad(Math.min(0.9, (got / len) * 0.9), `Downloading model ${(got / 1e6).toFixed(1)} of ${(len / 1e6).toFixed(1)} MB`); }
  const buf = new Uint8Array(got); let o = 0; for (const c of chunks) { buf.set(c, o); o += c.length; } return buf;
}
async function boot() {
  $("theme").addEventListener("click", () => { const r = document.documentElement; const dark = (r.dataset.theme || (matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light")) === "dark"; r.dataset.theme = dark ? "light" : "dark"; try { localStorage.setItem("plm-theme", r.dataset.theme); } catch {} });
  $("f-temp").addEventListener("input", () => ($("v-temp").textContent = $("f-temp").value)); $("f-cand").addEventListener("input", () => ($("v-cand").textContent = $("f-cand").value));
  const [cat, meta, syl, tok] = await Promise.all([fetch("model/catalog.json").then((r) => r.json()), fetch("model/meta.json?" + Date.now()).then((r) => r.json()), fetch("model/syllabus.json").then((r) => r.json()), fetch("model/tokenizer.json").then((r) => r.json())]);
  S.cat = cat; S.meta = meta; $("b-ver").textContent = meta.version; $("b-loss").textContent = `val loss ${meta.val_loss.toFixed(2)}, ppl ${meta.perplexity.toFixed(1)}`;
  document.title = `PaperLM ${meta.version} playground`; renderQuality(meta);
  fillSelect($("f-preset"), Object.entries(cat).map(([k, e]) => [k, e.label])); $("f-preset").value = "NEB|C12";
  $("f-preset").addEventListener("change", () => { refreshSubjects(); setMode(S.mode); }); $("f-subject").addEventListener("change", () => { refreshUnits(); if (S.mode === "paper") paperInfo(); }); $("f-type").addEventListener("change", refreshMarks);
  $("f-count").addEventListener("change", () => S.mode === "paper" && paperInfo());
  document.querySelectorAll("#modes button").forEach((b) => b.addEventListener("click", () => setMode(b.dataset.mode)));
  $("go").addEventListener("click", run); $("stop").addEventListener("click", () => S.abort && S.abort.abort()); $("print").addEventListener("click", () => window.print());
  $("keytoggle").addEventListener("click", () => { const o = $("out"); o.classList.toggle("hidden-ans"); $("keytoggle").textContent = o.classList.contains("hidden-ans") ? "Show answers" : "Hide answers"; });
  refreshSubjects(); setMode("single");
  setLoad(0.02, "Loading math renderer"); await loadScript("vendor/katex/katex.min.js");
  let lex = null; try { lex = await fetch("model/lexicon.json?" + meta.version).then((r) => (r.ok ? r.json() : null)); } catch {}
  const bytes = await fetchModel("model/model.onnx?" + meta.version);
  setLoad(0.93, "Starting ONNX Runtime (WASM)"); ort.env.wasm.numThreads = 1; ort.env.wasm.wasmPaths = new URL("vendor/ort/", location.href).href;
  S.engine = await PaperLM.create({ ort, model: bytes, tokenizer: tok, syllabus: syl, seed: 7, lexicon: lex });
  setLoad(0.97, "Loading verified concept bank and formula library"); const [bank, tpl, facts] = await Promise.all([fetch("model/bank.json?" + meta.version).then((r) => r.json()), fetch("model/templates.json?" + meta.version).then((r) => r.json()), fetch("model/facts.json?" + meta.version).then((r) => r.json())]);
  S.comp = new Composer(S.engine, bank, tpl, facts);
  setLoad(1, `Model ready: ${meta.version}, ${(meta.params / 1e6).toFixed(1)}M parameters, ${meta.quant}`); $("load").classList.add("done"); busy(false);
}
boot().catch((e) => { setLoad(0, "Failed to load: " + e.message); console.error(e); });
