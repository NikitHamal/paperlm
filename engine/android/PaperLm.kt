// PaperLM-Tiny Android SDK (Kotlin) — PaperSetterEngine mirror of engine/web/paperlm.js. Uses ONNX Runtime Android (com.microsoft.onnxruntime:onnxruntime-android).
// NOTE: written to match the JS/Python reference rule-for-rule; compile it inside the NEBians Android module (not compiled in the training sandbox).
package com.nebians.paperlm

import ai.onnxruntime.*
import org.json.JSONObject
import java.nio.FloatBuffer
import java.nio.LongBuffer
import java.text.Normalizer
import kotlin.math.exp
import kotlin.random.Random

class ItemGenerationError(msg: String) : Exception(msg)
data class Part(val label: String, val text: String, val marks: Int)
data class Item(val kind: String, val question: String, val options: List<String>, val key: String, val explanation: String,
                val parts: List<Part>, val orParts: List<Part>, val rubric: String, val board: String, val level: String,
                val subject: String, val unit: String, val marks: Int, val type: String)

class PaperTokenizer(json: String) {
    private val pre = Regex(""" ?\\[A-Za-z]+| ?[A-Za-z\u0900-\u097F]+| ?[0-9]| ?[^\sA-Za-z0-9\u0900-\u097F]|\s+""")
    val vocab = HashMap<String, Int>(); val special = HashMap<String, Int>(); private val rank = HashMap<String, Int>()
    private val enc = Array(256) { "" }; private val dec = HashMap<Char, Int>(); val strs: Array<String?>; val isSpecial: BooleanArray; val n: Int
    init {
        val j = JSONObject(json); val v = j.getJSONObject("model").getJSONObject("vocab"); v.keys().forEach { vocab[it] = v.getInt(it) }
        val mg = j.getJSONObject("model").getJSONArray("merges")
        for (i in 0 until mg.length()) { val m = mg.get(i); rank[if (m is String) m else (m as org.json.JSONArray).let { it.getString(0) + " " + it.getString(1) }] = i }
        val at = j.getJSONArray("added_tokens"); for (i in 0 until at.length()) special[at.getJSONObject(i).getString("content")] = at.getJSONObject(i).getInt("id")
        val bs = ArrayList<Int>(); (33..126).forEach(bs::add); (161..172).forEach(bs::add); (174..255).forEach(bs::add); val cs = ArrayList(bs); var k = 0
        for (b in 0..255) if (b !in bs) { bs.add(b); cs.add(256 + k); k++ }
        for (i in bs.indices) { enc[bs[i]] = cs[i].toChar().toString(); dec[cs[i].toChar()] = bs[i] }
        n = vocab.size; strs = arrayOfNulls(n); isSpecial = BooleanArray(n)
        for ((t, id) in vocab) {
            if (special.containsKey(t)) { isSpecial[id] = true; continue }
            val bytes = ByteArray(t.length) { (dec[t[it]] ?: 0).toByte() }
            val s = try { Charsets.UTF_8.newDecoder().decode(java.nio.ByteBuffer.wrap(bytes)).toString() } catch (e: Exception) { null }
            strs[id] = if (s != null && s.all { Validator.charOk(it) }) s else null
        }
    }
    private val cache = HashMap<String, List<Int>>()
    private fun bpe(w: String): List<Int> = cache.getOrPut(w) {
        val p = w.map { it.toString() }.toMutableList()
        while (p.size > 1) { var best = -1; var bi = -1
            for (i in 0 until p.size - 1) { val r = rank[p[i] + " " + p[i + 1]]; if (r != null && (best < 0 || r < best)) { best = r; bi = i } }
            if (bi < 0) break; p[bi] = p[bi] + p[bi + 1]; p.removeAt(bi + 1) }
        p.map { vocab[it]!! } }
    fun encode(text: String): List<Int> {
        val out = ArrayList<Int>(); val tagRe = Regex("""<\|[a-z0-9_=.\-]+\|>"""); var last = 0
        fun plain(s: String) { for (m in pre.findAll(Normalizer.normalize(s, Normalizer.Form.NFC))) out += bpe(m.value.toByteArray().joinToString("") { enc[it.toInt() and 255] }) }
        for (m in tagRe.findAll(text)) { plain(text.substring(last, m.range.first)); special[m.value]?.let { out += it }; last = m.range.last + 1 }
        plain(text.substring(last)); return out
    }
}

