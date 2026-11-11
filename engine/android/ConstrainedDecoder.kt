// Constrained decoder for PaperSetterEngine (Kotlin port of PaperLM.tryOnce / validFn / apply / finalize in engine/web/paperlm.js).
package com.nebians.paperlm

import kotlin.math.exp
import kotlin.random.Random

internal class ConstrainedDecoder(
    private val stepFn: (List<Int>, Any?) -> Pair<FloatArray, Any>, private val tok: PaperTokenizer, private val S: Map<String, Int>,
    private val letters: Map<Char, Int>, private val digits: Map<Char, Int>, private val rnd: Random, private val lexicon: Set<String>? = null) {
    private val caps = mapOf("q" to 420, "oa" to 120, "ob" to 120, "oc" to 120, "od" to 120, "part" to 320, "why" to 320, "sol" to 700)
    private val minLen = mapOf("q" to 12, "part" to 6, "why" to 8, "sol" to 12)
    private val nextMcq = mapOf("q" to "<|oa|>", "oa" to "<|ob|>", "ob" to "<|oc|>", "oc" to "<|od|>", "od" to "<|ans|>")
    private val structIds = S.values.toSet()
    private fun norm(s: String) = s.lowercase().replace(Regex("[^a-z0-9\u0900-\u097F]+"), "")

    private class St(val typ: String, val marks: Int, val wantSol: Boolean) {
        val mcq = typ == "MCQ"; var sec = "q"; var t = TextSt(); val opts = ArrayList<String>(); var key = ""; var why = ""; var q = ""
        val parts = ArrayList<Array<Any>>(); val alt = ArrayList<Array<Any>>(); var inAlt = false; var pm = ""; var sol = ""; var done = false
        val seen4 = HashSet<List<Int>>(); val recent = ArrayList<Int>()
        fun cur() = if (inAlt) alt else parts
    }
    private fun marksOk(st: St): Boolean { for (ps in listOf(st.parts, st.alt)) if (ps.isNotEmpty() && ps.any { it[2] as Int > 0 } && (!ps.all { it[2] as Int > 0 } || ps.sumOf { it[2] as Int } != st.marks)) return false; return true }
    private fun allowed(st: St): List<String> {
        val out = ArrayList<String>()
        if (st.mcq) { nextMcq[st.sec]?.let { out += it }; if (st.sec == "why") out += "<|end|>" }
        else if (st.sec == "q" || st.sec == "part") { val ps = st.cur()
            if (st.sec == "part" && (ps.size == 1 || ps.dropLast(1).all { it[2] as Int > 0 })) out += "<|pm|>"; out += "<|part|>"
            if (st.typ == "OR" && !st.inAlt) out += "<|or|>" else out += if (st.wantSol) "<|sol|>" else "<|end|>" }
        else if (st.sec == "sol") out += "<|end|>"
        return out
    }
    private fun valid(st: St): (Int) -> Boolean {
        val dig = digits.values.toSet()
        if (st.sec == "ans") return { it in letters.values }
        if (st.sec == "pm") { if (st.pm.length >= 2) return { false }; return { i -> i in dig && !(st.pm.isEmpty() && i == digits['0']) && (st.pm + digits.entries.first { e -> e.value == i }.key).toInt() <= st.marks } }
        if (st.sec == "or") return { it == S["part"] }
        val cap = caps[st.sec] ?: 300; val raw = st.t.raw; val ok = HashSet<Int>()
        if (st.t.closed() && raw.trim().length >= (minLen[st.sec] ?: 1)) for (name in allowed(st)) {
            val nm = name.removePrefix("<|").removeSuffix("|>")
            if (!st.mcq && nm in listOf("part", "or", "sol", "end") && !marksOk(st)) continue
            if (st.mcq && name in listOf("<|ob|>", "<|oc|>", "<|od|>", "<|ans|>")) { val n = norm(raw); if (n.isEmpty() || st.opts.any { norm(it) == n }) continue }
            ok += tok.special[name]!! }
        val over = raw.length >= cap
        return { i -> if (i in ok) true else if (tok.isSpecial[i] || tok.strs[i] == null || over) false else if (raw.length + tok.strs[i]!!.length > cap + 12) false else st.t.copy().feed(tok.strs[i]!!) }
    }
    private fun closeSeg(st: St) { val txt = st.t.raw.trim()
        when (st.sec) { "q" -> st.q = txt; "oa", "ob", "oc", "od" -> st.opts += txt; "why" -> st.why = txt; "sol" -> st.sol = txt
            "part" -> st.cur().last()[1] = txt; "pm" -> { if (st.pm.isNotEmpty()) st.cur().last()[2] = st.pm.toInt(); st.pm = "" } } }
    private fun apply(st: St, tid: Int) {
        if (st.sec == "ans") { st.key = letters.entries.first { it.value == tid }.key.toString(); st.sec = "ans_done"; return }
        if (st.sec == "pm" && tid in digits.values) { st.pm += digits.entries.first { it.value == tid }.key; return }
        if (tid in structIds) { val name = S.entries.first { it.value == tid }.key; closeSeg(st); if (name == "end") { st.done = true; return }; st.t = TextSt()
            when (name) { "oa", "ob", "oc", "od", "ans", "why", "sol" -> st.sec = name; "part" -> { st.sec = "part"; st.pm = ""; st.cur().add(arrayOf("", "", 0)) }
                "pm" -> { st.sec = "pm"; st.pm = "" }; "or" -> { st.sec = "or"; st.inAlt = true } }; return }
        val s = tok.strs[tid]!!; st.t.feed(s); st.t.raw += s
    }
    private fun sample(lg: FloatArray, valid: (Int) -> Boolean, temp: Float, topP: Float, st: St): Int? {
        val idx = lg.indices.sortedByDescending { lg[it] }; var cand = idx.take(96).filter(valid)
        if (cand.isEmpty()) cand = idx.drop(96).asSequence().filter(valid).take(8).toList(); if (cand.isEmpty()) return null
        cand = cand.filter { c -> val g = st.recent.takeLast(3) + c; !(g.size == 4 && g in st.seen4) }.ifEmpty { cand }
        val mx = cand.maxOf { lg[it] }; val w = cand.map { exp(((lg[it] - mx) / maxOf(temp, 1e-4f)).toDouble()) }; val z = w.sum()
        val o = cand.indices.sortedByDescending { w[it] }; var cs = 0.0; val sel = ArrayList<Int>()
        for (i in o) { sel += i; cs += w[i] / z; if (cs >= topP) break }
        var u = rnd.nextDouble() * sel.sumOf { w[it] }; for (i in sel) { u -= w[i]; if (u <= 0) return cand[i] }; return cand[sel.last()]
    }
    private fun tryOnce(hid: List<Int>, typ: String, marks: Int, wantSol: Boolean, temp: Float): St? {
        val st = St(typ, marks, wantSol); var (lg, kv) = stepFn(hid + S["q"]!!, null); var n = 0
        while (!st.done && n < 520 && hid.size + n < 1020) {
            val tid: Int? = when {
                st.sec == "ans_done" -> S[if (wantSol) "why" else "end"]
                st.sec == "pm" && st.pm.isNotEmpty() -> { val v = valid(st); val tot = st.cur().dropLast(1).sumOf { it[2] as Int } + st.pm.toInt()
                    val names = if (tot < marks) listOf("part") else if (tot == marks) (if (typ == "OR" && !st.inAlt) listOf("or") else listOf(if (wantSol) "sol" else "end")) else emptyList()
                    val opts = names.map { S[it]!! }.toSet(); sample(lg, { it in opts || v(it) }, temp, 0.92f, st) }
                else -> sample(lg, valid(st), temp, 0.92f, st) }
            if (tid == null) return null; apply(st, tid); st.recent += tid; if (st.recent.size >= 4) st.seen4 += st.recent.takeLast(4); n++
            if (st.done) break; val r = stepFn(listOf(tid), kv); lg = r.first; kv = r.second }
        return if (st.done) st else null
    }
    fun generate(board: String, level: String, subject: String, unit: String, marks: Int, type: String, rubric: Boolean, attempts: Int): Item {
        val sid = if (tok.special.containsKey("<|subj=$subject|>")) "<|subj=$subject|>" else "<|subj=general|>"
        val hid = tok.encode("<|bos|><|board=$board|><|level=$level|>$sid<|unit|>$unit<|marks=$marks|><|type=$type|>")
        for (a in 0 until attempts) {
            val st = tryOnce(hid, type, marks, rubric, minOf(1.1f, 0.75f + 0.03f * a)) ?: continue
            fun mk(ps: List<Array<Any>>) = ps.mapIndexed { i, p -> Part(('a' + i).toString(), p[1] as String, p[2] as Int) }
            if (st.mcq) { if (st.opts.size != 4 || st.key !in listOf("a", "b", "c", "d")) continue
                if (listOf(st.q) .plus(st.opts).plus(st.why).any { Validator.checkText(it, true) != null } || st.opts.map(::norm).toSet().size != 4) continue
                val it = Verifier.clean(Item("mcq", st.q, st.opts, st.key, st.why, emptyList(), emptyList(), "", board, level, subject, unit, marks, type))
                if (Verifier.verify(it, unit, lexicon).isNotEmpty()) continue; return it }
            if (!marksOk(st) || (type == "OR" && st.alt.isEmpty())) continue
            val p = mk(st.parts); val al = mk(st.alt); if ((p + al).any { it.text.isEmpty() }) continue
            if ((listOf(st.q) + p.map { it.text } + al.map { it.text }).any { Validator.checkText(it, true) != null } || (st.sol.isNotEmpty() && Validator.checkText(st.sol) != null)) continue
            val it = Verifier.clean(Item("written", st.q, emptyList(), "", "", p, al, st.sol, board, level, subject, unit, marks, type))
            if (Verifier.verify(it, unit, lexicon).isNotEmpty()) continue; return it
        }
        throw ItemGenerationError("no valid item for $board/$level/$subject/$unit/$marks/$type")
    }
}
