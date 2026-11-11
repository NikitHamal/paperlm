// Strict Semantic & Factual Coherence Gate (JS twin of engine/ground.py).
// A candidate written by the 10M LM from a verified Concept Anchor is accepted ONLY if it is grounded in that anchor:
// no invented numbers/symbols, explanation/rubric lexically grounded, on-topic, key option supported, no second supported option.
const STOP = new Set(("a about all also an and another any are as at be because between both but by calculate called can did does done during each find following for from give given gives had has have hence her his how if in into is it its known made make makes may more most must no not of on one only or other our over per should so some state such than that the their them then there therefore these they this those thus to two under use used using via was we were what when where which while whom whose why will with would write you your").split(" "));
const WORD = /[a-z\u0900-\u097f]{4,}/g;
const NUM = /(?<![\w.])\d+(?:\.\d+)?/g;
const SYM_SKIP = new Set(["\\text", "\\mathrm", "\\frac", "\\dfrac", "\\tfrac", "\\left", "\\right", "\\times", "\\cdot", "\\ ", "\\quad", "\\textbf", "\\textit", "\\mathbf", "\\sqrt"]);
export const strip = (s) => (s || "").replace(/\\(?:text|mathrm|textbf|textit|mathbf)\{([^}]*)\}/g, " $1 ");
export function cwords(s) {
  const out = new Set(); for (const w0 of strip(s).toLowerCase().match(WORD) || []) { if (STOP.has(w0)) continue; out.add(w0.endsWith("s") && w0.length > 4 ? w0.slice(0, -1) : w0); } return out;
}
export const nums = (s) => new Set(strip(s).replace(/\\(?:tfrac|dfrac|frac)/g, " ").match(NUM) || []);
export const sym = (s) => new Set((String(s || "").match(/\\[A-Za-z]+/g) || []).filter((x) => !SYM_SKIP.has(x)));
const inter = (a, b) => { let n = 0; for (const x of a) if (b.has(x)) n++; return n; };
const union = (...ss) => { const o = new Set(); for (const s of ss) for (const x of s) o.add(x); return o; };
const minus = (a, ...bs) => [...a].filter((x) => !bs.some((b) => b.has(x)));
export function itemText(it) { return [it.question, ...(it.options || []), ...(it.parts || []).map((p) => p.text), ...(it.or_parts || []).map((p) => p.text)].join(" "); }
function repetitive(t) {
  const w = strip(t).toLowerCase().match(/[a-z]{3,}/g) || []; const cw = w.filter((x) => !STOP.has(x)); const cnt = {};
  for (const x of cw) { cnt[x] = (cnt[x] || 0) + 1; if (cnt[x] >= 3) return true; }
  const bg = {}; for (let i = 0; i + 1 < w.length; i++) { if (STOP.has(w[i]) && STOP.has(w[i + 1])) continue; const k = w[i] + " " + w[i + 1]; bg[k] = (bg[k] || 0) + 1; if (bg[k] >= 2) return true; }
  return false;
}
export function gate(item, anchor, minP = 0.8, minR = 0.5) {
  const issues = []; const A = cwords(anchor), an = nums(anchor), asym = sym(anchor); const q = item.question; const ctx = itemText(item), C = cwords(ctx);
  if (!A.size) return { ok: false, issues: ["empty anchor"], p: 0, r: 0 };
  let p, r, ansAll;
  if (item.kind === "mcq") {
    const key = "abcd".indexOf(item.key), ans = item.options[key], expl = item.explanation || ""; const E = union(cwords(expl), cwords(ans)), allowed = union(A, cwords(q));
    p = inter(E, allowed) / Math.max(1, E.size); r = inter(A, union(E, cwords(q), cwords(ans))) / A.size;
    if (!inter(cwords(q), A)) issues.push("question off-topic for the anchor");
    const bad = minus(union(nums(expl), nums(ans)), an, nums(q)); if (bad.length) issues.push("number not in anchor: " + bad.sort()[0]);
    const ac = cwords(ans); if (ac.size && inter(ac, union(A, cwords(q))) / ac.size < 0.5 && !nums(ans).size) issues.push("key option not supported by the anchor");
    item.options.forEach((o, i) => {
      if (i === key) return; const oc = cwords(o);
      if (oc.size >= 2 && inter(oc, A) / oc.size >= 0.9 && !q.toLowerCase().includes(o.trim().toLowerCase())) issues.push(`distractor ${"abcd"[i]} is also supported by the anchor`);
      const on = nums(o), kn = nums(ans); if (on.size && [...on].every((x) => an.has(x)) && !(on.size === kn.size && [...on].every((x) => kn.has(x))) && kn.size) issues.push(`distractor ${"abcd"[i]} repeats an anchor figure`);
    });
    ansAll = expl + " " + ans;
    if (p < minP) issues.push("explanation not grounded in the anchor");
  } else {
    const rub = item.rubric || ""; const E = cwords(rub), allowed = union(A, cwords(ctx)); p = inter(E, allowed) / Math.max(1, E.size); r = inter(A, union(E, C)) / A.size;
    if (!inter(C, A)) issues.push("question off-topic for the anchor");
    const bad = minus(nums(rub), an, nums(ctx)); if (bad.length && !/\\(?:frac|sqrt|int|sum)/.test(rub)) issues.push("number not in anchor: " + bad.sort()[0]);
    if (rub && E.size >= 4 && p < minP) issues.push("rubric not grounded in the anchor");
    ansAll = rub; if (!rub.trim()) issues.push("no rubric");
  }
  const bs = minus(sym(ansAll), asym, sym(ctx)); if (bs.length) issues.push("symbol not in anchor: " + bs.sort()[0]);
  if (repetitive(item.question) || [...(item.parts || []), ...(item.or_parts || [])].some((x) => repetitive(x.text))) issues.push("repetitive wording");
  if (r < minR) issues.push("anchor concept barely used");
  return { ok: !issues.length, issues, p: +p.toFixed(3), r: +r.toFixed(3) };
}
