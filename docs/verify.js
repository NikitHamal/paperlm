// PaperLM verification layer (Fix 3): symbol cleanup, MCQ dimensional-homogeneity, answer-key consistency, concept anchoring.
// Mirrors engine/verify.py. Pure functions, no dependencies (browser, node, and the Android port use the same rules).

const WORD = /[A-Za-z\u0900-\u097F]{2,}/g;
export const STOP = new Set("the of a an and or in on to is are was were be by for with as at from that this which what following these those its it into than then their there has have had can will would should not no all any each one two three four give write state define explain find calculate prove show using used use following correct incorrect true false value values".split(" "));

// ---- symbol cleanup: models cannot emit multi-byte symbols in one token, so normalise every spelling to one KaTeX-safe form
export function cleanSymbols(t) {
  if (!t) return t;
  let out = "", i = 0;
  while (i < t.length) {
    if (t[i] === "$") {
      const d = t.startsWith("$$", i) ? "$$" : "$"; const k = t.indexOf(d, i + d.length);
      if (k < 0) { out += t.slice(i); break; }
      let m = t.slice(i + d.length, k);
      m = m.replace(/\\leqslant|\\leq(?![A-Za-z])|\\le(?![A-Za-z])/g, "\\leq").replace(/\\geqslant|\\geq(?![A-Za-z])|\\ge(?![A-Za-z])/g, "\\geq")
        .replace(/<=/g, "\\leq ").replace(/>=/g, "\\geq ").replace(/\\neq(?![A-Za-z])/g, "\\neq").replace(/!=/g, "\\neq ")
        .replace(/\s{2,}/g, " ").trim();
      out += d + m + d; i = k + d.length;
    } else { let j = t.indexOf("$", i); if (j < 0) j = t.length; out += t.slice(i, j).replace(/<=/g, "\u2264").replace(/>=/g, "\u2265").replace(/!=/g, "\u2260"); i = j; }
  }
  return out.replace(/ {2,}/g, " ").replace(/\$ +\$/g, " ").replace(/ +([,.;:?])/g, "$1").trim();
}

const stripMath = (s) => s.replace(/\$\$?/g, "");
const NUM = /-?\d+(?:\.\d+)?(?:\s*\\times\s*10\^\{?-?\d+\}?)?/;
function units(s) {
  // collect unit-like tokens: \text{..}, \mathrm{..}, trailing letters after a number, degree, percent
  const u = [];
  for (const m of s.matchAll(/\\(?:text|mathrm)\{\s*([^}]*)\}/g)) u.push(m[1].replace(/\s+/g, "").toLowerCase());
  const nu = /\d\s*\}?\s*(?:\\,|\\ |\s)*([A-Za-z]{1,3}(?:\/[A-Za-z]{1,3})?(?:\^\{?-?\d\}?)?)\s*$/.exec(stripMath(s).trim()); if (nu && !/^(and|or|is|a)$/i.test(nu[1])) u.push(nu[1].toLowerCase());
  if (/\^\\circ|\u00b0/.test(s)) u.push("deg"); if (/%|\\%/.test(s)) u.push("%");
  return u.join("|");
}
export function shape(opt) {
  const raw = opt.trim(); const noM = raw.replace(/\$[^$]*\$/g, " ").replace(/\s+/g, " ").trim(); const words = (noM.match(WORD) || []).length;
  const hasMath = /\$/.test(raw); const body = stripMath(raw).trim();
  const digits = /\d/.test(body); const numeric = digits && new RegExp("^[^A-Za-z]*" + NUM.source + "[^A-Za-z]*(?:\\\\(?:text|mathrm)\\{[^}]*\\})?[^A-Za-z]*[A-Za-z%/^{}\\-\\d\\\\ ,]*$").test(body) && words <= 1;
  const cls = words >= 3 ? "text" : numeric ? "num" : hasMath || /[=+\-*/^]/.test(body) ? "expr" : "word";
  return { cls, words, len: raw.length, unit: units(raw), digits, numeric, hasMath, body };
}
const numVal = (s) => { const m = /(-?\d+(?:\.\d+)?)/.exec(stripMath(s).replace(/,(?=\d{3})/g, "")); return m ? parseFloat(m[1]) : null; };
const normT = (s) => s.toLowerCase().replace(/[^a-z0-9\u0900-\u097F]+/g, "");

