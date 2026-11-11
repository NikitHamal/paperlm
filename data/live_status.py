"""Tiny helper used by every PaperLM pipeline stage on the MoLab VM to publish live telemetry."""
import json, os, time
PARTS = "/tmp/paperlm"
os.makedirs(PARTS, exist_ok=True)

def update(section: str, **kw):
    """Merge keys into section file (stage/dataset/train/samples/eval)."""
    p = f"{PARTS}/status_{section}.json"
    try:
        d = json.load(open(p))
    except Exception:
        d = {}
    d.update(kw); d["_t"] = time.time()
    tmp = p + ".tmp"; json.dump(d, open(tmp, "w")); os.replace(tmp, p)

def append(section: str, key: str, item, keep=2000):
    p = f"{PARTS}/status_{section}.json"
    try:
        d = json.load(open(p))
    except Exception:
        d = {}
    d.setdefault(key, []).append(item); d[key] = d[key][-keep:]; d["_t"] = time.time()
    tmp = p + ".tmp"; json.dump(d, open(tmp, "w")); os.replace(tmp, p)
