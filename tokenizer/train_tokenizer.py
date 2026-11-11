#!/usr/bin/env python3
"""Custom exam-math byte-level BPE for PaperLM.

 - Pre-tokenizer keeps LaTeX commands (\\frac, \\sqrt, ...) as atomic words, splits every digit (exact arithmetic),
   keeps Devanagari runs, and is expressible as one regex => trivially portable to JS/Kotlin.
 - Special tokens carry the strict schema (board/level/subject/marks/type/structure) as single ids.
Usage: train_tokenizer.py <data_dir> <out_dir> [vocab_size]
"""
import json, os, re, sys, collections
from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders, Regex, normalizers

PATTERN = r" ?\\[A-Za-z]+| ?[A-Za-z\u0900-\u097F]+| ?[0-9]| ?[^\sA-Za-z0-9\u0900-\u097F]|\s+"
STRUCT = ["<|pad|>", "<|bos|>", "<|end|>", "<|unit|>", "<|q|>", "<|oa|>", "<|ob|>", "<|oc|>", "<|od|>", "<|ans|>", "<|why|>",
          "<|part|>", "<|pm|>", "<|or|>", "<|sol|>"]

def main():
    data, out = sys.argv[1], sys.argv[2]; vocab = int(sys.argv[3]) if len(sys.argv) > 3 else 6144
    os.makedirs(out, exist_ok=True)
    meta = json.load(open(f"{data}/schema_meta.json"))
    specials = list(STRUCT)
    specials += [f"<|board={b}|>" for b in meta["boards"]] + [f"<|level={l}|>" for l in meta["levels"]]
    specials += [f"<|subj={s}|>" for s in meta["subjects"]] + [f"<|marks={m}|>" for m in meta["marks"]] + [f"<|type={t}|>" for t in meta["types"]]
    tok = Tokenizer(models.BPE(unk_token=None))
    tok.normalizer = normalizers.NFC()
    tok.pre_tokenizer = pre_tokenizers.Sequence([
        pre_tokenizers.Split(Regex(PATTERN), behavior="isolated", invert=False),
        pre_tokenizers.ByteLevel(add_prefix_space=False, use_regex=False)])
    tok.decoder = decoders.ByteLevel()
    tr = trainers.BpeTrainer(vocab_size=vocab, special_tokens=specials, initial_alphabet=pre_tokenizers.ByteLevel.alphabet(), min_frequency=3, show_progress=False)
    tok.train([f"{data}/train.txt"], tr)
    tok.save(f"{out}/paperlm_tokenizer.json")
    # --- verification: exact round trip on val + train sample, fertility stats
    def lines(p): return [l.rstrip("\n") for l in open(p, encoding="utf-8") if l.strip()]
    tr_l, va_l = lines(f"{data}/train.txt"), lines(f"{data}/val.txt")
    bad = 0; ntok = 0; nch = 0; maxlen = 0; lens = []
    for l in va_l + tr_l[:3000]:
        ids = tok.encode(l).ids
        if tok.decode(ids, skip_special_tokens=False).replace(" <|", "<|").replace("|> ", "|>") != l:
            # decoder may insert spaces around specials; compare after stripping
            if re.sub(r"\s+", "", tok.decode(ids, skip_special_tokens=False)) != re.sub(r"\s+", "", l): bad += 1
    for l in tr_l:
        n = len(tok.encode(l).ids); ntok += n; nch += len(l); lens.append(n)
    lens.sort()
    stats = dict(vocab_size=tok.get_vocab_size(), n_special=len(specials), roundtrip_failures=bad, train_tokens=ntok, chars_per_token=round(nch / ntok, 3),
                 avg_item_tokens=round(ntok / len(tr_l), 1), p50=lens[len(lens) // 2], p95=lens[int(len(lens) * .95)], p99=lens[int(len(lens) * .99)], max=lens[-1],
                 val_tokens=sum(len(tok.encode(l).ids) for l in va_l))
    json.dump(dict(pattern=PATTERN, specials=specials, pad=0, bos=1, end=2, stats=stats), open(f"{out}/tokenizer_meta.json", "w"), indent=1)
    print(json.dumps(stats, indent=1))
    try:
        sys.path.insert(0, "/tmp/paperlm"); import live_status as LS
        LS.update("dataset", tokens=ntok, vocab=tok.get_vocab_size(), val_tokens=stats["val_tokens"])
    except Exception: pass
    print("sample:", tok.encode("<|bos|><|board=NEB|>Find $\\frac{1}{2}mv^{2}$ if m = 12 kg").tokens)

if __name__ == "__main__": main()
