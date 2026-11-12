package ai.paperlm

import org.json.JSONArray
import org.json.JSONObject
import kotlin.math.exp
import kotlin.math.ln

/**
 * Kotlin twin of docs/packlm.js: FSM grammar-constrained decoding + grounding gate + strict gate v3 + best-of-K rerank for ONE subject pack.
 * Backend-agnostic: pass any `feed(ids) -> logits of the last token` (TflitePackRunner::feed or an ORT wrapper).  NOT compiled in CI yet.
 */
class PackMeta(j: JSONObject) {
    val id = j.getString("pack_id"); val vocab = j.getInt("vocab"); val maxSeq = j.getInt("max_seq")
    val layers = j.getInt("layers"); val heads = j.getInt("heads"); val headDim = j.getInt("head_dim")
    val specials: Map<String, Int> = j.getJSONObject("specials").let { o -> o.keys().asSequence().associateWith { o.getInt(it) } }
    /** segment order per kind: (name, closing tag, min chars, max chars) */
    val fsm: Map<String, List<Seg>> = j.getJSONObject("fsm").let { o -> o.keys().asSequence().associateWith { k -> o.getJSONArray(k).let { a -> (0 until a.length()).map { i -> a.getJSONArray(i).let { Seg(it.getString(0), it.getString(1), it.getInt(2), it.getInt(3)) } } } } }
}
data class Seg(val name: String, val closer: String, val lo: Int, val hi: Int)

/** per-token decoded text + brace/dollar deltas, built once from tokenizer.json (byte-level BPE) */
class TokTable(tokJson: JSONObject, val vocab: Int) {
    val strs = arrayOfNulls<String>(vocab); val open = IntArray(vocab); val close = IntArray(vocab); val dollar = IntArray(vocab); val isSpecial = BooleanArray(vocab)
    init {
        val bs = (33..126).toMutableList().apply { addAll(161..172); addAll(174..255) }; val cs = bs.toMutableList(); var n = 0
        for (b in 0..255) if (b !in bs) { bs.add(b); cs.add(256 + n); n++ }
        val dec = HashMap<Char, Int>().apply { bs.forEachIndexed { i, b -> put(cs[i].toChar(), b) } }
        val sp = tokJson.getJSONArray("added_tokens").let { a -> (0 until a.length()).map { a.getJSONObject(it).getString("content") }.toSet() }
        val v = tokJson.getJSONObject("model").getJSONObject("vocab")
        for (t in v.keys()) {
            val id = v.getInt(t); if (id >= vocab) continue
            if (t in sp) { isSpecial[id] = true; continue }
            val bytes = ByteArray(t.length) { (dec[t[it]] ?: 63).toByte() }; val s = String(bytes, Charsets.UTF_8)
            if (s.any { it.code < 32 || it.code > 126 && it !in "°±×÷²³µΩ→≈≤≥−·λμπσΔ" }) continue   // mirrors the web table: printable only
            strs[id] = s; for (c in s) when (c) { '{' -> open[id]++; '}' -> close[id]++; '$' -> dollar[id]++ }
        }
    }
}

class Fsm(private val t: TokTable, private val meta: PackMeta, kind: String) {
    private val spec = meta.fsm.getValue(kind); private var k = 0; private var text = StringBuilder(); private var depth = 0; private var dol = 0
    val ids = ArrayList<Int>(); val segs = ArrayList<String>(); var done = false; private set
    /** legal next tokens only: the closing tag once min length is met and braces/$ balance; otherwise printable tokens that never over-close */
    fun mask(): BooleanArray {
        val m = BooleanArray(t.vocab); val s = spec[k]; val closer = meta.specials.getValue(s.closer); val n = text.length; val bal = depth == 0 && dol % 2 == 0
        if ((n >= s.hi && bal) || n >= s.hi + 80) { m[closer] = true; return m }
        for (i in 0 until t.vocab) { val st = t.strs[i] ?: continue; if (depth + t.open[i] - t.close[i] < 0) continue; if (n == 0 && (st.startsWith(" ") || st.isBlank())) continue; m[i] = true }
        if (n >= s.lo && bal) m[closer] = true; return m
    }
    fun feed(id: Int) {
        ids.add(id)
        if (t.isSpecial[id]) { segs.add(text.toString().trim()); k++; text = StringBuilder(); depth = 0; dol = 0; if (k >= spec.size) done = true; return }
        text.append(t.strs[id]); depth += t.open[id] - t.close[id]; dol += t.dollar[id]
    }
}

object PackGate {
    private val STOP = "the of and a an to in is are was were be by for with on as at from that this which it its or their these those can has have into than then also not one two more most each other".split(" ").toSet()
    private val OPEN = Regex("^(what|which|why|how|when|where|who|name|define|state|explain|describe|write|differentiate|distinguish|give|calculate|find|list|mention|compare|justify|derive|prove|identify|discuss|illustrate|is|are|does|do)\\b", RegexOption.IGNORE_CASE)
    fun cw(s: String) = Regex("[a-z][a-z0-9]{2,}").findAll(s.lowercase()).map { it.value }.filter { it !in STOP }.toList()
    private fun frac(ws: List<String>, s: Set<String>) = ws.count { it in s }.toDouble() / maxOf(1, ws.size)
    private fun rep3(t: String): Boolean { val w = t.lowercase().split(Regex("\\s+")); val seen = HashSet<String>(); for (i in 0 until w.size - 2) if (!seen.add(w.subList(i, i + 3).joinToString(" "))) return true; return false }
    private fun distinct(t: String): Double { val w = t.lowercase().split(Regex("\\s+")).filter { it.isNotEmpty() }; return if (w.isEmpty()) 0.0 else w.toSet().size.toDouble() / w.size }

