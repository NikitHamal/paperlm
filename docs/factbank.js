// PaperLM Fact Bank (JS twin of engine/factbank.py).
// The verified "fact" tier: closed-world tables of (key, value, definition) rows.  A question is a projection of one row and
// its three distractors are the values (or keys) of other rows of the same class chosen so that no two options share a value.
// So the key is correct by construction, no distractor can also be correct, and no free text is generated at all.
// Class selection is unit-aware: keyword list, then lexical overlap, else the item is marked unit_matched = false so the
// caller labels it with the class topic instead of the requested unit.
const STOP = new Set("the of and for with from that this which their there into than then were was are its his her has have had not all any each both one two three four five some more most other only over under between during using used use called known given state write find name explain define when where while whose whom how why does did make makes made give gives must but because therefore thus hence about per via also".split(" "));
const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, "");
const words = (s) => new Set((String(s).toLowerCase().match(/[a-z]{4,}/g) || []).filter((w) => !STOP.has(w)));
const stem6 = (w) => w.slice(0, 6);
function article(word) {
  const low = String(word).toLowerCase().replace(/^[^a-z]+/, "");
  return "aeiou".includes(low[0]) && !/^(uni|use|one|eu)/.test(low) ? "an" : "a";
}
function fill(tpl, k, v) {
  if (tpl.includes(" a {k}") && article(k) === "an") tpl = tpl.replace(" a {k}", " an {k}");
  return tpl.split("{k}").join(k).split("{v}").join(v);
}
function shuffle(a, rand) { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } }

export class FactBank {
  constructor(doc) {
    this.classes = doc.classes; this.stats = doc.stats || {};
    this.rx = this.classes.map((c) => [c, c.subjects.map((p) => new RegExp(p, "i"))]);
    this.cw = {}; for (const c of this.classes) { const w = words(c.label); for (const [k, v] of c.pairs) { for (const x of words(k)) w.add(x); for (const x of words(v)) w.add(x); } this.cw[c.id] = w; }
  }
  classesFor(subject) { return this.rx.filter(([, rxs]) => rxs.some((r) => r.test(subject || ""))).map(([c]) => c); }
  canMake(subject) { return this.classesFor(subject).length > 0; }
  relevance(cls, unit) {
    const u = words(unit); let n = 0;
    for (const x of u) for (const y of this.cw[cls.id]) if (x === y || (x.length >= 6 && stem6(x) === stem6(y))) { n++; break; }
    return n;
  }
  pickClass(subject, unit, rand, exclude = []) {
    let cs = this.classesFor(subject).filter((c) => !exclude.includes(c.id)); if (!cs.length) cs = this.classesFor(subject); if (!cs.length) return [null, false];
    if (unit) {
      const ul = unit.toLowerCase();
      const kw = cs.filter((c) => (c.units || []).some((k) => ul.includes(k.toLowerCase())));
      if (kw.length) return [kw[Math.min(kw.length - 1, Math.floor(rand() * kw.length))], true];
      // No lexical guessing: a class is either declared for this unit by its keyword list, or it is offered as a
      // topic-labelled item (unit_matched = false) that the caller may use as a last resort.
    }
    return [cs[Math.min(cs.length - 1, Math.floor(rand() * cs.length))], false];
  }
  makeItem(subject, unit, marks, type, rand) {
    const [cls, matched] = this.pickClass(subject, unit, rand); if (!cls) return null;
    const rows = cls.pairs, i = Math.min(rows.length - 1, Math.floor(rand() * rows.length));
    if (type === "MCQ" || marks <= 1) { const m = this.mcq(cls, rows, i, rand); if (m) m.unit_matched = matched; return m; }
    const it = this.written(cls, marks, rand, subject, unit); if (it) it.unit_matched = matched; return it;
  }
  mcq(cls, rows, i, rand) {
    const [k, v, d] = rows[i], cat = !!cls.cat;
    const distinctVals = new Set(rows.map((r) => norm(r[1]))).size;
    const reverse = !!cls.qb && (distinctVals < 4 || rand() < 0.35);
    let stem, answer, pool, field;
    if (reverse) { stem = fill(cls.qb, k, v); answer = k; field = 0; pool = rows.filter((r, j) => j !== i && norm(r[1]) !== norm(v)); }
    else {
      stem = fill(cls.qa, k, v); answer = v; field = 1;
      pool = cat ? rows.filter((r, j) => j !== i && norm(r[0]) !== norm(k)) : rows.filter((r, j) => j !== i && norm(r[1]) !== norm(v));
    }
    const seen = new Set([norm(answer)]), opts = [];
    shuffle(pool, rand);
    for (const r of pool) { const t = norm(r[field]); if (seen.has(t)) continue; seen.add(t); opts.push(r[field]); if (opts.length === 3) break; }
    if (opts.length < 3) return null;
    const options = opts.concat([answer]); shuffle(options, rand);
    const key = "abcd"[options.indexOf(answer)];
    let expl = String(d).trim(); if (!expl.endsWith(".")) expl += ".";
    expl += " Therefore the correct answer is " + answer + ".";
    return { source: "fact", verified: true, kind: "mcq", question: stem, options, key, explanation: expl, topic: cls.label,
      fact_id: cls.id, fact_src: cls.src, fact_row: i, fact_dir: reverse ? "reverse" : "forward", unit_matched: true, unit_label: null };
  }
  written(cls, marks, rand, subject, unit) {
    const need = marks <= 3 ? 1 : marks < 6 ? 2 : 3;
    const parts_meta = [[cls, Math.min(cls.pairs.length - 1, Math.floor(rand() * cls.pairs.length))]];
    const used = new Set([cls.id]);
    const pool = [cls].concat(this.classesFor(subject).filter((c) => c !== cls));
    for (let n = 1; n < need; n++) {
      let [c2, matched] = this.pickClass(subject, unit, rand, [...used]);
      if (!matched) c2 = cls;  // keep the written item inside one unit
      used.add(c2.id);
      parts_meta.push([c2, Math.min(c2.pairs.length - 1, Math.floor(rand() * c2.pairs.length))]);
    }
    const qs = parts_meta.map(([c, i]) => fill(c.qo, c.pairs[i][0], c.pairs[i][1]));
    const defs = parts_meta.map(([c, i]) => c.pairs[i][2]);
    const meta = { source: "fact", verified: true, kind: "written", or_parts: [], topic: cls.label, fact_id: cls.id, fact_src: cls.src,
      fact_row: parts_meta[0][1], fact_parts: parts_meta.map(([c, i]) => ({ fact_id: c.id, fact_row: i, src: c.src, topic: c.label })),
      unit_matched: true, unit_label: null };
    if (need === 1) return { ...meta, question: qs[0], parts: [], rubric: defs[0] };
    const base = Math.floor(marks / qs.length), extra = marks % qs.length;
    const parts = qs.map((t, x) => ({ label: "abc"[x], text: t, marks: base + (x < extra ? 1 : 0) }));
    const rubric = parts.map((p, x) => `(${p.label}) ${defs[x]} [${p.marks}]`).join(" ");
    return { ...meta, question: "Answer the following:", parts, rubric };
  }
}
