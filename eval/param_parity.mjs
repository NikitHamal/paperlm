// Python <-> JS parity: re-instantiate each template with identical variables and print answer / stem / steps as JSON.
import fs from "fs"; import path from "path"; import { fileURLToPath, pathToFileURL } from "url";
const D = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "docs"); const { Parametric } = await import(path.join(D, "parametric.js"));
const pm = new Parametric(JSON.parse(fs.readFileSync(path.join(D, "model/templates.json"), "utf8"))); const rand = () => 0.5;
const out = JSON.parse(fs.readFileSync(process.argv[2], "utf8")).map((c) => { const i = pm.instantiate(pm.byId[c.id], rand, c.vars); if (!i) return null; const r = pm.render(i, rand); return { ans: i.ans, stem: r.stem, steps: r.steps }; });
console.log(JSON.stringify(out));