// ---- MCQ homogeneity: 4 options must be the same kind of thing (same dimensions/unit/form)
export function checkOptions(opts, question = "") {
  const issues = []; const sh = opts.map(shape);
  const classes = new Set(sh.map((s) => (s.cls === "num" || s.cls === "expr" ? "math" : s.cls === "word" ? "text" : s.cls)));
  if (classes.size > 1) issues.push("option kinds differ (" + [...classes].join("/") + ")");
  const nums = sh.filter((s) => s.cls === "num");
  if (nums.length >= 2) { const us = new Set(nums.map((s) => s.unit)); if (us.size > 1 && nums.length === 4) issues.push("option units differ"); }
  const withU = sh.filter((s) => s.unit).length; if (withU && withU < 4 && sh.every((s) => s.digits)) issues.push("some options lack the unit");
  const lens = sh.map((s) => Math.max(1, s.len)); if (Math.max(...lens) / Math.min(...lens) > (classes.has("text") ? 6 : 12)) issues.push("option length mismatch");
  if (sh.every((s) => s.cls === "num")) { const v = sh.map((s) => numVal(s.body)); if (new Set(v.map(String)).size < 4) issues.push("numeric duplicates"); }
  // foreign subscripted symbols appearing in a single option only (e.g. I_6/2 in a question about voltage)
  const sub = opts.map((o) => new Set([...o.matchAll(/([A-Za-z])_\{?(\w)\}?/g)].map((m) => m[1] + m[2])));
  const qs = new Set([...question.matchAll(/([A-Za-z])_\{?(\w)\}?/g)].map((m) => m[1] + m[2]));
  sub.forEach((s, i) => { for (const sym of s) if (!qs.has(sym) && sub.filter((x, j) => j !== i && x.has(sym)).length === 0 && sub.some((x, j) => j !== i && x.size === 0)) issues.push("foreign symbol " + sym); });
  if (opts.some((o) => /all of the above|none of the above/i.test(o)) && opts.filter((o) => /(all|none) of the above/i.test(o)).length > 1) issues.push("duplicate catch-all");
  return issues;
}

// ---- key consistency: the explanation must support the keyed option and not a different one
export function checkKey(opts, key, why) {
  const issues = []; const k = "abcd".indexOf(key); if (k < 0) return ["bad key"]; if (!why) return issues;
  const wn = normT(stripMath(why)); const hits = opts.map((o) => { const n = normT(stripMath(o)); return n.length >= 2 && wn.includes(n); });
  const anyHit = hits.some(Boolean);
  if (anyHit && !hits[k]) issues.push("explanation names a different option than the key");
  // numeric: final values in the explanation vs options
  const nums = [...stripMath(why).replace(/,(?=\d{3})/g, "").matchAll(/=\s*(-?\d+(?:\.\d+)?)/g)].map((m) => parseFloat(m[1]));
  if (nums.length) { const last = nums[nums.length - 1]; const ov = opts.map((o) => numVal(o)); const hit = ov.map((v, i) => (v !== null && Math.abs(v - last) <= 1e-9 + 1e-6 * Math.abs(last) ? i : -1)).filter((i) => i >= 0); if (hit.length === 1 && hit[0] !== k && opts.every((o) => shape(o).digits)) issues.push("computed value matches option " + "abcd"[hit[0]] + ", key is " + key); }
  return issues;
}