    /** returns (score, ansGround, distinct, homog) like grounding() in packlm.js */
    fun grounding(segs: List<String>, kind: String, anchor: String, unitTerms: Set<String>): DoubleArray {
        val a = cw(anchor).toSet()
        if (kind == "mcq") {
            if (segs.size < 6) return doubleArrayOf(0.0, 0.0, 0.0, 0.0)
            val ans = segs[0]; val q = segs[1]; val ds = listOf(segs[2], segs[3], segs[4]); val why = segs[5]; val al = anchor.lowercase()
            val ag = frac(cw(ans).ifEmpty { listOf("_") }, a); val qg = cw(q).count { it in a || it in unitTerms }.toDouble() / maxOf(1, cw(q).size)
            val dis = if ((ds + ans).map { it.lowercase() }.toSet().size == 4 && ds.all { al.indexOf(it.lowercase()) < 0 || it.length < 4 }) 1.0 else 0.0
            val hom = if (ds.all { val r = (it.length + 3.0) / (ans.length + 3); r in 0.3..3.5 }) 1.0 else 0.0
            val sc = 0.35 * ag + 0.2 * qg + 0.2 * dis + 0.1 * frac(cw(why), a) + 0.05 * (if (al.contains(q.lowercase())) 0 else 1) + 0.1 * hom
            return doubleArrayOf(sc, ag, dis, hom)
        }
        if (segs.size < 2) return doubleArrayOf(0.0, 0.0, 1.0, 1.0)
        val ag = frac(cw(segs[0]).ifEmpty { listOf("_") }, a); val qg = cw(segs[1]).count { it in a || it in unitTerms }.toDouble() / maxOf(1, cw(segs[1]).size)
        return doubleArrayOf(0.6 * ag + 0.4 * qg, ag, 1.0, 1.0)
    }
    fun pass(g: DoubleArray, kind: String) = g[0] >= 0.85 && (kind == "short" || (g[2] > 0 && g[3] > 0 && g[1] >= 0.8))

    /** strict gate v3 (same rules as strictOK in packlm.js) */
    fun strictOk(kind: String, segs: List<String>, anchor: String, lp: Double, lpMin: Double = -1.6): Boolean {
        val ans = segs[0]; val q = segs[1]; val a = cw(anchor).toSet(); val qc = cw(q)
        if (!OPEN.containsMatchIn(q.trim()) || qc.size < 3 || qc.count { it in a } < 2) return false
        if (kind == "mcq" && (q.length < 20 || (q.lowercase().contains(ans.lowercase()) && ans.length > 3))) return false
        for (t in segs) { if (rep3(t) || distinct(t) < 0.55 || Regex("(\\$\\s*\\$)|\\s{2,}|([a-z])\\2{3,}").containsMatchIn(t)) return false; if (t.length > 25 && !Regex("[a-z]{3}", RegexOption.IGNORE_CASE).containsMatchIn(t)) return false }
        return lp >= lpMin
    }
}

data class Candidate(val segs: List<String>, val lp: Double, val done: Boolean)

class PackEngine(val meta: PackMeta, val tok: PaperTokenizer, val table: TokTable, private val feed: (IntArray) -> FloatArray, private val reset: () -> Unit) {
    /** best-of-K constrained sampling with copy-bias toward anchor tokens; the caller reranks with PackGate */
    fun sample(unit: String, kind: String, marks: Int, anchor: String, k: Int = 3, temp: Float = 0.75f, topP: Float = 0.92f, beta: Float = 1f, rnd: java.util.Random = java.util.Random()): List<Candidate> {
        val prompt = "<|bos|><|pack=${meta.id}|><|type=$kind|><|marks=$marks|><|unit|>$unit<|book|>$anchor<|ans|>"; val bias = FloatArray(table.vocab); tok.encode(anchor).forEach { if (it < bias.size) bias[it] = beta }
        val out = ArrayList<Candidate>()
        repeat(k) {
            reset(); var lg = feed(tok.encode(prompt).toIntArray()); val f = Fsm(table, meta, kind); var lp = 0.0
            var step = 0
            while (!f.done && step++ < 420) {
                val m = f.mask(); val l = FloatArray(table.vocab) { if (m[it]) lg[it] + bias[it] else -1e30f }; val mx = l.max()
                val idx = l.indices.filter { l[it] > -1e29f }.sortedByDescending { l[it] }; val p = idx.map { exp(((l[it] - mx) / temp).toDouble()) }; val z = p.sum()
                var cum = 0.0; var cut = idx.size; for (j in idx.indices) { cum += p[j] / z; if (cum >= topP) { cut = j + 1; break } }
                var r = rnd.nextDouble() * p.take(cut).sum(); var pick = idx[0]; for (j in 0 until cut) { r -= p[j]; if (r <= 0) { pick = idx[j]; break } }
                val gm = lg.max(); lp += (lg[pick] - gm) - ln(lg.sumOf { exp((it - gm).toDouble()) })
                f.feed(pick); if (!f.done) lg = feed(intArrayOf(pick))
            }
            out.add(Candidate(f.segs.toList(), lp / maxOf(1, f.ids.size), f.done))
        }
        return out
    }
    /** rerank candidates by grounding + 0.02*avg logprob; returns the winner only if both gates pass (else null -> caller falls back to bank.json) */
    fun best(cands: List<Candidate>, kind: String, anchor: String, unitTerms: Set<String>): Candidate? {
        val s = cands.filter { it.done }.map { it to PackGate.grounding(it.segs, kind, anchor, unitTerms) }.maxByOrNull { it.second[0] + 0.02 * it.first.lp } ?: return null
        return if (PackGate.pass(s.second, kind) && PackGate.strictOk(kind, s.first.segs, anchor, s.first.lp)) s.first else null
    }
}