object Validator {
    val known: Set<String> = ("frac dfrac tfrac sqrt text textbf textit mathrm mathbf mathbb mathcal mathit left right cdot times div pm mp leq geq neq approx equiv propto infty partial nabla int iint oint sum prod lim log ln sin cos tan cot sec csc sinh cosh tanh arcsin arccos arctan alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta lambda mu nu xi pi rho sigma tau phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Phi Psi Omega vec hat bar overline underline dot ddot tilde rightarrow leftarrow Rightarrow Leftarrow leftrightarrow Leftrightarrow rightleftharpoons to implies iff uparrow downarrow degree circ angle perp parallel triangle therefore because in notin subset subseteq cup cap emptyset setminus forall exists neg land lor ldots cdots dots quad qquad ce begin end hline binom choose mid lt gt le ge ne displaystyle boxed cancel underbrace overbrace operatorname ang bigg Big big Bigg lbrace rbrace langle rangle lceil rceil lfloor rfloor max min det sgn gcd lcm hbar ell Re Im prime star ast oplus otimes odot sim simeq cong mapsto arg exp deg dim ker").split(" ").toSet()
    val sorted = known.sorted()
    private const val EXTRA = "°×÷±≤≥≠≈≡∝πΩμαβγδεζηθλρστφχψωΔΘΛΣΦΨΓΠ√∞∂∫∑∈∉∪∩⊂⊆⊄→←↔⇒⇌↑↓∴∵·•′″‰℃℉Å²³⁴⁵⁶⁷⁸⁹⁰¹⁻⁺₀₁₂₃₄₅₆₇₈₉ₙ½¼¾€£₹ʹ…–—§éèêçñüöäÉ"
    fun charOk(c: Char) = c.code in 32..126 || c in EXTRA || c.code in 0x900..0x97F
    fun checkText(t: String, allowEmpty: Boolean = false): String? {
        if (t.isBlank()) return if (allowEmpty) null else "empty"
        if (!t.all(::charOk)) return "bad char"
        if (Regex("""</?[a-zA-Z][^>]*>|&[a-z]+;|&#\d+;""").containsMatchIn(t) || Regex("""\*\*|__|`|\[\[|\]\]|@mcq|@opts|:::""").containsMatchIn(t)) return "residue"
        var i = 0; val outside = StringBuilder()
        while (i < t.length) { if (t[i] == '$') { val d = if (t.startsWith("$$", i)) "$$" else "$"; val k = t.indexOf(d, i + d.length); if (k < 0) return "unbalanced $"
            val e = checkMath(t.substring(i + d.length, k)); if (e != null) return "math: $e"; i = k + d.length } else outside.append(t[i++]) }
        if (outside.any { it in "\\{}^" }) return "stray tex"; return null
    }
    fun checkMath(m: String): String? {
        val s = m.trim(); if (s.isEmpty()) return "empty math"; var depth = 0; var l = 0; var r = 0; var i = 0
        while (i < s.length) { val c = s[i]
            if (c == '\\') { val mm = Regex("""^\\([A-Za-z]+)""").find(s.substring(i)); if (mm != null) { val cmd = mm.groupValues[1]; if (cmd !in known) return "unknown cmd"; if (cmd == "left") l++; if (cmd == "right") r++; i += mm.value.length; continue }; i += 2; continue }
            if (c == '{') depth++ else if (c == '}') { depth--; if (depth < 0) return "brace underflow" }; i++ }
        return if (depth != 0 || l != r) "unbalanced" else if (Regex("""[\^_]\s*$""").containsMatchIn(s)) "dangling script" else null
    }
}

