// LM-tier yield test: for N random (subject,unit) with facts, sample 4 grounded attempts each and report strict-gate pass rate. usage: node lm_tier_test.mjs model beta N
import { createRequire } from "module"; import fs from "fs"; import path from "path"; import { fileURLToPath, pathToFileURL } from "url";
const req = createRequire("/tmp/jsenv/x.js"); const ort = req("onnxruntime-node"); const D = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "docs"); const J = (f) => JSON.parse(fs.readFileSync(path.join(D, "model", f), "utf8"));
const { PaperLM } = await import(pathToFileURL(path.join(D, "paperlm.js")).href); const { gate } = await import(path.join(D, "ground.js"));
const model = fs.readFileSync(process.argv[2]); const beta = +process.argv[3], N = +process.argv[4] || 25;
const eng = await PaperLM.create({ ort, model, tokenizer: J("tokenizer.json"), syllabus: J("syllabus.json"), seed: 11, lexicon: J("lexicon.json"), providers: ["cpu"] }); const bank = J("bank.json");
const cells = []; for (const [k, f] of Object.entries(bank.facts)) for (const u of Object.keys(f)) if (f[u].length) cells.push([k, u, f[u]]);
let tries = 0, pass = 0, valid = 0, shown = []; const rej = {};
for (let i = 0; i < N; i++) {
  const [k, u, fs_] = cells[Math.floor(eng.rand() * cells.length)]; const [b, l, s] = k.split("|"); const anc = fs_[Math.floor(eng.rand() * fs_.length)]; const mcq = i % 2 === 0;
  for (let a = 0; a < 4; a++) { tries++; let it; try { it = await eng.generateItem({ board: b, level: l, subject: s, unit: u, marks: mcq ? 1 : 5, type: mcq ? "MCQ" : "SHORT", attempts: 1, temperature: 0.7 + 0.05 * a, anchor: anc, biasBeta: beta }); } catch { continue; }
    valid++; const g = gate(it, anc); if (g.ok) { pass++; if (shown.length < 4) shown.push({ anchor: anc, q: it.question, o: it.options, k: it.key, e: it.explanation, r: it.rubric }); break; } for (const x of g.issues) rej[x.replace(/:.*/, "")] = (rej[x.replace(/:.*/, "")] || 0) + 1; }
}
console.log(JSON.stringify({ beta, tries, structurally_valid: valid, gate_pass: pass, prompts: N, rej }));
if (process.env.SHOW) console.log(JSON.stringify(shown, null, 1));
