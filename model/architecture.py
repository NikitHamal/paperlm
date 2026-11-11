"""PaperLM-Tiny: ~10M-parameter Llama/SmolLM-style decoder (RoPE + RMSNorm + SwiGLU, tied embeddings, KV-cache aware)."""
import math
from dataclasses import dataclass, asdict
import torch, torch.nn as nn, torch.nn.functional as F

@dataclass
class PaperLMConfig:
    vocab_size: int = 6144
    d_model: int = 320
    n_layers: int = 6
    n_heads: int = 5
    ffn_hidden: int = 960
    max_seq: int = 1024
    rope_theta: float = 10000.0
    dropout: float = 0.1
    norm_eps: float = 1e-5
    pad_id: int = 0

class RMSNorm(nn.Module):
    def __init__(self, d, eps):
        super().__init__(); self.eps = eps; self.weight = nn.Parameter(torch.ones(d))
    def forward(self, x):
        return x * torch.rsqrt(x.float().pow(2).mean(-1, keepdim=True) + self.eps).to(x.dtype) * self.weight

def rope_tables(head_dim, max_seq, theta):
    inv = 1.0 / (theta ** (torch.arange(0, head_dim, 2).float() / head_dim))
    t = torch.arange(max_seq).float()
    fr = torch.outer(t, inv)
    return fr.cos(), fr.sin()           # [T, D/2]

def apply_rope(x, cos, sin):            # x [B,H,S,D]; cos/sin [S,D/2]
    x1, x2 = x[..., 0::2], x[..., 1::2]
    c, s = cos[None, None], sin[None, None]
    return torch.stack((x1 * c - x2 * s, x1 * s + x2 * c), dim=-1).flatten(-2)

class Attention(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.h, self.hd = c.n_heads, c.d_model // c.n_heads
        self.qkv = nn.Linear(c.d_model, 3 * c.d_model, bias=False)
        self.o = nn.Linear(c.d_model, c.d_model, bias=False)
        self.drop = c.dropout
    def forward(self, x, cos, sin, pk=None, pv=None):
        B, S, _ = x.shape
        q, k, v = self.qkv(x).view(B, S, 3, self.h, self.hd).permute(2, 0, 3, 1, 4)
        q, k = apply_rope(q, cos, sin), apply_rope(k, cos, sin)
        if pk is not None:
            P = pk.shape[2]
            k, v = torch.cat([pk, k], 2), torch.cat([pv, v], 2)
            i = torch.arange(S, device=x.device)[:, None] + P; j = torch.arange(P + S, device=x.device)[None, :]
            y = F.scaled_dot_product_attention(q, k, v, attn_mask=(j <= i))
        else:
            y = F.scaled_dot_product_attention(q, k, v, is_causal=True, dropout_p=self.drop if self.training else 0.0)
        return self.o(y.transpose(1, 2).reshape(B, S, -1)), k, v

class SwiGLU(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.gate = nn.Linear(c.d_model, c.ffn_hidden, bias=False); self.up = nn.Linear(c.d_model, c.ffn_hidden, bias=False)
        self.down = nn.Linear(c.ffn_hidden, c.d_model, bias=False); self.drop = nn.Dropout(c.dropout)
    def forward(self, x):
        return self.drop(self.down(F.silu(self.gate(x)) * self.up(x)))

class Block(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.n1, self.attn, self.n2, self.mlp = RMSNorm(c.d_model, c.norm_eps), Attention(c), RMSNorm(c.d_model, c.norm_eps), SwiGLU(c)
        self.rd = nn.Dropout(c.dropout)
    def forward(self, x, cos, sin, pk=None, pv=None):
        a, k, v = self.attn(self.n1(x), cos, sin, pk, pv)
        x = x + self.rd(a)
        return x + self.mlp(self.n2(x)), k, v

class PaperLM(nn.Module):
    def __init__(self, c: PaperLMConfig):
        super().__init__()
        self.cfg = c
        self.emb = nn.Embedding(c.vocab_size, c.d_model)
        self.blocks = nn.ModuleList(Block(c) for _ in range(c.n_layers))
        self.norm = RMSNorm(c.d_model, c.norm_eps)
        cos, sin = rope_tables(c.d_model // c.n_heads, c.max_seq, c.rope_theta)
        self.register_buffer("cos", cos, persistent=False); self.register_buffer("sin", sin, persistent=False)
        self.apply(self._init)
        for n, p in self.named_parameters():
            if n.endswith("o.weight") or n.endswith("down.weight"): nn.init.normal_(p, 0, 0.02 / math.sqrt(2 * c.n_layers))
    def _init(self, m):
        if isinstance(m, (nn.Linear, nn.Embedding)): nn.init.normal_(m.weight, 0, 0.02)
    def n_params(self):
        return sum(p.numel() for p in self.parameters())
    def forward(self, idx, past_k=None, past_v=None):
        """idx [B,S]. Without cache -> logits [B,S,V]. With cache (tensors [L,B,H,P,D]) -> (logits, new_k, new_v)."""
        S = idx.shape[1]
        P = 0 if past_k is None else past_k.shape[3]
        cos, sin = self.cos[P:P + S], self.sin[P:P + S]
        x = self.emb(idx); ks, vs = [], []
        for i, b in enumerate(self.blocks):
            x, k, v = b(x, cos, sin, None if past_k is None else past_k[i], None if past_v is None else past_v[i])
            ks.append(k); vs.append(v)
        logits = F.linear(self.norm(x), self.emb.weight)
        if past_k is None and not getattr(self, "return_cache", False): return logits
        return logits, torch.stack(ks), torch.stack(vs)

def build(cfg_dict=None):
    c = PaperLMConfig(**(cfg_dict or {}))
    return PaperLM(c)

if __name__ == "__main__":
    m = build(); print("params:", m.n_params(), asdict(m.cfg))
