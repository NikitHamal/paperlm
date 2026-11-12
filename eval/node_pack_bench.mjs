// Deterministic Node benchmark of every shipped pack (docs/packs/<id>): loads the INT8 ONNX + subject-pure tokenizer + syllabus graph + verified bank,
// plans a blueprint paper (coverage tracker, no duplicate facts), and for each slot runs FSM-constrained neural generation (K candidates, strict gate v3).
// Reports neural acceptance, verified-bank fallbacks and prints verbatim items.   usage: node eval/node_pack_bench.mjs [slots=12] [tries=3] [pack ids...]
import { createRequire } from "module"; import fs from "fs"; import path from "path"; import { fileURLToPath, pathToFileURL } from "url";
const req = createRequire((process.env.JSENV || "/tmp/jsenv") + "/x.js"), ort = req("onnxruntime-node");
const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), ".."), D = path.join(ROOT, "docs");
const { Pack, planPaper, rng32 } = await import(pathToFileURL(path.join(D, "packlm.js")).href);
const reg = JSON.parse(fs.readFileSync(path.join(D, "packs/pack_registry.json"))), N = +process.argv[2] || 12, TRIES = +process.argv[3] || 3;
const ids = process.argv.slice(4).length ? process.argv.slice(4) : reg.packs.map((p) => p.pack_id), lines = [], report = {};
for (const id of ids) {
  const dir = path.join(D, "packs", id), J = (f) => JSON.parse(fs.readFileSync(path.join(dir, f))), meta = J("pack.json");
  const pack = Pack.fromParts(ort, meta, J("tokenizer.json"), J("syllabus_graph.json")); pack.bank = fs.existsSync(path.join(dir, "bank.json")) ? J("bank.json") : [];
  pack.session = await ort.InferenceSession.create(path.join(dir, "model.onnx"), { executionProviders: ["cpu"] });
  const rand = rng32(5), t0 = Date.now(), plan = planPaper(pack.graph, [{ kind: "mcq", marks: 1, n: N }, { kind: "short", marks: 3, n: Math.max(2, N >> 2) }], 11);
  let att = 0, neural = 0, bank = 0, none = 0, rej = 0; const items = [], units = new Set(), seen = new Set(); pack.used.clear();
  for (const s of plan) {
    let it = null;
    for (let t = 0; t < TRIES && !it; t++) { const f = t ? s.unit.facts[Math.floor(rand() * s.unit.facts.length)] : s.fact; att++; const r = await pack.makeItem(s.unit, s.kind, s.marks, f, { K: 3, rand }); if (r && !r.rejected) { it = r; it.src = "neural"; neural++; } else rej++; }
    if (!it) { it = pack.bankItem(s.unit, s.kind, s.marks, rand); if (it) bank++; else none++; }
    if (it && !seen.has(it.question)) { seen.add(it.question); items.push(it); units.add(it.unit); }
  }
  const nb = pack.bank.length, bykind = { mcq: pack.bank.filter((b) => b.type === "mcq").length, short: pack.bank.filter((b) => b.type === "short").length };
  report[id] = { params: meta.params, onnx_mb: meta.onnx_mb, val_loss: meta.val_loss, slots: plan.length, neural_accepted: neural, neural_attempts: att, neural_gate_rate: +(neural / Math.max(1, att)).toFixed(3), bank_fallback: bank, empty: none,
    units_covered: `${units.size}/${pack.graph.units.length}`, duplicates: plan.length - none - items.length, bank_size: nb, bank_mcq: bykind.mcq, bank_short: bykind.short, seconds: +((Date.now() - t0) / 1000).toFixed(1) };
  lines.push(`\n##### ${id} (${meta.title}) ${JSON.stringify(report[id])}`);
  for (const it of items) lines.push(it.kind === "mcq" ? `\n[${it.unit}] MCQ <${it.src || "bank"}>\nQ. ${it.question}\n${it.options.map((o, i) => "  " + "abcd"[i] + ") " + o).join("\n")}\nKey: ${it.key}  Why: ${it.why}` : `\n[${it.unit}] ${it.marks}-mark <${it.src || "bank"}>\nQ. ${it.question}\nModel answer: ${it.answer}`);
}
console.log(JSON.stringify(report, null, 1)); const out = path.join(ROOT, "eval/results/packs"); fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(path.join(out, "bench.json"), JSON.stringify(report, null, 1)); fs.writeFileSync(path.join(out, "samples_verbatim.txt"), lines.join("\n"));
