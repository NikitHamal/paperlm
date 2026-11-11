// PaperLM-Tiny Web SDK — PaperSetterEngine (grammar/schema-constrained generator) for browsers & Node.
// Mirrors engine/paper_setter.py + data/validator.py rule-for-rule. Needs onnxruntime-web (browser) or onnxruntime-node.
import { KNOWN_CMDS, ALLOWED_EXTRA } from "./known_cmds.js";
import { cleanSymbols, verifyItem } from "./verify.js";
export { verifyItem, cleanSymbols };
const KNOWN = [...KNOWN_CMDS].filter((c) => !["begin", "end", "hline"].includes(c)).sort(), KSET = new Set(KNOWN), EXTRA = new Set([...ALLOWED_EXTRA]);
const TWO = new Set(["frac", "dfrac", "tfrac", "binom"]);
const ONE = new Set(["sqrt", "text", "textbf", "textit", "mathrm", "mathbf", "mathbb", "mathcal", "mathit", "vec", "hat", "bar", "overline", "underline", "dot", "ddot", "tilde", "operatorname", "boxed", "cancel", "ce", "underbrace", "overbrace"]);
export class ItemGenerationError extends Error {}
const charOk = (c) => { const o = c.codePointAt(0); return (o >= 32 && o < 127) || EXTRA.has(c) || (o >= 0x900 && o < 0x980); };

// ---------------------------------------------------------------- tokenizer (byte-level BPE, regex pre-split)
const PRE = / ?\\[A-Za-z]+| ?[A-Za-z\u0900-\u097F]+| ?[0-9]| ?[^\sA-Za-z0-9\u0900-\u097F]|\s+/gu;
function byteMaps() {
  const bs = []; for (let i = 33; i < 127; i++) bs.push(i); for (let i = 161; i < 173; i++) bs.push(i); for (let i = 174; i < 256; i++) bs.push(i);
  const cs = bs.slice(); let n = 0; for (let b = 0; b < 256; b++) if (!bs.includes(b)) { bs.push(b); cs.push(256 + n); n++; }
  const enc = new Array(256), dec = new Map(); bs.forEach((b, i) => { enc[b] = String.fromCharCode(cs[i]); dec.set(String.fromCharCode(cs[i]), b); }); return { enc, dec };
}
export class Tok {
  constructor(j) {
    this.vocab = j.model.vocab; this.rank = new Map(); j.model.merges.forEach((m, i) => this.rank.set(typeof m === "string" ? m : m[0] + " " + m[1], i));
    this.special = new Map(j.added_tokens.map((t) => [t.content, t.id])); const { enc, dec } = byteMaps(); this.enc = enc; this.dec = dec; this.n = Object.keys(this.vocab).length; this.cache = new Map();
    this.strs = new Array(this.n).fill(null); this.isSpecial = new Array(this.n).fill(false);
    for (const [t, id] of Object.entries(this.vocab)) {
      if (this.special.has(t)) { this.isSpecial[id] = true; continue; }
      try { const bytes = Uint8Array.from([...t].map((c) => this.dec.get(c))); const s = new TextDecoder("utf-8", { fatal: true }).decode(bytes); this.strs[id] = [...s].every(charOk) ? s : null; } catch { this.strs[id] = null; }
    }
  }
  bpe(word) {
    if (this.cache.has(word)) return this.cache.get(word);
    let parts = [...word];
    while (parts.length > 1) {
      let best = -1, bi = -1; for (let i = 0; i < parts.length - 1; i++) { const r = this.rank.get(parts[i] + " " + parts[i + 1]); if (r !== undefined && (best < 0 || r < best)) { best = r; bi = i; } }
      if (bi < 0) break; parts.splice(bi, 2, parts[bi] + parts[bi + 1]);
    }
    const ids = parts.map((p) => this.vocab[p]); this.cache.set(word, ids); return ids;
  }
  encode(text) {
    const out = []; const segs = text.normalize("NFC").split(/(<\|[A-Za-z0-9_=.\-]+\|>)/);
    for (const s of segs) {
      if (!s) continue; if (this.special.has(s)) { out.push(this.special.get(s)); continue; }
      for (const m of s.matchAll(PRE)) { const w = [...new TextEncoder().encode(m[0])].map((b) => this.enc[b]).join(""); out.push(...this.bpe(w)); }
    }
    return out;
  }
}