// ---- arithmetic self-consistency: every "a op b ... = c" chain of plain numbers in the explanation/rubric must be numerically right
const ARITH = /(?<![A-Za-z0-9_^{.\\])(-?\d+(?:\.\d+)?(?:\s*(?:\\times|\\cdot|\\div|\+|-|\*|\/)\s*\d+(?:\.\d+)?)+)\s*=\s*(-?\d+(?:\.\d+)?)(?![\d.]*[A-Za-z^_/{])/g;
function evalChain(e) {
  const t = e.replace(/\\times|\\cdot/g, "*").replace(/\\div/g, "/").replace(/\s+/g, ""); if (!/^[\d.+\-*/]+$/.test(t)) return null;
  const toks = t.match(/-?\d+(?:\.\d+)?|[+\-*/]/g); if (!toks) return null; const out = [toks[0] === undefined ? 0 : parseFloat(toks[0])]; const ops = [];
  for (let i = 1; i < toks.length; i += 2) { const op = toks[i], v = parseFloat(toks[i + 1]); if (Number.isNaN(v)) return null; if (op === "*") out.push(out.pop() * v); else if (op === "/") out.push(out.pop() / v); else { ops.push(op); out.push(v); } }
  let r = out[0]; for (let i = 0; i < ops.length; i++) r = ops[i] === "+" ? r + out[i + 1] : r - out[i + 1]; return r;
}
export function checkArith(text) {
  const bad = []; const t = stripMath(text).replace(/\\(?:text|mathrm)\{[^}]*\}/g, " ");
  for (const m of t.matchAll(ARITH)) { const v = evalChain(m[1]), c = parseFloat(m[2]); if (v === null || !isFinite(v)) continue; if (Math.abs(v - c) > Math.max(0.02 * Math.abs(v), 0.0105)) bad.push(`${m[1].trim()} = ${m[2]} (is ${+v.toPrecision(4)})`); }
  return bad;
}

// ---- concept anchoring: the item must talk about the requested unit/subject
export function words(s) { return (stripMath(s).toLowerCase().match(WORD) || []).filter((w) => !STOP.has(w)); }
export function anchorScore(text, unit, lexicon) {
  const ws = new Set(words(text)); if (!ws.size) return { score: 0, hits: 0 };
  const uw = words(unit || "").filter((w) => !/^(unit|paper|model|question|set|general|stream|chapter)$/.test(w)); let hits = uw.filter((w) => ws.has(w)).length;
  let lex = 0; if (lexicon) for (const w of ws) if (lexicon.has(w)) lex++;
  return { score: (hits ? 1 : 0) * 0.5 + Math.min(1, lex / 3) * 0.5, hits, lex, lexN: lexicon ? lexicon.size : 0 };
}

export function verifyItem(item, { unit = "", lexicon = null, strictAnchor = false } = {}) {
  const issues = []; let score = 1;
  const text = [item.question, ...(item.options || []), item.explanation || "", ...(item.parts || []).map((p) => p.text), ...(item.or_parts || []).map((p) => p.text), item.rubric || ""].join(" ");
  if (item.kind === "mcq") {
    if (words(item.question).length < 2) issues.push("question too short");
    issues.push(...checkOptions(item.options, item.question)); issues.push(...checkKey(item.options, item.key, item.explanation));
    if (!item.explanation) score -= 0.15;
    const lo = item.options.map((o) => normT(stripMath(o))); if (lo.some((o) => o.length > 3 && normT(item.question).includes(o) && o.length > 12)) score -= 0.1;
  } else {
    if (words(item.question + " " + item.parts.map((p) => p.text).join(" ")).length < 3) issues.push("written item too short");
    if (item.parts.some((p) => p.text.length < 8)) issues.push("part too short");
    if (item.parts.length > 6) issues.push("too many parts");
  }
  const bad = checkArith(text); if (bad.length) issues.push("arithmetic error: " + bad[0]);
  const a = anchorScore(text, unit, lexicon); score = score * 0.6 + a.score * 0.4;
  if (strictAnchor && lexicon && lexicon.size > 50 && a.lex === 0 && words(text).length > 8) issues.push("no syllabus concept in item");
  if (/(.)\1{5,}/.test(text)) issues.push("character run");
  return { ok: issues.length === 0, issues, score: +score.toFixed(3), anchor: a };
}
