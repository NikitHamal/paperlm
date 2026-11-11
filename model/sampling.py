"""Sampling helpers (KV-cache) + human-readable rendering of PaperLM items."""
import re, torch

def pretty(txt):
    """Render a schema string (<|..|> tags) as an exam-paper style block."""
    m = re.search(r"<\|board=(\w+)\|><\|level=(\w+)\|><\|subj=([\w-]+)\|><\|unit\|>(.*?)<\|marks=(\d+)\|><\|type=(\w+)\|>", txt)
    head = f"[{m.group(1)} · {m.group(2)} · {m.group(3)} · {m.group(4)} · {m.group(5)}M · {m.group(6)}]" if m else ""
    body = txt.split("<|q|>", 1)[-1].replace("<|end|>", "")
    body = body.replace("<|oa|>", "\n  (a) ").replace("<|ob|>", "\n  (b) ").replace("<|oc|>", "\n  (c) ").replace("<|od|>", "\n  (d) ")
    body = body.replace("<|ans|>", "\n  ✔ Answer: ").replace("<|why|>", "\n  Why: ").replace("<|sol|>", "\n  Rubric: ")
    body = body.replace("<|or|>", "\n  — OR —").replace("<|part|>", "\n  ").replace("<|pm|>", " [") 
    body = re.sub(r"\[(\d+)(?=\s|\n|$)", r"[\1]", body)
    return (head + "\n" + body.strip()).strip()

@torch.no_grad()
def generate(model, ids, max_new=400, temperature=0.8, top_p=0.9, stop_id=2, logits_hook=None, device="cuda", rng=None):
    """ids: list[int] prompt. logits_hook(generated_ids, logits[V]) -> logits[V] (constraints). Returns generated ids (without prompt)."""
    model.eval(); model.return_cache = True
    cfg = model.cfg
    x = torch.tensor([ids], device=device)
    pk = torch.zeros(cfg.n_layers, 1, cfg.n_heads, 0, cfg.d_model // cfg.n_heads, device=device); pv = pk.clone()
    out = []
    try:
      logits, pk, pv = model(x, pk, pv)
      for _ in range(max_new):
          lg = logits[0, -1].float()
          if logits_hook is not None: lg = logits_hook(out, lg)
          if temperature <= 0: nxt = int(lg.argmax())
          else:
              p = torch.softmax(lg / temperature, -1)
              sp, si = torch.sort(p, descending=True); cs = sp.cumsum(0)
              sp[(cs - sp) > top_p] = 0; sp = sp / sp.sum()
              nxt = int(si[torch.multinomial(sp, 1, generator=rng)])
          out.append(nxt)
          if nxt == stop_id or len(ids) + len(out) >= cfg.max_seq - 1: break
          logits, pk, pv = model(torch.tensor([[nxt]], device=device), pk, pv)
    finally:
      model.return_cache = False
    return out
