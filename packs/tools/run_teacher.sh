#!/bin/bash
cd /work/paperlm && bash packs/tools/build_all.sh && python3 packs/tools/teacher.py ${@:-bio12 phy11 bio11 phy12 chem11 chem12}
