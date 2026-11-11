// PaperLM Parametric Formula & Distractor Engine (JS twin of engine/parametric.py).
// Numericals / numeric MCQs are NOT written by the language model: every number, unit, key and worked solution is computed from a
// verified law template and the three distractors come from typical-mistake expressions of the same formula (same unit & dimension).
const ENVF = { sqrt: Math.sqrt, sin: Math.sin, cos: Math.cos, tan: Math.tan, atan: Math.atan, ln: Math.log, log10: Math.log10, exp: Math.exp, abs: Math.abs, pi: Math.PI, rad: (d) => (d * Math.PI) / 180,
  comb: (n, k) => { if (k < 0 || k > n) return 0; let r = 1; for (let i = 1; i <= k; i++) r = (r * (n - k + i)) / i; return Math.round(r); },
  perm: (n, k) => { let r = 1; for (let i = 0; i < k; i++) r *= n - i; return r; }, fact: (n) => { let r = 1; for (let i = 2; i <= n; i++) r *= i; return r; }, max: Math.max, min: Math.min, ceil: Math.ceil, floor: Math.floor };
const GENERIC = new Set(["system", "equation", "calculation", "concept", "general", "basic", "introduction", "theory", "number", "formula", "law", "analysis", "principle", "application", "problem", "fundamental", "motion", "wave", "light", "heat", "power"]);
const FILL = [2, 0.5, 10, 0.1, 1.5, 3, 0.25, 4, 0.2, 5];
const cache = new Map();
export class Parametric {
  constructor(lib) { this.lib = lib; this.byId = Object.fromEntries(lib.templates.map((t) => [t.id, t])); }
  ev(expr, env) {
    const names = Object.keys(env); let f = cache.get(expr + "|" + names.join());
    if (!f) { f = new Function(...Object.keys(ENVF), ...names, `return (${expr.replace(/\band\b/g, "&&").replace(/\bor\b/g, "||")});`); cache.set(expr + "|" + names.join(), f); }
    return f(...Object.values(ENVF), ...names.map((n) => env[n]));
  }
  domainsFor(subject) { const s = subject.toLowerCase(), out = []; for (const [rx, doms] of this.lib.domains) if (new RegExp(rx).test(s)) for (const d of doms) if (!out.includes(d)) out.push(d); return out; }
  levelOk(t, level) { const tags = this.lib.levels[level] || "SHEN"; return t.lv === "all" || [...t.lv].some((c) => tags.includes(c)); }
  canMake(subject, level) { const d = this.domainsFor(subject); return d.length > 0 && this.lib.templates.some((t) => this.levelOk(t, level) && t.dom.split(" ").some((x) => d.includes(x))); }
  parseVar(spec) {
    const i = spec.indexOf("="), name = spec.slice(0, i), rng = spec.slice(i + 1); let vals;
    if (rng.startsWith("[")) vals = rng.slice(1, -1).split(",").map(Number); else { const [lo, hi, st] = rng.split(":").map(Number); const n = Math.round((hi - lo) / st) + 1; vals = Array.from({ length: n }, (_, k) => +(lo + k * st).toFixed(10)); }
    return [name, vals];
  }
  rnd(x, sig) { return x === 0 ? 0 : Number(x.toPrecision(sig)); }
  fmt(x, sig = 3) {
    if (x === 0) return "0"; const r = this.rnd(x, sig), a = Math.abs(r);
    if (a >= 1e6 || a < 1e-4) { let [m, e] = r.toExponential(sig - 1).split("e"); if (m.includes(".")) m = m.replace(/0+$/, "").replace(/\.$/, ""); return `${m}\\times10^{${parseInt(e, 10)}}`; }
    return String(r);
  }
  static words(s) { return new Set((String(s).toLowerCase().match(/[a-z]{4,}/g) || []).map((w) => w.replace(/s$/, "")).filter((w) => !GENERIC.has(w))); }
  unitMatch(t, unit) { const uw = Parametric.words(unit); if (!uw.size) return false; return [...Parametric.words(t.unit)].some((w) => uw.has(w)) || t.kw.some((k) => { const kw = [...Parametric.words(k)]; return kw.length > 0 && kw.every((w) => uw.has(w)); }); }
  pick(subject, level, unit, rand, exclude = []) {
    const doms = this.domainsFor(subject); const pool = this.lib.templates.filter((t) => t.dom.split(" ").some((d) => doms.includes(d)) && this.levelOk(t, level) && !exclude.includes(t.id));
    if (!pool.length) return [null, false]; const m = pool.filter((t) => this.unitMatch(t, unit)); const c = m.length ? m : pool;
    return [c[Math.floor(rand() * c.length)], m.length > 0];
  }
  shuffle(a, rand) { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } }
  instantiate(t, rand, vals = null) {
    const vars = Object.fromEntries(t.vars.map((v) => this.parseVar(v)));
    for (let tries = 0; tries < 400; tries++) {
      const env = vals ? { ...vals } : {}; if (!vals) for (const [k, v] of Object.entries(vars)) env[k] = v[Math.floor(rand() * v.length)]; let ans;
      try {
        for (const d of t.derived.split(";").filter(Boolean)) { const i = d.indexOf("="); env[d.slice(0, i).trim()] = this.ev(d.slice(i + 1), env); }
        ans = Number(this.ev(t.ans, env)); if (!Number.isFinite(ans)) throw 0; if (!this.ev(t.cond, { ...env, ans })) throw 0;
      } catch { if (vals) return null; continue; }
      const sig = t.sig; let a = this.rnd(ans, sig); if (Math.abs(ans - Math.round(ans)) < 1e-9 && Math.abs(ans) < 1e9) a = Math.round(ans);
      const seen = new Set([a]); const wrongs = [];
      for (const w of t.wrong) { let v; try { v = Number(this.ev(w, env)); } catch { continue; } if (!Number.isFinite(v)) continue; v = this.rnd(v, sig);
        if (seen.has(v) || v * a <= 0 || this.fmt(v, sig) === this.fmt(a, sig) || !(Math.abs(v / a) >= 0.01 && Math.abs(v / a) <= 100)) continue; seen.add(v); wrongs.push(v); }
      this.shuffle(wrongs, rand);
      for (const m of FILL) { if (wrongs.length >= 3) break; const v = this.rnd(a * m, sig); if (!seen.has(v) && this.fmt(v, sig) !== this.fmt(a, sig)) { seen.add(v); wrongs.push(v); } }
      if (wrongs.length < 3) { if (vals) return null; continue; } return { tpl: t, env, ans: a, wrong: wrongs.slice(0, 3) };
    }
    return null;
  }
  sub(text, env, ans, sig) { return text.replace(/@(\w+)@/g, (_, k) => (k === "ans" ? this.fmt(ans, sig) : this.fmt(Number(env[k]), 6))); }
  withUnit(v, t) { const s = this.fmt(v, t.sig); return t.u ? `$${s}\\ ${t.u}$` : `$${s}$`; }
  render(inst, rand) {
    const { tpl: t, env, ans: a } = inst, sig = t.sig; const stem = this.sub(t.stem, env, a, sig), steps = t.sol.map((s) => this.sub(s, env, a, sig));
    const opts = [a, ...inst.wrong]; const order = [0, 1, 2, 3]; this.shuffle(order, rand);
    return { stem, options: order.map((i) => this.withUnit(opts[i], t)), key: "abcd"[order.indexOf(0)], law: t.law, lawname: t.lawname, steps, answer: this.withUnit(a, t) };
  }
  makeItem(subject, level, unit, marks, typ, rand, exclude = []) {
    const [t, matched] = this.pick(subject, level, unit, rand, exclude); if (!t) return null; const inst = this.instantiate(t, rand); if (!inst) return null;
    const r = this.render(inst, rand); const item = { source: "parametric", verified: true, tpl: t.id, concept: r.law, unit_matched: matched, unit_label: t.unit };
    const expl = r.law + " " + r.steps.join(" ");
    if (typ === "MCQ" || marks <= 1) return Object.assign(item, { kind: "mcq", question: r.stem, options: r.options, key: r.key, explanation: expl });
    const sol = expl + " Answer: " + r.answer + ".";
    if (marks >= 4 && ["NUMERICAL", "OR", "SHORT", "CONCEPTUAL", "LONG"].includes(typ)) {
      const ma = marks === 4 ? 1 : 2; const parts = [{ label: "a", text: `State ${r.lawname}.`, marks: ma }, { label: "b", text: r.stem, marks: marks - ma }];
      Object.assign(item, { kind: "written", question: "Answer the following:", parts, or_parts: [], rubric: `(a) ${r.law} (b) ${r.steps.join(" ")} Answer: ${r.answer}.` });
      if (typ === "OR") { const [t2] = this.pick(subject, level, unit, rand, [...exclude, t.id]); const i2 = t2 && this.instantiate(t2, rand);
        if (i2) { const r2 = this.render(i2, rand); item.or_parts = [{ label: "a", text: `State ${r2.lawname}.`, marks: ma }, { label: "b", text: r2.stem, marks: marks - ma }]; item.rubric += ` OR (a) ${r2.law} (b) ${r2.steps.join(" ")} Answer: ${r2.answer}.`; } }
      return item;
    }
    return Object.assign(item, { kind: "written", question: r.stem, parts: [], or_parts: [], rubric: sol });
  }
}