/** Incremental LaTeX/text state — identical rules to TextSt in paperlm.js */
class TextSt(var mode: String = "", var depth: Int = 0, var cmd: String? = null, var bs: Boolean = false, var lr: Int = 0, var mlen: Int = 0, var last: String = "", var raw: String = "", var exp: Int = 0, var frames: ArrayList<IntArray> = ArrayList()) {
    fun copy() = TextSt(mode, depth, cmd, bs, lr, mlen, last, raw, exp, ArrayList(frames.map { it.clone() }))
    private val two = setOf("frac", "dfrac", "tfrac", "binom")
    private val one = setOf("sqrt", "text", "textbf", "textit", "mathrm", "mathbf", "mathbb", "mathcal", "mathit", "vec", "hat", "bar", "overline", "underline", "dot", "ddot", "tilde", "operatorname", "boxed", "cancel", "ce", "underbrace", "overbrace")
    fun closed() = mode == "" && depth == 0 && cmd == null && !bs && exp == 0
    fun feed(s: String): Boolean {
        var i = 0
        while (i < s.length) { val ch = s[i]
            if (cmd != null) { if (ch.isLetter() && ch.code < 128) { cmd += ch; if (Validator.sorted.none { it.startsWith(cmd!!) }) return false; i++; continue }
                if (cmd !in Validator.known || cmd in setOf("begin", "end", "hline")) return false; if (cmd == "left") lr++ else if (cmd == "right") lr--; exp = if (cmd in two) 2 else if (cmd in one) 1 else 0; cmd = null }
            if (bs) { bs = false
                if (ch.isLetter() && ch.code < 128) { cmd = ch.toString(); if (Validator.sorted.none { it.startsWith(ch.toString()) }) return false; i++; continue }
                if (mode == "" || ch !in "\\{}%&_#,;:! |$") return false; i++; mlen++; continue }
            if (exp > 0 && ch != ' ' && ch != '{') return false
            if (ch == '$') { val dbl = i + 1 < s.length && s[i + 1] == '$'
                if (mode == "") { mode = if (dbl) "$$" else "$"; depth = 0; mlen = 0; lr = 0; last = ""; i += if (dbl) 2 else 1 }
                else { if (depth != 0 || lr != 0 || mlen == 0 || last == "^" || last == "_") return false
                    if (mode == "$$") { if (!dbl) return false; i += 2 } else { if (dbl) return false; i++ }; mode = "" }
                last = "$"; continue }
            if (mode != "") { if (ch == '\\') { bs = true; i++; continue }
                if (ch == '{') { if (exp > 0) { frames.add(intArrayOf(exp - 1, depth)); exp = 0 }; depth++ } else if (ch == '}') { depth--; if (depth < 0) return false; if (frames.isNotEmpty() && frames.last()[1] == depth) exp = frames.removeAt(frames.size - 1)[0] } else if ((ch == '^' || ch == '_') && (last == "^" || last == "_")) return false
                if (ch != ' ') { mlen++; last = ch.toString() } else if (last == "") { i++; continue }
            } else { if (ch in "\\{}^") return false; val prev = if (i > 0) s[i - 1] else raw.lastOrNull() ?: 'x'; if (ch == ' ' && prev == ' ') return false }
            i++ }
        return true
    }
}

