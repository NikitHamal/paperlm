// PaperLM Reasoning Engine (JS twin of engine/reasoning.py): mental-agility number and letter series.
// The series comes from a rule, the key is the rule's next term, and the three distractors are what the typical wrong rules
// give (one step extra, one step fewer, off by one), so all four options are computed and provably distinct.
function shuffle(a, rand) { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } }
function mcq(stem, answer, distractors, law, rand) {
  const opts = distractors.slice(0, 3).map(String);
  if (new Set(opts).size < 3 || opts.includes(String(answer))) return null;
  const options = opts.concat([String(answer)]); shuffle(options, rand);
  return { source: "reasoning", verified: true, kind: "mcq", question: stem, options, key: "abcd"[options.indexOf(String(answer))],
    explanation: law + " So the answer is " + String(answer) + ".", topic: "Reasoning series", unit_matched: true, unit_label: null };
}
export function canMake(subject) {
  const toks = String(subject || "").toLowerCase().split(/[^a-z]+/);
  return toks.includes("mental") || toks.includes("reasoning") || toks.includes("aptitude");
}
function written(marks, rand) {
  const need = marks <= 3 ? 1 : marks < 6 ? 2 : 3, qs = [], laws = [];
  for (let i = 0; i < need; i++) for (let t = 0; t < 40; t++) { const it = makeItem("", "", 1, "MCQ", rand); if (it && !qs.includes(it.question)) { qs.push(it.question); laws.push(it.explanation); break; } }
  const base = Math.floor(marks / need), extra = marks % need;
  const parts = qs.map((t, x) => ({ label: "abc"[x], text: t, marks: base + (x < extra ? 1 : 0) }));
  const rubric = parts.map((p, x) => `(${p.label}) ${laws[x]} [${p.marks}]`).join(" ");
  return { source: "reasoning", verified: true, kind: "written", question: "Answer the following:", parts: need > 1 ? parts : [], or_parts: [], rubric, topic: "Reasoning series", unit_matched: true, unit_label: null };
}
export function makeItem(subject, unit, marks, type, rand) {
  if (!(type === "MCQ" || marks <= 1)) return written(marks, rand);
  const r = rand();
  if (r < 0.30) {
    const a = Math.floor(1 + rand() * 12), d = Math.floor(1 + rand() * 9);
    const t = Array.from({ length: 5 }, (_, i) => a + i * d), ans = a + 5 * d;
    return mcq("Find the next term of the series: " + t.join(", ") + ", ?", ans, [ans + d, ans - d, ans + 2 * d],
      `Each term increases by ${d}, so the next term is ${t[4]}+${d}=${ans}.`, rand);
  }
  if (r < 0.50) {
    const a = Math.floor(1 + rand() * 4), g = Math.floor(2 + rand() * 2);
    const t = Array.from({ length: 4 }, (_, i) => a * g ** i), ans = a * g ** 4;
    return mcq("Find the next term of the series: " + t.join(", ") + ", ?", ans, [a * g ** 3, a * g ** 5, ans + g],
      `Each term is multiplied by ${g}, so the next term is ${t[3]}x${g}=${ans}.`, rand);
  }
  if (r < 0.70) {
    const n = Math.floor(3 + rand() * 6);
    const t = Array.from({ length: 4 }, (_, i) => (n + i) ** 2), ans = (n + 4) ** 2;
    return mcq("Find the next term of the series: " + t.join(", ") + ", ?", ans, [(n + 5) ** 2, ans + 1, ans - 1],
      `The terms are consecutive squares ${n}^2 to ${n + 3}^2, so the next term is ${n + 4}^2=${ans}.`, rand);
  }
  if (r < 0.85) {
    const a = Math.floor(1 + rand() * 6); let d = Math.floor(1 + rand() * 4); const k = Math.floor(1 + rand() * 2);
    const t = [a]; let step = d;
    for (let i = 0; i < 4; i++) { t.push(t[t.length - 1] + step); step += k; }
    const ans = t[t.length - 1] + step;
    return mcq("Find the next term of the series: " + t.join(", ") + ", ?", ans, [ans - k, ans + k, t[t.length - 1]],
      `The difference between consecutive terms increases by ${k} each time, so the next term is ${t[t.length - 1]}+${step}=${ans}.`, rand);
  }
  const start = Math.floor(65 + rand() * 8), step = Math.floor(2 + rand() * 3);
  const letters = Array.from({ length: 4 }, (_, i) => String.fromCharCode(start + i * step)), ans = String.fromCharCode(start + 4 * step);
  return mcq("Find the next letter of the series: " + letters.join(", ") + ", ?", ans,
    [String.fromCharCode(start + 3 * step), String.fromCharCode(start + 5 * step), String.fromCharCode(start + 4 * step + 1)],
    `The letters advance by ${step} places in the alphabet, so the next letter is ${ans}.`, rand);
}
