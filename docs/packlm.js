// PaperLM pack engine (JS twin of packs/tools/fsm.py): lazy per-pack ONNX loader + FSM grammar-constrained decoding + grounding verifier + paper planner.
const PRE = / ?\\[A-Za-z]+| ?[A-Za-z\u0900-\u097F]+| ?[0-9]| ?[^\sA-Za-z0-9\u0900-\u097F]|\s+/gu, EXTRA = "°±×÷²³µΩ→≈≤≥−·λμπσΔ";
const SPEC = { mcq: [["ans", "<|q|>", 1, 160], ["q", "<|d|>", 15, 360], ["d1", "<|d|>", 1, 160], ["d2", "<|d|>", 1, 160], ["d3", "<|why|>", 1, 160], ["why", "<|end|>", 15, 300]],
  short: [["ans", "<|q|>", 20, 650], ["q", "<|end|>", 15, 300]] };
const STOP = new Set("the of and a an to in is are was were be by for with on as at from that this which it its or their these those can has have into than then also not one two more most each other such when where what who how why".split(" "));
export const cw = (s) => (s.toLowerCase().match(/[a-z][a-z0-9]{2,}/g) || []).filter((w) => !STOP.has(w));
function byteMaps() { const bs = []; for (let i = 33; i < 127; i++) bs.push(i); for (let i = 161; i < 173; i++) bs.push(i); for (let i = 174; i < 256; i++) bs.push(i);
  const cs = bs.slice(); let n = 0; for (let b = 0; b < 256; b++) if (!bs.includes(b)) { bs.push(b); cs.push(256 + n); n++; }
  const enc = new Array(256), dec = new Map(); bs.forEach((b, i) => { enc[b] = String.fromCharCode(cs[i]); dec.set(String.fromCharCode(cs[i]), b); }); return { enc, dec }; }