class PaperSetterEngine(private val env: OrtEnvironment, private val session: OrtSession, private val tok: PaperTokenizer, private val units: Map<String, List<String>>, seed: Long = 1,
                        private val lexicons: Map<String, Set<String>> = emptyMap()) {
    private val rnd = Random(seed); private val L = 6; private val H = 5; private val D = 64
    private val S = listOf("pad", "bos", "end", "unit", "q", "oa", "ob", "oc", "od", "ans", "why", "part", "pm", "or", "sol").associateWith { tok.special["<|$it|>"]!! }
    private val letters = "abcd".associate { it to tok.vocab[it.toString()]!! }; private val digits = "0123456789".associate { it to tok.vocab[it.toString()]!! }
    internal class KV(val k: FloatArray, val v: FloatArray, val p: Int)

    private fun step(ids: List<Int>, kv: KV?): Pair<FloatArray, KV> {
        val p = kv?.p ?: 0
        val idT = OnnxTensor.createTensor(env, LongBuffer.wrap(LongArray(ids.size) { ids[it].toLong() }), longArrayOf(1, ids.size.toLong()))
        val sh = longArrayOf(L.toLong(), 1, H.toLong(), p.toLong(), D.toLong())
        val kT = OnnxTensor.createTensor(env, FloatBuffer.wrap(kv?.k ?: FloatArray(0)), sh); val vT = OnnxTensor.createTensor(env, FloatBuffer.wrap(kv?.v ?: FloatArray(0)), sh)
        session.run(mapOf("ids" to idT, "past_k" to kT, "past_v" to vT)).use { r ->
            val lg = (r[0] as OnnxTensor).floatBuffer; val logits = FloatArray(tok.n); lg.position(lg.limit() - tok.n); lg.get(logits)
            fun arr(t: OnnxTensor): FloatArray { val b = t.floatBuffer; val a = FloatArray(b.remaining()); b.get(a); return a }
            return logits to KV(arr(r[1] as OnnxTensor), arr(r[2] as OnnxTensor), p + ids.size) }
    }
    // The constrained-decoding state machine (sections q/oa/ob/oc/od/ans/why | part/pm/or/sol) is a line-for-line port of
    // PaperLM.tryOnce/validFn/apply in engine/web/paperlm.js; see that file for the reference implementation and tests.
    fun generateItem(board: String, level: String, subject: String, unit: String, marks: Int, type: String, rubric: Boolean = true, attempts: Int = 12): Item =
        ConstrainedDecoder({ ids, kv -> step(ids, kv as KV?) }, tok, S, letters, digits, rnd, lexicons[subject] ?: lexicons["*"]).generate(board, level, subject, unit, marks, type, rubric, attempts)

    /** Full model paper from the official blueprint of [level]. A dead-end or verifier-rejected cell is resampled with another unit; an invalid item is never emitted. */
    fun modelPaper(board: String, level: String, subject: String, rubric: Boolean = true, blueprint: List<Triple<String, String, Pair<Int, Int>>>? = null,
                   onItem: ((String, Item) -> Unit)? = null): List<Pair<String, List<Item>>> {
        val bp = blueprint ?: Blueprints.ALL[level] ?: throw ItemGenerationError("no blueprint for $level")
        val us = (units["$board|$level|$subject"] ?: listOf("General")).shuffled(rnd); var k = 0; val seen = HashSet<String>(); val out = ArrayList<Pair<String, List<Item>>>()
        for ((g, typ, mc) in bp) {
            val (marks, count) = mc; val items = ArrayList<Item>(); var fails = 0
            while (items.size < count) {
                val unit = us[k++ % us.size]; val t = if (typ == "SHORT") listOf("CONCEPTUAL", "NUMERICAL", "DERIVATION", "SHORT")[items.size % 4] else typ
                val it = try { generateItem(board, level, subject, unit, marks, t, rubric) } catch (e: ItemGenerationError) { if (++fails > 8 * count + 12) throw e; continue }
                val key = (it.question + it.options.joinToString("")).lowercase().replace(Regex("[^a-z0-9]"), "").take(90); if (!seen.add(key)) continue
                items.add(it); onItem?.invoke(g, it)
            }
            out.add(g to items)
        }
        return out
    }
}