// ---------------------------------------------------------------- incremental LaTeX/text state
class TextSt {
  constructor() { this.mode = ""; this.depth = 0; this.cmd = null; this.bs = false; this.lr = 0; this.mlen = 0; this.last = ""; this.raw = ""; this.exp = 0; this.frames = []; }
  copy() { const c = Object.assign(new TextSt(), this); c.frames = this.frames.slice(); return c; }
  closed() { return this.mode === "" && this.depth === 0 && this.cmd === null && !this.bs && this.exp === 0; }
  feed(s) {
    const a = [...s]; let i = 0;
    while (i < a.length) {
      const ch = a[i];
      if (this.cmd !== null) {
        if (/^[A-Za-z]$/.test(ch)) { this.cmd += ch; if (!KNOWN.some((k) => k.startsWith(this.cmd))) return false; i++; continue; }
        if (!KSET.has(this.cmd)) return false; if (this.cmd === "left") this.lr++; else if (this.cmd === "right") this.lr--; this.exp = TWO.has(this.cmd) ? 2 : ONE.has(this.cmd) ? 1 : 0; this.cmd = null;
      }
      if (this.bs) {
        this.bs = false;
        if (/^[A-Za-z]$/.test(ch)) { this.cmd = ch; if (!KNOWN.some((k) => k.startsWith(ch))) return false; i++; continue; }
        if (this.mode === "" || !"\\{}%&_#,;:! |$".includes(ch)) return false; i++; this.mlen++; continue;
      }
      if (this.exp > 0 && ch !== " " && ch !== "{") return false;
      if (ch === "$") {
        const dbl = a[i + 1] === "$";
        if (this.mode === "") { this.mode = dbl ? "$$" : "$"; this.depth = 0; this.mlen = 0; this.lr = 0; this.last = ""; i += dbl ? 2 : 1; }
        else {
          if (this.depth !== 0 || this.lr !== 0 || this.mlen === 0 || this.last === "^" || this.last === "_") return false;
          if (this.mode === "$$") { if (!dbl) return false; i += 2; } else { if (dbl) return false; i++; }
          this.mode = "";
        }
        this.last = "$"; continue;
      }
      if (this.mode) {
        if (ch === "\\") { this.bs = true; i++; continue; }
        if (ch === "{") { if (this.exp > 0) { this.frames.push([this.exp - 1, this.depth]); this.exp = 0; } this.depth++; } else if (ch === "}") { this.depth--; if (this.depth < 0) return false; const f = this.frames.at(-1); if (f && f[1] === this.depth) this.exp = this.frames.pop()[0]; }
        else if ((ch === "^" || ch === "_") && (this.last === "^" || this.last === "_")) return false;
        if (ch !== " ") { this.mlen++; this.last = ch; } else if (this.last === "") { i++; continue; }
      } else {
        if ("\\{}^".includes(ch)) return false;
        const prev = i > 0 ? a[i - 1] : this.raw.slice(-1); if (ch === " " && prev === " ") return false;
      }
      i++;
    }
    return true;
  }
}

