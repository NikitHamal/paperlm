// Deterministic Node verification of every shipped pack: loads docs/packs/<id> (ONNX INT8 + tokenizer + graph), runs FSM decoding + grounding gate,
// prints verbatim items.  usage: node eval/node_pack_test.mjs [n_per_pack=6] [pack ids...]   (onnxruntime-node via /tmp/jsenv)
import { createRequire } from "module"; import fs from "fs"; import path from "path"; import { fileURLToPath, pathToFileURL } from "url";
const req = createRequire((process.env.JSENV || "/tmp/jsenv") + "/x.js"), ort = req("onnxruntime-node");
const D = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "docs"), { Pack, planPaper, rng32 } = await import(pathToFileURL(path.join(D, "packlm.js")).href);
const reg = JSON.parse(fs.readFileSync(path.join(D, "packs/pack_registry.json"))), N = +process.argv[2] || 6, ids = process.argv.slice(3).length ? process.argv.slice(3) : reg.packs.map((p) => p.pack_id), report = {}, lines = [];
for (const id of ids) {
  const dir = path.join(D, "packs", id), J = (f) => JSON.parse(fs.readFileSync(path.join(dir, f))), meta = J("pack.json"), pack = Pack.fromParts(ort, meta, J("tokenizer.json"), J("syllabus_graph.json"));
  pack.session = await ort.InferenceSession.create(path.join(dir, "model.onnx"), { executionProviders: ["cpu"] }); const rand = rng32(5), t0 = Date.now(); let att = 0, ok = 0, sc = 0; const items = [];
  const plan = planPaper(pack.graph, [{ kind: "mcq", marks: 1, n: N }, { kind: "short", marks: 3, n: Math.max(1, N >> 2) }], 11);
  for (const s of plan) { for (let t = 0; t < 5; t++) { const f = t ? s.unit.facts[Math.floor(rand() * s.unit.facts.length)] : s.fact; att++; const it = await pack.makeItem(s.unit, s.kind, s.marks, f, { K: 4, rand }); if (it && !it.rejected) { ok++; sc += it.score; items.push(it); break; } } }
  report[id] = { params: meta.params, onnx_mb: meta.onnx_mb, items: plan.length, accepted: items.length, gate_attempts: att, gate_accept_rate: +(ok / att).toFixed(3), mean_grounding: +(sc / Math.max(1, ok)).toFixed(3), seconds: (Date.now() - t0) / 1000 };
  lines.push(`\n##### ${id} (${meta.title}) ${JSON.stringify(report[id])}`);
  for (const it of items) lines.push(it.kind === "mcq" ? `\n[${it.unit}] MCQ (grounding ${it.score.toFixed(2)})\nQ. ${it.question}\n${it.options.map((o, i) => "  " + "abcd"[i] + ") " + o).join("\n")}\nKey: ${it.key}) -- ${it.why}\nAnchor: ${it.anchor}` : `\n[${it.unit}] ${it.marks}-mark (grounding ${it.score.toFixed(2)})\nQ. ${it.question}\nModel answer: ${it.answer}\nAnchor: ${it.anchor}`);
}
console.log(JSON.stringify(report, null, 1)); fs.mkdirSync(path.join(D, "..", "eval/results/packs"), { recursive: true }); fs.writeFileSync(path.join(D, "..", "eval/results/packs/node_samples_verbatim.txt"), lines.join("\n")); fs.writeFileSync(path.join(D, "..", "eval/results/packs/node_report.json"), JSON.stringify(report, null, 1));
