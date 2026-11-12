package ai.paperlm

import kotlin.random.Random

/** Kotlin twin of engine/pack_paper.py and planPaper in docs/packlm.js (bank tier). Blueprint planner + coverage tracker. */
object PackPaper {
    data class Slot(val kind: String, val marks: Int, val item: BankItem, val steps: List<Pair<String, Int>>)
    data class Paper(val slots: List<Slot>, val missed: Int, val unitsCovered: Int)

    private val WORD = Regex("[a-z0-9]{3,}")
    private fun words(s: String) = WORD.findAll(s.lowercase()).map { it.value }.toSet()
    private fun jac(a: Set<String>, b: Set<String>) = a.intersect(b).size.toDouble() / maxOf(1, a.union(b).size)

    /** Largest-remainder quotas so unit shares sum exactly to [total]. */
    fun quotas(units: List<UnitInfo>, total: Int): IntArray {
        val q = units.map { it.share * total }; val base = q.map { it.toInt() }.toIntArray()
        val order = q.indices.sortedByDescending { q[it] - base[it] }
        for (i in order.take(total - base.sum())) base[i]++
        return base
    }

    /** Model answer -> step marks. Answers that already carry "... [2] ... [1]" keep them when they add up. */
    fun scheme(ans: String, marks: Int): List<Pair<String, Int>> {
        val tg = ans.trim().split(Regex("\\s*\\[(\\d+)]\\s*\\|?\\s*"))
        val tagged = Regex("\\[(\\d+)]").findAll(ans).map { it.groupValues[1].toInt() }.toList()
        if (tagged.isNotEmpty() && tagged.sum() == marks && tg.size >= 2) {
            val st = tagged.indices.filter { tg[it].isNotBlank() }.map { tg[it].trim() to tagged[it] }
            if (st.isNotEmpty()) return st
        }
        val steps = ans.split(Regex("(?<=[.;])\\s+(?=[A-Z(\\\\$])")).map { it.trim() }.filter { it.length > 8 }.ifEmpty { listOf(ans) }
        val k = maxOf(1, minOf(steps.size, marks * 2)); val mk = IntArray(k) { marks / k }
        for (i in 0 until marks - mk.sum()) mk[i % k]++
        return steps.take(k).zip(mk.toList()).filter { it.second > 0 }
    }

    fun plan(p: LoadedPack, nMcq: Int = 10, nShort: Int = 4, nNum: Int = 2, seed: Int = 7): Paper {
        val rnd = Random(seed); val us = p.units
        val spec = List(nMcq) { "mcq" to 1 } + List(nShort / 2) { "short" to 3 } + List(nShort - nShort / 2) { "short" to 5 }
        val slots = us.zip(quotas(us, spec.size).toList()).flatMap { (u, c) -> List(c) { u } }.shuffled(rnd)
        val used = HashSet<String>(); val anchors = HashSet<String>(); val seen = ArrayList<Set<String>>()
        val out = ArrayList<Triple<String, Int, BankItem>>(); var miss = 0
        for ((i, sp) in spec.withIndex()) {
            val (kind, marks) = sp
            val order = listOf(slots[i]) + us.filter { it !== slots[i] }.sortedByDescending { it.share }
            val pool = order.asSequence().map { u ->
                p.bank.filter { it.unit == u.name && it.type == kind && it.question !in used && it.anchor !in anchors &&
                    (kind == "mcq" || Math.abs(it.marks - marks) <= 1) && seen.all { w -> jac(words(it.question), w) < 0.6 } }
            }.firstOrNull { it.isNotEmpty() }
            if (pool == null) { miss++; continue }
            val b = pool[rnd.nextInt(pool.size)]
            used += b.question; anchors += b.anchor; seen += words(b.question); out += Triple(kind, marks, b)
        }
        // computed numericals (key + distractors derived from a formula) replace the lowest-priority bank MCQs
        val share = us.associate { it.name to it.share }
        val tpl = p.numeric.groupBy { it.tpl }.values.sortedByDescending { share[it[0].unit] ?: 0.0 }
        val seenU = HashSet<String>(); var done = 0
        for (g in tpl) {
            if (done >= nNum) break
            if (g[0].unit in seenU && seenU.size < tpl.map { it[0].unit }.toSet().size) continue
            val pick = g.shuffled(rnd).take(8).firstOrNull { c -> out.all { o -> jac(words(c.question), words(o.third.question)) < 0.6 } } ?: continue  // near-duplicate gate also applies to computed items
            seenU += pick.unit
            val j = out.indices.lastOrNull { out[it].first == "mcq" && out[it].third.src != "computed" && out[it].third.unit == pick.unit }
                ?: out.indices.lastOrNull { out[it].first == "mcq" && out[it].third.src != "computed" } ?: break
            out[j] = Triple("mcq", 1, pick); done++
        }
        return Paper(out.map { (k, m, b) -> Slot(k, m, b, if (k == "mcq") emptyList() else scheme(b.answer, b.marks)) }, miss, out.map { it.third.unit }.toSet().size)
    }
}
