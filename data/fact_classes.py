"""Closed-world fact classes for the PaperLM verified "fact" tier (aggregator).

Knowledge is data, not model output.  Each class is a table (key, value, definition) plus question forms, so:
  * answers are correct by construction (the stored value of the row),
  * distractors are wrong by construction (they are the values of other rows of the same class),
  * no numbers, names or relations are invented at generation time.

Split across modules only to keep the files reviewable:
  facts_a.py  physics
  facts_b.py  chemistry
  facts_c.py  biology
  facts_d.py  mathematics and English
  facts_e.py  social studies, computer science, economics, accountancy, nursing, general knowledge
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from facts_a import K, CLASSES as _A  # noqa: E402,F401
from facts_b import PART as _B  # noqa: E402
from facts_c import PART as _C  # noqa: E402
from facts_d import PART as _D  # noqa: E402
from facts_e import PART as _E  # noqa: E402

CLASSES = _A + _B + _C + _D + _E

if __name__ == "__main__":
    rows = sum(len(c["pairs"]) for c in CLASSES)
    print(f"{len(CLASSES)} classes, {rows} rows")
    for c in CLASSES:
        print(f"  {c['id']:26s} {len(c['pairs']):2d} rows  qb={'yes' if c['qb'] else 'no ':3s}  {c['label']}")