export class Tok {
  constructor(j) {
    this.vocab = j.model.vocab; this.rank = new Map(); j.model.merges.forEach((m, i) => this.rank.set(typeof m === "string" ? m : m[0] + " " + m[1], i));
    this.special = new Map(j.added_tokens.map((t) => [t.content, t.id])); const { enc, dec } = byteMaps(); this.enc = enc; this.dec = dec; this.V = Math.max(...Object.values(this.vocab)) + 1; this.cache = new Map();
    this.strs = new Array(this.V).fill(null); this.isSp = new Uint8Array(this.V);
    for (const [t, id] of Object.entries(this.vocab)) {
      if (this.special.has(t)) { this.isSp[id] = 1; continue; }
      try { const s = new TextDecoder("utf-8", { fatal: true }).decode(Uint8Array.from([...t].map((c) => this.dec.get(c)))); this.strs[id] = [...s].every((c) => (c >= " " && c < "\x7f") || EXTRA.includes(c)) ? s : null; } catch { this.strs[id] = null; }
    }
  }
  bpe(w) { if (this.cache.has(w)) return this.cache.get(w); let p = [...w];
    while (p.length > 1) { let best = -1, bi = -1; for (let i = 0; i < p.length - 1; i++) { const r = this.rank.get(p[i] + " " + p[i + 1]); if (r !== undefined && (best < 0 || r < best)) { best = r; bi = i; } } if (bi < 0) break; p.splice(bi, 2, p[bi] + p[bi + 1]); }
    const ids = p.map((x) => this.vocab[x]); this.cache.set(w, ids); return ids; }
  encode(text) { const out = []; for (const s of text.normalize("NFC").split(/(<\|[A-Za-z0-9_=.\-]+\|>)/)) { if (!s) continue; if (this.special.has(s)) { out.push(this.special.get(s)); continue; }
      for (const m of s.matchAll(PRE)) out.push(...this.bpe([...new TextEncoder().encode(m[0])].map((b) => this.enc[b]).join(""))); } return out; }
}
class FSM {  // grammar state: only the legal next tag is ever unmasked; no empty segments; balanced {} and $ before a tag may close
  constructor(T, kind) { this.T = T; this.spec = SPEC[kind]; this.k = 0; this.text = ""; this.d = 0; this.dol = 0; this.done = false; this.ids = []; this.segs = []; }
  mask() {
    const T = this.T, [, closer, lo, hi] = this.spec[this.k], n = this.text.length, m = new Uint8Array(T.V), c = T.special.get(closer), bal = this.d === 0 && this.dol % 2 === 0;
    if (n >= hi && bal || n >= hi + 80) { m[c] = 1; return m; }
    for (let i = 0; i < T.V; i++) { if (!T.ok[i]) continue; if (this.d + T.op[i] - T.cl[i] < 0) continue; if (n === 0 && (T.strs[i].startsWith(" ") || !T.strs[i].trim())) continue; m[i] = 1; }
    if (n >= lo && bal) m[c] = 1; return m;
  }
  feed(i) { const T = this.T; this.ids.push(i);
    if (T.isSp[i]) { this.segs.push(this.text.trim()); this.k++; this.text = ""; this.d = 0; this.dol = 0; if (this.k >= this.spec.length) this.done = true; return; }
    const s = T.strs[i]; this.text += s; this.d += T.op[i] - T.cl[i]; this.dol += T.dl[i]; }
}
export function grounding(segs, kind, anchor, unitTerms = []) {
  const A = new Set(cw(anchor)), UT = new Set(unitTerms), f = {}, frac = (ws, S2) => ws.filter((w) => S2.has(w)).length / Math.max(1, ws.length);
  if (kind === "mcq") { if (segs.length < 6) return [0, { bad: "shape" }]; const [ans, q, d1, d2, d3, why] = segs, ds = [d1, d2, d3], al = anchor.toLowerCase();
    f.ans_ground = frac(cw(ans).length ? cw(ans) : ["_"], A); f.q_ground = cw(q).filter((w) => A.has(w) || UT.has(w)).length / Math.max(1, cw(q).length);
    f.distinct = new Set([...ds, ans].map((x) => x.toLowerCase())).size === 4 && ds.every((x) => !al.includes(x.toLowerCase()) || x.length < 4) ? 1 : 0;
    f.why_ground = frac(cw(why), A); f.no_copy_q = al.includes(q.toLowerCase()) ? 0 : 1; f.homog = ds.every((x) => { const r = (x.length + 3) / (ans.length + 3); return r >= 0.3 && r <= 3.5; }) ? 1 : 0;
    return [0.35 * f.ans_ground + 0.2 * f.q_ground + 0.2 * f.distinct + 0.1 * f.why_ground + 0.05 * f.no_copy_q + 0.1 * f.homog, f];
  } if (segs.length < 2) return [0, { bad: "shape" }]; const [ans, q] = segs; f.ans_ground = frac(cw(ans).length ? cw(ans) : ["_"], A);
  f.q_ground = cw(q).filter((w) => A.has(w) || UT.has(w)).length / Math.max(1, cw(q).length); return [0.6 * f.ans_ground + 0.4 * f.q_ground, f];
}
export const gatePass = (sc, f, kind) => sc >= 0.85 && (kind === "short" || (f.distinct && f.homog && f.ans_ground >= 0.8));
function rng32(a) { return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
export async function loadRegistry(base = "packs/") { return (await fetch(base + "pack_registry.json")).json(); }

const OPEN = /^(what|which|why|how|when|where|who|name|define|state|explain|describe|write|differentiate|distinguish|give|calculate|find|list|mention|compare|justify|derive|prove|identify|discuss|illustrate|draw|show|an?|the|if|in|on|at|for|from|during|define)\b/i;
const rep3 = (t) => { const w = t.toLowerCase().split(/\s+/); const seen = new Set(); for (let i = 0; i + 2 < w.length; i++) { const g = w.slice(i, i + 3).join(" "); if (seen.has(g)) return true; seen.add(g); } return false; };
const distinct = (t) => { const w = t.toLowerCase().split(/\s+/).filter(Boolean); return w.length ? new Set(w).size / w.length : 0; };
/** Strict gate v3 (on top of the lexical grounding gate): well-formed question, no repetition, no answer leak, no clause fragments, fluent under the model itself. */
const NUMS = (t) => t.match(/\d+(?:\.\d+)?/g) || [], PLAIN = (t) => t.replace(/\$[^$]*\$/g, " ").replace(/\\[A-Za-z]+/g, " ");
const stem = (w) => w.replace(/(ing|ed|es|s|ly)$/, "");
/** v4 lexicon + numeric-provenance gate: every number must occur in the anchor (single digits allowed outside the answer), every word of 4+ letters must be a word the pack has seen
 *  in its own syllabus/bank (or a stem of one), and no digit run like "00000". Kills fluent-looking hallucinations such as "observed00000 ... 900/1". */
export function lexOK(segs, anchor, lex) {
  const an = new Set(NUMS(anchor));
  for (let k = 0; k < segs.length; k++) { const t = segs[k]; if (/(\d)\1{3,}/.test(t)) return false;
    for (const n of NUMS(t)) if (!an.has(n) && (k === 0 || n.length > 1)) return false;
    if (lex) for (const w of PLAIN(t).toLowerCase().match(/[a-z]{4,}/g) || []) if (!lex.has(w) && !lex.has(stem(w)) && !lex.has(w + "e")) return false; }
  return true;
}
export function strictOK(kind, segs, anchor, lp, lpMin = -1.6, lex = null) {
  const [ans, q] = segs, A = new Set(cw(anchor)), qc = cw(q);
  if (!OPEN.test(q.trim()) || qc.length < 3 || qc.filter((w) => A.has(w)).length < 2) return false;
  if (kind === "mcq") { if (q.length < 20 || q.toLowerCase().includes(ans.toLowerCase()) && ans.length > 3) return false; }
  for (const t of segs) { if (rep3(t) || distinct(t) < 0.55 || /(\$\s*\$)|\s{2,}|([a-z])\2{3,}/.test(t)) return false; if (t.length > 25 && !/[a-z]{3}/i.test(t)) return false; }
  if (kind === "short" && !/[.)$]\s*$|\w$/.test(ans)) return false;
  if (!lexOK(segs, anchor, lex)) return false;
  return lp >= lpMin;
}
function pickBank(bank, unit, kind, marks, rand, used) {
  const pool = bank.filter((b) => b.unit === unit.name && b.type === kind && !used.has(b.question) && (kind === "mcq" || Math.abs(b.marks - marks) <= 1));
  const alt = pool.length ? pool : bank.filter((b) => b.unit === unit.name && b.type === kind && !used.has(b.question)); if (!alt.length) return null;
  const b = alt[Math.floor(rand() * alt.length)]; used.add(b.question);
  if (kind === "mcq") { const opts = [b.answer, ...b.distractors].map((t, i) => ({ t, ok: i === 0 })); for (let i = 3; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [opts[i], opts[j]] = [opts[j], opts[i]]; }
    return { kind, marks: 1, unit: unit.name, question: b.question, options: opts.map((x) => x.t), key: "abcd"[opts.findIndex((x) => x.ok)], why: b.why, anchor: b.anchor, score: 1, flags: { bank: 1 }, src: b.src, scores: b.scores }; }
  return { kind, marks: b.marks, unit: unit.name, question: b.question, answer: b.answer, anchor: b.anchor, score: 1, flags: { bank: 1 }, src: b.src, scores: b.scores };
}
export class Pack {
  static async load(ort, id, base = "packs/", onProgress = () => {}) {
    const dir = `${base}${id}/`, meta = await (await fetch(dir + "pack.json")).json(); onProgress(0.05, "tokenizer");
    const tokJ = await (await fetch(dir + "tokenizer.json")).json(), graph = await (await fetch(dir + "syllabus_graph.json")).json(); const p = Pack.fromParts(ort, meta, tokJ, graph); try { p.bank = await (await fetch(dir + "bank.json")).json(); } catch { p.bank = []; }
    let buf; const cache = "caches" in self ? await caches.open("paperlm-packs-v2") : null, url = dir + "model.onnx", hit = cache && await cache.match(url);
    if (hit) buf = await hit.arrayBuffer(); else { const r = await fetch(url), tot = +r.headers.get("content-length") || meta.onnx_mb * 1e6, rd = r.body.getReader(), parts = []; let got = 0;
      for (;;) { const { done, value } = await rd.read(); if (done) break; parts.push(value); got += value.length; onProgress(0.1 + 0.8 * got / tot, "model"); } buf = await new Blob(parts).arrayBuffer(); if (cache) await cache.put(url, new Response(buf.slice(0))); }
    onProgress(0.92, "session"); p.session = await ort.InferenceSession.create(new Uint8Array(buf), { executionProviders: ["wasm"] }); onProgress(1, "ready"); return p;
  }
  static fromParts(ort, meta, tokJ, graph) {
    const p = new Pack(); p.meta = meta; p.graph = graph; p.bank = []; p.used = new Set(); p.ort = ort; p.tok = new Tok(tokJ); p.units = Object.fromEntries(graph.units.map((u) => [u.id, u]));
    const T = p.tok; T.ok = new Uint8Array(T.V); T.op = new Int32Array(T.V); T.cl = new Int32Array(T.V); T.dl = new Int32Array(T.V);
    T.strs.forEach((s, i) => { if (s !== null) { T.ok[i] = 1; for (const ch of s) { if (ch === "{") T.op[i]++; else if (ch === "}") T.cl[i]++; else if (ch === "$") T.dl[i]++; } } }); return p;
  }
  async run(ids, st) { const o = this.ort, M = this.meta, P = st ? st.P : 0, z = new Float32Array(0);
    const r = await this.session.run({ ids: new o.Tensor("int64", BigInt64Array.from(ids.map(BigInt)), [1, ids.length]), past_k: new o.Tensor("float32", st ? st.k : z, [M.layers, 1, M.heads, P, M.head_dim]), past_v: new o.Tensor("float32", st ? st.v : z, [M.layers, 1, M.heads, P, M.head_dim]) });
    return { lg: r.logits.data.slice(r.logits.data.length - this.tok.V), k: r.present_k.data, v: r.present_v.data, P: P + ids.length }; }
  prompt(unit, kind, marks, anchor) { return `<|bos|><|pack=${this.meta.pack_id}|><|type=${kind}|><|marks=${marks}|><|unit|>${unit.name}<|book|>${anchor}<|ans|>`; }
  async sample(unit, kind, marks, anchor, { K = 3, temp = 0.75, topP = 0.92, beta = 1.0, rand = Math.random } = {}) {
    const T = this.tok, pre = await this.run(this.tok.encode(this.prompt(unit, kind, marks, anchor)), null), bias = new Float32Array(T.V); for (const i of this.tok.encode(anchor)) bias[i] = beta; const out = [];
    for (let s = 0; s < K; s++) { const f = new FSM(T, kind); let st = pre, lg = pre.lg, lp = 0;
      for (let step = 0; step < 420 && !f.done; step++) { const m = f.mask(), l = new Float32Array(T.V), seen = f.ids; let mx = -1e30;
        for (let i = 0; i < T.V; i++) { if (!m[i]) { l[i] = -1e30; continue; } l[i] = lg[i] + bias[i]; if (l[i] > mx) mx = l[i]; }
        if (seen.length > 6) { const n = seen.length; for (let a = 0; a + 4 < n; a++) if (seen[a] === seen[n - 4] && seen[a + 1] === seen[n - 3] && seen[a + 2] === seen[n - 2] && seen[a + 3] === seen[n - 1]) l[seen[a + 4]] = -1e30; }
        const idx = []; let Z = 0; for (let i = 0; i < T.V; i++) if (l[i] > -1e29) { l[i] = Math.exp((l[i] - mx) / temp); Z += l[i]; idx.push(i); }
        idx.sort((a, b) => l[b] - l[a]); let cum = 0, cut = idx.length; for (let j = 0; j < idx.length; j++) { cum += l[idx[j]] / Z; if (cum >= topP) { cut = j + 1; break; } }
        let tz = 0; for (let j = 0; j < cut; j++) tz += l[idx[j]]; let r = rand() * tz, pick = idx[0]; for (let j = 0; j < cut; j++) { r -= l[idx[j]]; if (r <= 0) { pick = idx[j]; break; } }
        let mm = -1e30, ls = 0; for (let i = 0; i < T.V; i++) if (lg[i] > mm) mm = lg[i]; for (let i = 0; i < T.V; i++) ls += Math.exp(lg[i] - mm); lp += lg[pick] - mm - Math.log(ls);
        f.feed(pick); if (!f.done) { st = await this.run([pick], st); lg = st.lg; } }
      out.push({ segs: f.segs, lp: lp / Math.max(1, f.ids.length), done: f.done }); }
    return out;
  }
  /** answer-first generation + FSM + best-of-K entailment (grounding) rerank + deterministic key placement -> item or null */
  lexicon() { if (this._lex && this._lexN === this.bank.length) return this._lex; const L = new Set(), add = (t) => (PLAIN(t || "").toLowerCase().match(/[a-z]{4,}/g) || []).forEach((w) => { L.add(w); L.add(stem(w)); });
    for (const u of this.graph.units) { add(u.name); (u.terms || []).forEach(add); for (const f of u.facts) add(f.text); } for (const b of this.bank) { add(b.question); add(b.answer); add(b.why); (b.distractors || []).forEach(add); add(b.anchor); } this._lex = L; this._lexN = this.bank.length; return L; }
  bankItem(unit, kind, marks, rand = Math.random) { return pickBank(this.bank, unit, kind, marks, rand, this.used); }
  async makeItem(unit, kind, marks, fact, opt = {}) {
    const ut = unit.terms || [], outs = await this.sample(unit, kind, marks, fact.text, opt), rand = opt.rand || Math.random;
    const scored = outs.filter((o) => o.done).map((o) => { const [sc, f] = grounding(o.segs, kind, fact.text, ut); return { o, sc, f, rank: sc + 0.02 * o.lp }; }).sort((a, b) => b.rank - a.rank); if (!scored.length) return null;
    const { o, sc, f } = scored[0], pass = gatePass(sc, f, kind); if (!pass || (opt.strict !== false && !strictOK(kind, o.segs, fact.text, o.lp, opt.lpMin, this.lexicon()))) return { rejected: true, score: sc, flags: f, segs: o.segs };
    if (kind === "mcq") { const [ans, q, d1, d2, d3, why] = o.segs, opts = [ans, d1, d2, d3].map((t, i) => ({ t, ok: i === 0 })); for (let i = 3; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [opts[i], opts[j]] = [opts[j], opts[i]]; }
      return { kind, marks: 1, unit: unit.name, question: q, options: opts.map((x) => x.t), key: "abcd"[opts.findIndex((x) => x.ok)], why, anchor: fact.text, score: sc, flags: f, fid: fact.id }; }
    return { kind, marks, unit: unit.name, question: o.segs[1], answer: o.segs[0], anchor: fact.text, score: sc, flags: f, fid: fact.id };
  }
}
/** Paper-level blueprint planner + anti-duplication coverage tracker: units get slots proportional to their syllabus share (largest remainder), every slot gets a not-yet-used fact. */
export function planPaper(graph, spec, seed = 1) {
  const rand = rng32(seed), us = graph.units, total = spec.reduce((a, s) => a + s.n, 0), plan = [], used = new Set();
  const quota = us.map((u) => ({ u, q: u.share * total })); let base = quota.map((x) => Math.floor(x.q)), left = total - base.reduce((a, b) => a + b, 0);
  quota.map((x, i) => [x.q - base[i], i]).sort((a, b) => b[0] - a[0]).slice(0, left).forEach(([, i]) => base[i]++);
  const slots = []; us.forEach((u, i) => { for (let k = 0; k < base[i]; k++) slots.push(u); }); for (let i = slots.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [slots[i], slots[j]] = [slots[j], slots[i]]; }
  let si = 0; for (const s of spec) for (let n = 0; n < s.n; n++) { const u = slots[si++ % slots.length], pool = u.facts.filter((f) => !used.has(f.id)); const f = pool[Math.floor(rand() * pool.length)] || u.facts[Math.floor(rand() * u.facts.length)]; used.add(f.id); plan.push({ unit: u, fact: f, kind: s.kind, marks: s.marks }); }
  return plan;
}
export { rng32 };