// ---------------------------------------------------------------- final validator (port of data/validator.py check_text / check_mcq / check_written)
export function checkMath(m) {
  const s = m.trim(); if (!s) return "empty math"; let depth = 0, left = 0, right = 0; const envs = [];
  for (let i = 0; i < s.length;) {
    const c = s[i];
    if (c === "\\") {
      const mm = /^\\([A-Za-z]+)/.exec(s.slice(i));
      if (mm) {
        const cmd = mm[1]; if (!KSET.has(cmd)) return "unknown cmd"; let j = i + mm[0].length;
        if (cmd === "left") left++; else if (cmd === "right") right++;
        else if (cmd === "begin" || cmd === "end") { const e = /^\{([A-Za-z*]+)\}/.exec(s.slice(j)); if (!e) return "bad env"; if (cmd === "begin") envs.push(e[1]); else if (envs.pop() !== e[1]) return "env mismatch"; j += e[0].length; }
        else if (TWO.has(cmd)) { j = needGroups(s, j, 2); if (j < 0) return "frac args"; }
        i = j; continue;
      }
      i += 2; continue;
    }
    if (c === "{") depth++; else if (c === "}") { depth--; if (depth < 0) return "brace underflow"; } i++;
  }
  if (depth !== 0 || left !== right || envs.length) return "unbalanced";
  if (/[\^_]\s*$/.test(s) || /\^\{\}|_\{\}/.test(s)) return "dangling script"; return null;
}
function needGroups(s, j, k) {
  for (let t = 0; t < k; t++) {
    while (s[j] === " ") j++; if (j >= s.length) return -1;
    if (s[j] === "{") { let d = 0; for (; j < s.length; j++) { if (s[j] === "\\") { j++; continue; } if (s[j] === "{") d++; else if (s[j] === "}") { d--; if (d === 0) { j++; break; } } } if (d !== 0) return -1; }
    else if (s[j] === "\\") { const m = /^\\[A-Za-z]+/.exec(s.slice(j)); j += m ? m[0].length : 2; } else j++;
  }
  return j;
}
export function checkText(t, allowEmpty = false) {
  if (!t.trim()) return allowEmpty ? null : "empty";
  for (const c of t) if (!charOk(c)) return "bad char";
  if (/<\/?[a-zA-Z][^>]*>|&[a-z]+;|&#\d+;/.test(t)) return "html residue";
  if (/\*\*|__|`|\[\[|\]\]|@mcq|@opts|:::/.test(t)) return "markdown residue";
  const outs = []; const maths = []; let buf = ""; 
  for (let i = 0; i < t.length;) {
    if (t[i] === "$") { const d = t.startsWith("$$", i) ? "$$" : "$"; const k = t.indexOf(d, i + d.length); if (k < 0) return "unbalanced $"; outs.push(buf); buf = ""; maths.push(t.slice(i + d.length, k)); i = k + d.length; } else buf += t[i++];
  }
  outs.push(buf); for (const m of maths) { const e = checkMath(m); if (e) return "math: " + e; }
  if (/[\\{}^]/.test(outs.join(" "))) return "stray tex"; if (/(.{3,}?)\1{4,}/.test(t)) return "repetition"; return null;
}
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9\u0900-\u097F]+/g, "");

// ---------------------------------------------------------------- engine
const CAPS = { q: 420, oa: 120, ob: 120, oc: 120, od: 120, part: 320, why: 320, sol: 700 };
const NEXT_MCQ = { q: "<|oa|>", oa: "<|ob|>", ob: "<|oc|>", oc: "<|od|>", od: "<|ans|>" };
const MINLEN = { q: 12, oa: 1, ob: 1, oc: 1, od: 1, part: 6, why: 8, sol: 12 };
function rng32(a) { return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
// Official blueprints (full marks): NEB 11/12 = 75 (11x1 + 8x5 + 3x8), SEE = 75 (10x1 + 8x2 + 6x4 + 5x5), IOE = 100 (100x1 MCQ), BLE 8 = 48.
export const BLUEPRINTS = {
  C8: [["A", "MCQ", 1, 10], ["B", "SHORT", 2, 6], ["C", "CONCEPTUAL", 4, 4], ["D", "LONG", 5, 2]],
  C10: [["A", "MCQ", 1, 10], ["B", "SHORT", 2, 8], ["C", "CONCEPTUAL", 4, 6], ["D", "LONG", 5, 5]],
  C11: [["A", "MCQ", 1, 11], ["B", "SHORT", 5, 8], ["C", "OR", 8, 3]], C12: [["A", "MCQ", 1, 11], ["B", "SHORT", 5, 8], ["C", "OR", 8, 3]],
  IOE: [["A", "MCQ", 1, 100]], CEE: [["A", "MCQ", 1, 100]], BCA: [["A", "MCQ", 1, 100]], BSN: [["A", "MCQ", 1, 100]], BE: [["A", "OR", 10, 8]],
};
export const MOCK_LENGTH = { IOE: 100, CEE: 100, BCA: 100, BSN: 100 };
export class PaperLM {
  constructor(ort, session, tok, syl, seed = 1) {
    this.ort = ort; this.s = session; this.tok = tok; this.syl = syl || { units: {} }; this.rand = rng32(seed); this.L = 6; this.H = 5; this.D = 64; this.lexicons = new Map(); this.stats = { tokens: 0, ms: 0, rejects: {}, attempts: 0, items: 0 };
    const id = tok.vocab; this.id = id; this.S = Object.fromEntries(["pad", "bos", "end", "unit", "q", "oa", "ob", "oc", "od", "ans", "why", "part", "pm", "or", "sol"].map((k) => [k, tok.special.get(`<|${k}|>`)]));
    this.structIds = new Set(Object.values(this.S)); this.letters = Object.fromEntries([..."abcd"].map((c) => [c, id[c]])); this.digits = Object.fromEntries([..."0123456789"].map((c) => [c, id[c]]));
  }
  static async create({ ort, model, tokenizer, syllabus, seed, lexicon, providers = ["wasm"] }) {
    const session = await ort.InferenceSession.create(model, { executionProviders: providers });
    const p = new PaperLM(ort, session, new Tok(tokenizer), syllabus, seed);
    if (lexicon) for (const [k, v] of Object.entries(lexicon)) p.lexicons.set(k, new Set(v)); return p;
  }
  async step(ids, st) {
    const o = this.ort, P = st ? st.P : 0, z = new Float32Array(0);
    const feeds = { ids: new o.Tensor("int64", BigInt64Array.from(ids.map(BigInt)), [1, ids.length]), past_k: new o.Tensor("float32", st ? st.k : z, [this.L, 1, this.H, P, this.D]), past_v: new o.Tensor("float32", st ? st.v : z, [this.L, 1, this.H, P, this.D]) };
    const t0 = performance.now(); const r = await this.s.run(feeds); this.stats.ms += performance.now() - t0; this.stats.tokens += ids.length === 1 ? 1 : 0; return { logits: r.logits.data.subarray(r.logits.data.length - this.tok.n), st: { k: r.present_k.data, v: r.present_v.data, P: P + ids.length } };
  }
  header(b, l, s, u, m, t) { const sid = this.tok.special.has(`<|subj=${s}|>`) ? `<|subj=${s}|>` : "<|subj=general|>"; return `<|bos|><|board=${b}|><|level=${l}|>${sid}<|unit|>${u}<|marks=${m}|><|type=${t}|>`; }
  newState(typ, marks, wantSol) { return { typ, marks, wantSol, mcq: typ === "MCQ", sec: "q", t: new TextSt(), opts: [], key: "", why: "", q: "", parts: [], alt: [], inAlt: false, pm: "", sol: "", done: false, seen4: new Set(), recent: [] }; }
  curParts(st) { return st.inAlt ? st.alt : st.parts; }
  marksOk(st) { for (const ps of [st.parts, st.alt]) if (ps.length && ps.some((p) => p[2]) && (!ps.every((p) => p[2]) || ps.reduce((a, p) => a + p[2], 0) !== st.marks)) return false; return true; }
  allowedStruct(st) {
    const sec = st.sec; let out = [];
    if (st.mcq) { if (NEXT_MCQ[sec]) out = [NEXT_MCQ[sec]]; else if (sec === "why") out = ["<|end|>"]; }
    else if (sec === "q" || sec === "part") {
      const ps = this.curParts(st); if (sec === "part" && (ps.length === 1 || ps.slice(0, -1).every((p) => p[2]))) out.push("<|pm|>"); out.push("<|part|>");
      if (st.typ === "OR" && !st.inAlt) out.push("<|or|>"); else out.push(st.wantSol ? "<|sol|>" : "<|end|>");
    } else if (sec === "sol") out = ["<|end|>"];
    return out;
  }
  validFn(st) {
    const T = this.tok, sec = st.sec, dig = new Set(Object.values(this.digits));
    if (sec === "ans") return (i) => Object.values(this.letters).includes(i);
    if (sec === "pm") { if (st.pm.length >= 2) return () => false; const inv = Object.fromEntries(Object.entries(this.digits).map(([d, v]) => [v, d])); return (i) => dig.has(i) && !(st.pm === "" && inv[i] === "0") && parseInt(st.pm + inv[i]) <= st.marks; }
    if (sec === "or") return (i) => i === this.S.part;
    const cap = CAPS[sec] || 300, raw = st.t.raw, allowed = new Set();
    if (st.t.closed() && raw.trim().length >= (MINLEN[sec] || 1)) {
      for (const name of this.allowedStruct(st)) {
        const nm = name.slice(2, -2);
        if (!st.mcq && ["part", "or", "sol", "end"].includes(nm) && !this.marksOk(st)) continue;
        if (st.mcq && ["<|ob|>", "<|oc|>", "<|od|>", "<|ans|>"].includes(name)) { const n = norm(raw); if (!n || st.opts.some((o) => norm(o) === n)) continue; }
        allowed.add(T.special.get(name));
      }
    }
    const over = raw.length >= cap;
    return (i) => { if (allowed.has(i)) return true; if (T.isSpecial[i] || T.strs[i] === null || over) return false; if (raw.length + T.strs[i].length > cap + 12) return false; return st.t.copy().feed(T.strs[i]); };
  }
  closeSeg(st) {
    const sec = st.sec, txt = st.t.raw.trim();
    if (sec === "q") st.q = txt; else if (["oa", "ob", "oc", "od"].includes(sec)) st.opts.push(txt); else if (sec === "why") st.why = txt; else if (sec === "sol") st.sol = txt;
    else if (sec === "part") this.curParts(st).at(-1)[1] = txt; else if (sec === "pm") { if (st.pm) this.curParts(st).at(-1)[2] = parseInt(st.pm); st.pm = ""; }
  }
  apply(st, tid) {
    if (st.sec === "ans") { st.key = Object.entries(this.letters).find(([, v]) => v === tid)[0]; st.sec = "ans_done"; return; }
    if (st.sec === "pm" && Object.values(this.digits).includes(tid)) { st.pm += Object.entries(this.digits).find(([, v]) => v === tid)[0]; return; }
    if (this.structIds.has(tid)) {
      const name = Object.entries(this.S).find(([, v]) => v === tid)[0]; this.closeSeg(st); if (name === "end") { st.done = true; return; } st.t = new TextSt();
      if (["oa", "ob", "oc", "od", "ans", "why", "sol"].includes(name)) st.sec = name;
      else if (name === "part") { st.sec = "part"; st.pm = ""; this.curParts(st).push(["", "", 0]); } else if (name === "pm") { st.sec = "pm"; st.pm = ""; } else if (name === "or") { st.sec = "or"; st.inAlt = true; }
      return;
    }
    const s = this.tok.strs[tid]; st.t.feed(s); st.t.raw += s;
  }
  sample(logits, valid, temp, topP, st) {
    const n = logits.length, idx = Array.from({ length: n }, (_, i) => i).sort((a, b) => logits[b] - logits[a]); let cand = [];
    for (let r = 0; r < 96; r++) if (valid(idx[r])) cand.push(idx[r]);
    if (!cand.length) for (let r = 96; r < n && cand.length < 8; r++) if (valid(idx[r])) cand.push(idx[r]);
    if (!cand.length) return null;
    const keep = cand.filter((c) => { const g = [...st.recent.slice(-3), c]; return !(g.length === 4 && st.seen4.has(g.join(","))); }); if (keep.length) cand = keep;
    const mx = Math.max(...cand.map((c) => logits[c])), p = cand.map((c) => Math.exp((logits[c] - mx) / Math.max(temp, 1e-4))); const z = p.reduce((a, b) => a + b, 0);
    const o = cand.map((c, i) => [c, p[i] / z]).sort((a, b) => b[1] - a[1]); let cs = 0, cut = o.length; for (let i = 0; i < o.length; i++) { cs += o[i][1]; if (cs >= topP) { cut = i + 1; break; } }
    const sel = o.slice(0, cut), tot = sel.reduce((a, b) => a + b[1], 0); let u = this.rand() * tot; for (const [c, w] of sel) { u -= w; if (u <= 0) return c; } return sel.at(-1)[0];
  }
  async tryOnce(hid, typ, marks, wantSol, temp, topP, maxTok) {
    const st = this.newState(typ, marks, wantSol); let { logits, st: ks } = await this.step([...hid, this.S.q], null), n = 0;
    while (!st.done && n < maxTok && hid.length + n < 1020) {
      let tid;
      if (st.sec === "ans_done") tid = this.S[wantSol ? "why" : "end"];
      else if (st.sec === "pm" && st.pm) {
        const valid = this.validFn(st), cur = parseInt(st.pm), tot = this.curParts(st).slice(0, -1).reduce((a, p) => a + p[2], 0) + cur; let names = [];
        if (tot < marks) names = ["part"]; else if (tot === marks) names = typ === "OR" && !st.inAlt ? ["or"] : [wantSol ? "sol" : "end"];
        const opts = new Set(names.map((x) => this.S[x])); tid = this.sample(logits, (i) => opts.has(i) || valid(i), temp, topP, st);
      } else tid = this.sample(logits, this.validFn(st), temp, topP, st);
      if (tid === null) return null; this.apply(st, tid); st.recent.push(tid); if (st.recent.length >= 4) st.seen4.add(st.recent.slice(-4).join(",")); n++;
      if (st.done) break; ({ logits, st: ks } = await this.step([tid], ks));
    }
    return st.done ? st : null;
  }
  finalize(st, b, l, s, u, m, t) {
    const h = this.header(b, l, s, u, m, t); let item, txt;
    if (st.mcq) {
      if (st.opts.length !== 4 || !"abcd".includes(st.key)) return null;
      if ([st.q, ...st.opts, st.why].some((x) => checkText(x, true)) || new Set(st.opts.map(norm)).size !== 4) return null;
      item = { kind: "mcq", question: st.q, options: st.opts, key: st.key, explanation: st.why };
    } else {
      if (!this.marksOk(st) || (t === "OR" && !st.alt.length)) return null; const mk = (ps) => ps.map((p, i) => ({ label: String.fromCharCode(97 + i), text: p[1], marks: p[2] }));
      const parts = mk(st.parts), alt = mk(st.alt); if ([...parts, ...alt].some((p) => !p.text)) return null;
      if ([st.q, ...parts.map((p) => p.text), ...alt.map((p) => p.text)].some((x) => checkText(x, true)) || (st.sol && checkText(st.sol))) return null;
      item = { kind: "written", question: st.q, parts, or_parts: alt, rubric: st.sol };
    }
    const cl = cleanSymbols;
    if (item.kind === "mcq") { item.question = cl(item.question); item.options = item.options.map(cl); item.explanation = cl(item.explanation); }
    else { item.question = cl(item.question); item.parts.forEach((p) => (p.text = cl(p.text))); item.or_parts.forEach((p) => (p.text = cl(p.text))); item.rubric = cl(item.rubric); }
    Object.assign(item, { board: b, level: l, subject: s, unit: u, marks: m, type: t });
    const lex = this.lexicons.get(s) || this.lexicons.get(`${b}|${l}|${s}`) || null; const v = verifyItem(item, { unit: u, lexicon: lex, strictAnchor: true });
    if (!v.ok) { for (const r of v.issues) this.stats.rejects[r] = (this.stats.rejects[r] || 0) + 1; return null; }
    item.verify = { score: v.score, anchor_hits: v.anchor.hits, concept_hits: v.anchor.lex }; return item;
  }
  async generateItem({ board, level, subject, unit, marks, type, rubric = true, attempts = 12, temperature = 0.75, topP = 0.92, candidates = 1, signal, anchor = null }) {
    const hid = this.tok.encode(this.header(board, level, subject, unit, marks, type) + (anchor ? `<|book|>${anchor}` : "")); let best = null, found = 0;
    for (let a = 0; a < attempts; a++) {
      if (signal && signal.aborted) throw new ItemGenerationError("aborted"); this.stats.attempts++;
      const st = await this.tryOnce(hid, type, marks, rubric, Math.min(1.1, temperature + 0.03 * a), topP, 520); if (!st) { this.stats.rejects["dead-end"] = (this.stats.rejects["dead-end"] || 0) + 1; continue; }
      const it = this.finalize(st, board, level, subject, unit, marks, type); if (!it) continue;
      it.attempts = a + 1; found++; if (!best || it.verify.score > best.verify.score) best = it; if (found >= candidates) break;
    }
    if (best) { this.stats.items++; return best; }
    throw new ItemGenerationError(`no valid item for ${board}/${level}/${subject}/${unit}/${marks}/${type}`);
  }
  unitsFor(b, l, s) { const u = this.syl.units?.[`${b}|${l}|${s}`]; return u && u.length ? u.slice() : ["General"]; }
  async modelPaper({ board, level, subject, blueprint, rubric = true, onItem, signal, units: unitOverride, candidates = 1 }) {
    const bp = blueprint || BLUEPRINTS[level], units = unitOverride && unitOverride.length ? unitOverride.slice() : this.unitsFor(board, level, subject);
    for (let i = units.length - 1; i > 0; i--) { const j = Math.floor(this.rand() * (i + 1)); [units[i], units[j]] = [units[j], units[i]]; }
    let k = 0; const seen = new Set(), sections = [];
    for (const [g, typ, marks, count] of bp) {
      const items = []; let fails = 0;
      while (items.length < count) {
        if (signal && signal.aborted) throw new ItemGenerationError("aborted");
        const unit = units[k++ % units.length]; const t = typ === "SHORT" ? ["CONCEPTUAL", "NUMERICAL", "DERIVATION", "SHORT"][items.length % 4] : typ; let it;
        try { it = await this.generateItem({ board, level, subject, unit, marks, type: t, rubric, candidates, signal }); }
        catch (e) { if (e.message === "aborted") throw e; if (++fails > 8 * count + 12) throw e; continue; } // resample another unit on dead-end; an invalid item is never emitted
        const key = norm(it.question + (it.options || []).join("")).slice(0, 90); if (seen.has(key)) continue; seen.add(key); it.no = items.length + 1; items.push(it); onItem && onItem(g, it, items.length, count);
      }
      sections.push({ group: g, type: typ, marks_each: marks, count, items });
    }
    return { board, level, subject, total_marks: sections.reduce((a, s) => a + s.marks_each * s.count, 0), sections, generator: "PaperLM-Tiny" };
  }
}
