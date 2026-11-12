"""PaperLM MoLab daemon: 60s keep-alive pings + 2s live status merge for the Marimo dashboard.

Launched detached (setsid/nohup) so it survives notebook cell re-runs and kernel restarts.
 - every 60s : HTTP-pings the marimo server (local + public sandbox URL), touches a heartbeat file,
               and runs a tiny CUDA op so the VM never looks idle.
 - every 2s  : samples nvidia-smi and merges /tmp/paperlm/status_*.json parts into
               /tmp/paperlm_live_status.json (atomic write).
"""
import glob, json, os, subprocess, threading, time, urllib.request

PUBLIC_URL = os.environ.get("MOLAB_PUBLIC_URL", "https://sb-84ba1da1dc9d55f9.sb.molab.run/")
OUT = "/tmp/paperlm_live_status.json"
PARTS = "/tmp/paperlm"
T0 = time.time()
os.makedirs(PARTS, exist_ok=True)
open("/tmp/paperlm/keepalive.pid", "w").write(str(os.getpid()))

def ping(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "paperlm-keepalive"}), timeout=15) as r:
            return r.status
    except Exception as e:  # noqa
        return str(e)[:60]

def gpu_sample():
    try:
        o = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10).stdout.strip().split(",")
        n, mu, mt, ut, tp, pw = [x.strip() for x in o]
        return dict(name=n, vram_used_mb=float(mu), vram_total_mb=float(mt), util=float(ut), temp=float(tp), power_w=float(pw))
    except Exception as e:  # noqa
        return dict(name="n/a", vram_used_mb=0, vram_total_mb=0, util=0, temp=0, power_w=0, err=str(e)[:80])

hb = {"count": 0, "last": None, "last_status": None}

def keepalive_loop():
    while True:
        s1 = ping("http://127.0.0.1:8080/health")
        s2 = ping(PUBLIC_URL + "health")
        try:
            import torch
            if torch.cuda.is_available():
                x = torch.randn(256, 256, device="cuda"); (x @ x).sum().item()
        except Exception:
            pass
        hb["count"] += 1; hb["last"] = time.time(); hb["last_status"] = f"local={s1} public={s2}"
        open("/tmp/paperlm/heartbeat.txt", "w").write(f"{time.ctime()} count={hb['count']} {hb['last_status']}\n")
        time.sleep(60)

def merge_loop():
    while True:
        try:
            doc = {"updated": time.time(), "uptime_s": time.time() - T0, "gpu": gpu_sample(), "keepalive": dict(hb)}
            for p in sorted(glob.glob(PARTS + "/status_*.json")):
                try:
                    doc[os.path.basename(p)[7:-5]] = json.load(open(p))
                except Exception:
                    pass
            tmp = OUT + ".tmp"; json.dump(doc, open(tmp, "w")); os.replace(tmp, OUT)
        except Exception:
            pass
        time.sleep(2)

threading.Thread(target=keepalive_loop, daemon=True).start()
merge_loop()
