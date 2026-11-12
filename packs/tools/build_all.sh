#!/bin/bash
cd /work/paperlm
for p in ${@:-bio12 phy11 bio11 phy12 chem11 chem12}; do python3 packs/tools/build_pack.py $p /tmp/packs/$p 2>&1 | tail -3; done
python3 - <<'P'
import json
g=json.load(open("/tmp/packs/bio12/syllabus_graph.json"))
for u in g["units"]: print(u["name"],len(u["facts"]),u["share"])
P
