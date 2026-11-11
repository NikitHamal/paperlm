// PaperLM Composer (JS twin of engine/composer.py): parametric solver -> concept-grounded LM behind the strict gate -> verified bank.
// An item is never emitted unless it is (a) computed by the symbolic engine, (b) written by the LM from a verified Concept Anchor AND
// accepted by the strict gate, or (c) a gold exam item from the verified bank. Each item carries its provenance tier.
import { gate } from "./ground.js";
import { Parametric } from "./parametric.js";
import { FactBank } from "./factbank.js";
import { canMake as reasonCanMake, makeItem as reasonMakeItem } from "./reasoning.js";
const NOSHUF = /\b(both|all of|none of|above|neither|either|only|a and b|a, b|a & b)\b|^\(?[a-d]\)?$/i;
export class Composer {
  constructor(engine, bank, templates, facts) { this.e = engine; this.bank = bank; this.pm = new Parametric(templates); this.fb = facts ? new FactBank(facts) : null; this.biasBeta = 2.5; this.stats = { param: 0, fact: 0, reason: 0, lm: 0, bank: 0, lm_tries: 0, lm_gate_pass: 0, gate_rejects: {} }; }
  // Boards such as IOE/CEE/TU expose a "model-papers" subject whose units name the real subject; resolve it.
  effSubject(subject, unit) {
    if (this.pm.domainsFor(subject).length || reasonCanMake(subject) || (this.fb && this.fb.canMake(subject))) return subject;
    const u = (unit || "").toLowerCase();
    for (const [pat, sub] of [["mathemat", "mathematics"], ["physic", "physics"], ["chemist", "chemistry"], ["botan", "botany"], ["zoolog", "zoology"], ["english", "english"], ["mental", "mental-agility-test"], ["agility", "mental-agility-test"]]) if (u.includes(pat)) return sub;
    return subject;
  }
  get rand() { return this.e.rand; }
  facts(key, unit) { const f = this.bank.facts[key] || {}; let l = f[unit] || []; if (!l.length) { const lu = Object.keys(f).find((u) => u.toLowerCase().includes(unit.toLowerCase()) || unit.toLowerCase().includes(u.toLowerCase())); if (lu) l = f[lu]; } return l; }
  seeds(key, unit, marks, mcq) {
    // tiers: same unit -> fuzzy unit (exact=true) -> any unit of the subject -> nearest written class -> same subject on other boards (exact=false). Never invents content.
    const want = mcq ? "mcq" : `w${marks}`, ok = (x) => mcq || (x.r && x.r.length > 15 && x.q && x.q.length > 8), pick = (arr) => arr.filter((x) => x.c === want && ok(x)); const s = this.bank.seeds[key] || {}; let l = pick(s[unit] || []), u = unit;
    if (l.length) return [u, l, true];
    const lu = Object.keys(s).find((k) => pick(s[k]).length && (k.toLowerCase().includes(unit.toLowerCase()) || unit.toLowerCase().includes(k.toLowerCase()))); if (lu) return [lu, pick(s[lu]), true];
    const all = Object.entries(s).flatMap(([k, v]) => pick(v).map((x) => [k, x])); if (all.length) { const [k, x] = all[Math.floor(this.rand() * all.length)]; return [k, [x], false]; }
    if (!mcq) { const w = Object.entries(s).flatMap(([k, v]) => v.filter((x) => x.c !== "mcq" && ok(x)).map((x) => [k, x])); if (w.length) { const near = Math.min(...w.map(([, x]) => Math.abs(x.m - marks))); const c = w.filter(([, x]) => Math.abs(x.m - marks) === near); const [k, x] = c[Math.floor(this.rand() * c.length)]; return [k, [x], false]; } }
    const subj = key.split("|")[2]; const c = Object.entries(this.bank.seeds).filter(([k]) => (k.split("|")[2] === subj || k.split("|")[2].includes(subj) || subj.includes(k.split("|")[2])) && k !== key).flatMap(([, v]) => Object.entries(v).flatMap(([k2, arr]) => (mcq ? pick(arr) : arr.filter((x) => x.c !== "mcq" && ok(x) && Math.abs(x.m - marks) <= 2)).map((x) => [k2, x])));
    if (c.length) { const [k, x] = c[Math.floor(this.rand() * c.length)]; return [k, [x], false]; }
    return [u, [], false];
  }
  fromSeed(s, unit, board, level, subject, typ) {
    const base = { board, level, subject, unit, marks: s.m, type: typ === "MCQ" ? "MCQ" : s.t || typ, source: "bank", verified: true, provenance: s.v === "T32" ? { tier: "teacher", p_blind: s.p, computed_check: !!s.n } : { tier: "bank", judged: s.j === 1 } };
    if (s.c === "mcq") {
      let o = s.o.slice(), k = s.k;
      if (!o.some((x) => NOSHUF.test(x))) { const perm = [0, 1, 2, 3]; for (let i = 3; i > 0; i--) { const j = Math.floor(this.rand() * (i + 1)); [perm[i], perm[j]] = [perm[j], perm[i]]; } o = perm.map((i) => s.o[i]); k = "abcd"[perm.indexOf("abcd".indexOf(s.k))]; }
      return { ...base, kind: "mcq", question: s.q, options: o, key: k, explanation: s.w || "", marks: 1 };
    }
    const mk = (ps) => (ps || []).map(([l, t, m], i) => ({ label: l || String.fromCharCode(97 + i), text: t, marks: m }));
    return { ...base, kind: "written", question: s.q, parts: mk(s.p), or_parts: mk(s.a), rubric: s.r || "" };
  }
  // opts: lmBudget (max LM attempts, 0 disables the LM tier), signal, temperature, rubric
  // Tier order by item type. The fact tier answers non-numeric items from closed-world tables, so it can never hallucinate;
  // the parametric tier computes every number; the gold bank is past-paper material. The LM tier is last and off by default.
  order(type, mcq, canp, canf, r, canr) {
    if (canr) return ["reason", "fact", "bank"];
    if (type === "NUMERICAL" || type === "DERIVATION") return canp ? ["param", "bank"] : ["bank"];
    if (mcq) return canp && r < 0.35 ? ["param", "fact", "bank", "lm"] : canf ? ["fact", "param", "bank", "lm"] : ["param", "bank", "lm"];
    return canf ? ["fact", "param", "bank", "lm"] : ["param", "bank", "lm"];
  }
  async item({ board, level, subject, unit, marks, type, lmBudget = 0, signal, temperature = 0.75, rubric = true, biasBeta = this.biasBeta }) {
    const key = `${board}|${level}|${subject}`, mcq = type === "MCQ" || marks <= 1, r = this.rand();
    const eff = this.effSubject(subject, unit);
    const canp = this.pm.canMake(eff, level), canf = !!(this.fb && this.fb.canMake(eff)) && type !== "DERIVATION";
    const canr = reasonCanMake(eff);
    const order = this.order(type, mcq, canp, canf, r, canr);
    for (const strict of [true, false]) for (const tier of order) {
      if (signal && signal.aborted) throw new Error("aborted");
      if (tier === "reason" && canr) {
        const it = reasonMakeItem(eff, unit, marks, type, this.rand);
        if (it) { this.stats.reason++; return Object.assign(it, { board, level, subject, unit, marks, type, provenance: { tier: "reason", topic: it.topic } }); }
      } else if (tier === "fact" && canf) {
        let it = this.fb.makeItem(eff, unit, marks, type, this.rand);
        if (it && strict && !it.unit_matched) it = null;
        if (it) { this.stats.fact++; return Object.assign(it, { board, level, subject, unit: it.unit_matched ? unit : it.topic, marks, type, provenance: { tier: "fact", fact_id: it.fact_id, topic: it.topic, src: it.fact_src } }); }
      } else if (tier === "param" && canp) {
        const it = this.pm.makeItem(eff, level, unit, marks, mcq ? "MCQ" : type, this.rand);
        if (it && (it.unit_matched || tier === order[0] || !this.facts(key, unit).length)) { this.stats.param++; return Object.assign(it, { board, level, subject, unit: it.unit_matched ? unit : it.unit_label, marks, type, provenance: { tier: "param", law: it.concept } }); }
      } else if (tier === "lm" && lmBudget > 0 && this.e) {
        const fs = this.facts(key, unit); let used = 0;
        for (let a = 0; a < (fs.length ? 3 : 0) && used < lmBudget; a++) {
          const anc = fs[Math.floor(this.rand() * fs.length)];
          for (let k = 0; k < 4 && used < lmBudget; k++, used++) {
            if (signal && signal.aborted) throw new Error("aborted"); this.stats.lm_tries++; let it;
            try { it = await this.e.generateItem({ board, level, subject, unit, marks, type, attempts: 1, temperature: Math.min(1, temperature - 0.05 + 0.05 * k), anchor: anc, rubric, signal, biasBeta }); } catch (e) { if (e.message === "aborted") throw e; continue; }
            const g = gate(it, anc);
            if (g.ok) { this.stats.lm_gate_pass++; this.stats.lm++; return Object.assign(it, { provenance: { tier: "lm", anchor: anc, gate: { p: g.p, r: g.r } }, verified: false, experimental: true, source: "lm" }); }
            for (const x of g.issues) { const kx = x.replace(/:.*/, ""); this.stats.gate_rejects[kx] = (this.stats.gate_rejects[kx] || 0) + 1; }
          }
        }
      } else if (tier === "bank") {
        const [u, l, exact] = this.seeds(key, unit, marks, mcq);
        if (l.length && !exact && canp) { const it = this.pm.makeItem(subject, level, unit, marks, mcq ? "MCQ" : type, this.rand); if (it && it.unit_matched) { this.stats.param++; return Object.assign(it, { board, level, subject, unit, marks, type, provenance: { tier: "param", law: it.concept } }); } }
        if (l.length) { this.stats.bank++; return this.fromSeed(l[Math.floor(this.rand() * l.length)], u, board, level, subject, type); }
      }
    }
    throw new Error(`no verified item for ${key}/${unit}/${marks}/${type}`);
  }
}
