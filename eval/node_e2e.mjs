// End-to-end Node test of the browser stack: ONNX LM + concept-grounded composer + strict gate + parametric engine.
// usage: node eval/node_e2e.mjs [model.onnx] [n] [lmBudget]   (needs onnxruntime-node resolvable from NODE_PATH or /tmp/jsenv)
import { createRequire } from "module"; import fs from "fs"; import path from "path"; import { fileURLToPath } from "url";
const req = createRequire(process.env.JSENV ? process.env.JSENV + "/x.js" : "/tmp/jsenv/x.js"); const ort = req("onnxruntime-node");
const D = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "docs"); const J = (f) => JSON.parse(fs.readFileSync(path.join(D, "model", f), "utf8"));
const { PaperLM, BLUEPRINTS } = await import(path.join(D, "paperlm.js")); const { Composer } = await import(path.join(D, "composer.js"));
const model = fs.readFileSync(process.argv[2] || path.join(D, "model/model.onnx")); const N = +process.argv[3] || 40, BUD = +(process.argv[4] ?? 6);
const eng = await PaperLM.create({ ort, model, tokenizer: J("tokenizer.json"), syllabus: J("syllabus.json"), seed: 7, lexicon: J("lexicon.json"), providers: ["cpu"] });
const comp = new Composer(eng, J("bank.json"), J("templates.json")); const cat = J("catalog.json"); const keys = Object.keys(cat);
const tiers = {}, subs = {}; let ok = 0, fail = 0; const samples = []; const t0 = Date.now();
for (let i = 0; i < N; i++) {
  const e = cat[keys[Math.floor(eng.rand() * keys.length)]]; const subj = Object.keys(e.subjects)[Math.floor(eng.rand() * Object.keys(e.subjects).length)]; const us = e.subjects[subj].units; const unit = us[Math.floor(eng.rand() * us.length)];
  const types = ["MCQ", "MCQ", "SHORT", "NUMERICAL", "OR", "CONCEPTUAL"]; const type = types[i % types.length]; const marks = type === "MCQ" ? 1 : type === "OR" ? 8 : type === "NUMERICAL" ? 4 : 5;
  try { const it = await comp.item({ board: e.board, level: e.level, subject: subj, unit, marks, type, lmBudget: BUD }); tiers[it.provenance.tier] = (tiers[it.provenance.tier] || 0) + 1; ok++; if (samples.length < 12 && (i % 3 === 0 || it.provenance.tier === "lm")) samples.push({ tier: it.provenance.tier, subject: subj, unit, type, item: it }); }
  catch (err) { fail++; console.log("FAIL", e.board, e.level, subj, unit, type, err.message); }
}
console.log(JSON.stringify({ n: N, ok, fail, tiers, stats: comp.stats, seconds: (Date.now() - t0) / 1000 }, null, 1));
for (const s of samples.slice(0, +process.env.SHOW || 6)) console.log("\n###", s.tier, s.subject, "|", s.unit, "|", s.type, "\n" + JSON.stringify(s.item, null, 1).slice(0, 900));
