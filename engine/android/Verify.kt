// PaperLM verification layer for Android: Kotlin port of engine/web/verify.js (same rules, same thresholds).
// Symbol cleanup, MCQ homogeneity (dimensions/units/kind), answer-key consistency, arithmetic self-check, concept anchoring.
package com.nebians.paperlm

object Verifier {
    private val WORD = Regex("[A-Za-z\\u0900-\\u097F]{2,}")
    private val STOP = ("the of a an and or in on to is are was were be by for with as at from that this which what following these those its it into than then " +
        "their there has have had can will would should not no all any each one two three four give write state define explain find calculate prove show using used use " +
        "correct incorrect true false value values").split(" ").toSet()
    private fun stripMath(s: String) = s.replace("$$", "").replace("$", "")
    private fun normT(s: String) = s.lowercase().replace(Regex("[^a-z0-9\\u0900-\\u097F]+"), "")
    fun words(s: String) = WORD.findAll(stripMath(s).lowercase()).map { it.value }.filter { it !in STOP }.toList()

    /** one KaTeX/LaTeX-safe spelling for every inequality symbol */
    fun cleanSymbols(t: String): String {
        if (t.isEmpty()) return t
        val sb = StringBuilder(); var i = 0
        while (i < t.length) {
            if (t[i] == '$') {
                val d = if (t.startsWith("$$", i)) "$$" else "$"; val k = t.indexOf(d, i + d.length)
                if (k < 0) { sb.append(t.substring(i)); break }
                var m = t.substring(i + d.length, k)
                m = m.replace(Regex("\\\\leqslant|\\\\leq(?![A-Za-z])|\\\\le(?![A-Za-z])"), "\\\\leq").replace(Regex("\\\\geqslant|\\\\geq(?![A-Za-z])|\\\\ge(?![A-Za-z])"), "\\\\geq")
                    .replace("<=", "\\leq ").replace(">=", "\\geq ").replace("!=", "\\neq ").replace(Regex("\\s{2,}"), " ").trim()
                sb.append(d).append(m).append(d); i = k + d.length
            } else {
                var j = t.indexOf('$', i); if (j < 0) j = t.length
                sb.append(t.substring(i, j).replace("<=", "\u2264").replace(">=", "\u2265").replace("!=", "\u2260")); i = j
            }
        }
        return sb.toString().replace(Regex(" {2,}"), " ").replace(Regex("\\$ +\\$"), " ").replace(Regex(" +([,.;:?])"), "$1").trim()
    }

    private class Shape(val cls: String, val len: Int, val unit: String, val digits: Boolean, val body: String)
    private val NUMRE = "-?\\d+(?:\\.\\d+)?(?:\\s*\\\\times\\s*10\\^\\{?-?\\d+\\}?)?"
    private fun units(s: String): String {
        val u = ArrayList<String>()
        Regex("\\\\(?:text|mathrm)\\{\\s*([^}]*)\\}").findAll(s).forEach { u.add(it.groupValues[1].replace(Regex("\\s+"), "").lowercase()) }
        Regex("\\d\\s*\\}?\\s*(?:\\\\,|\\\\ |\\s)*([A-Za-z]{1,3}(?:/[A-Za-z]{1,3})?(?:\\^\\{?-?\\d\\}?)?)\\s*$").find(stripMath(s).trim())?.let { if (!Regex("^(and|or|is|a)$", RegexOption.IGNORE_CASE).matches(it.groupValues[1])) u.add(it.groupValues[1].lowercase()) }
        if (s.contains("^\\circ") || s.contains("\u00b0")) u.add("deg"); if (s.contains("%")) u.add("%")
        return u.joinToString("|")
    }
    private fun shape(opt: String): Shape {
        val raw = opt.trim(); val noM = raw.replace(Regex("\\$[^$]*\\$"), " ").replace(Regex("\\s+"), " ").trim(); val words = WORD.findAll(noM).count()
        val hasMath = raw.contains('$'); val body = stripMath(raw).trim(); val digits = body.any { it.isDigit() }
        val numeric = digits && Regex("^[^A-Za-z]*$NUMRE[^A-Za-z]*(?:\\\\(?:text|mathrm)\\{[^}]*\\})?[^A-Za-z]*[A-Za-z%/^{}\\-\\d\\\\ ,]*$").matches(body) && words <= 1
        val cls = if (words >= 3) "text" else if (numeric) "num" else if (hasMath || Regex("[=+\\-*/^]").containsMatchIn(body)) "expr" else "word"
        return Shape(cls, raw.length, units(raw), digits, body)
    }
    private fun numVal(s: String) = Regex("(-?\\d+(?:\\.\\d+)?)").find(stripMath(s).replace(Regex(",(?=\\d{3})"), ""))?.groupValues?.get(1)?.toDouble()

    fun checkOptions(opts: List<String>, question: String): List<String> {
        val issues = ArrayList<String>(); val sh = opts.map(::shape)
        val classes = sh.map { if (it.cls == "num" || it.cls == "expr") "math" else if (it.cls == "word") "text" else it.cls }.toSet()
        if (classes.size > 1) issues.add("option kinds differ")
        val nums = sh.filter { it.cls == "num" }; if (nums.size == 4 && nums.map { it.unit }.toSet().size > 1) issues.add("option units differ")
        val withU = sh.count { it.unit.isNotEmpty() }; if (withU in 1..3 && sh.all { it.digits }) issues.add("some options lack the unit")
        val lens = sh.map { maxOf(1, it.len) }; if (lens.max().toDouble() / lens.min() > (if ("text" in classes) 6 else 12)) issues.add("option length mismatch")
        if (sh.all { it.cls == "num" } && sh.map { numVal(it.body).toString() }.toSet().size < 4) issues.add("numeric duplicates")
        val symRe = Regex("([A-Za-z])_\\{?(\\w)\\}?")
        val sub = opts.map { o -> symRe.findAll(o).map { it.groupValues[1] + it.groupValues[2] }.toSet() }; val qs = symRe.findAll(question).map { it.groupValues[1] + it.groupValues[2] }.toSet()
        sub.forEachIndexed { i, s -> for (sym in s) if (sym !in qs && sub.withIndex().none { (j, x) -> j != i && sym in x } && sub.withIndex().any { (j, x) -> j != i && x.isEmpty() }) issues.add("foreign symbol $sym") }
        if (opts.count { Regex("(all|none) of the above", RegexOption.IGNORE_CASE).containsMatchIn(it) } > 1) issues.add("duplicate catch-all")
        return issues
    }
    fun checkKey(opts: List<String>, key: String, why: String): List<String> {
        val k = "abcd".indexOf(key); if (k < 0) return listOf("bad key"); if (why.isEmpty()) return emptyList()
        val issues = ArrayList<String>(); val wn = normT(stripMath(why)); val hits = opts.map { val n = normT(stripMath(it)); n.length >= 2 && wn.contains(n) }
        if (hits.any { it } && !hits[k]) issues.add("explanation names a different option than the key")
        val nums = Regex("=\\s*(-?\\d+(?:\\.\\d+)?)").findAll(stripMath(why).replace(Regex(",(?=\\d{3})"), "")).map { it.groupValues[1].toDouble() }.toList()
        if (nums.isNotEmpty()) { val last = nums.last(); val hit = opts.indices.filter { val v = numVal(opts[it]); v != null && Math.abs(v - last) <= 1e-9 + 1e-6 * Math.abs(last) }
            if (hit.size == 1 && hit[0] != k && opts.all { shape(it).digits }) issues.add("computed value matches option ${"abcd"[hit[0]]}, key is $key") }
        return issues
    }
    private val ARITH = Regex("(?<![A-Za-z0-9_^{.\\\\])(-?\\d+(?:\\.\\d+)?(?:\\s*(?:\\\\times|\\\\cdot|\\\\div|\\+|-|\\*|/)\\s*\\d+(?:\\.\\d+)?)+)\\s*=\\s*(-?\\d+(?:\\.\\d+)?)(?![\\d.]*[A-Za-z^_/{])")
    private fun evalChain(e: String): Double? {
        val t = e.replace("\\times", "*").replace("\\cdot", "*").replace("\\div", "/").replace(Regex("\\s+"), ""); if (!Regex("^[\\d.+\\-*/]+$").matches(t)) return null
        val toks = Regex("-?\\d+(?:\\.\\d+)?|[+\\-*/]").findAll(t).map { it.value }.toList(); if (toks.isEmpty()) return null
        val out = arrayListOf(toks[0].toDouble()); val ops = ArrayList<String>(); var i = 1
        while (i + 1 < toks.size) { val v = toks[i + 1].toDoubleOrNull() ?: return null; when (toks[i]) { "*" -> out[out.lastIndex] = out.last() * v; "/" -> out[out.lastIndex] = out.last() / v; else -> { ops.add(toks[i]); out.add(v) } }; i += 2 }
        var r = out[0]; for (j in ops.indices) r = if (ops[j] == "+") r + out[j + 1] else r - out[j + 1]; return r
    }
    fun checkArith(text: String): List<String> {
        val t = stripMath(text).replace(Regex("\\\\(?:text|mathrm)\\{[^}]*\\}"), " "); val bad = ArrayList<String>()
        for (m in ARITH.findAll(t)) { val v = evalChain(m.groupValues[1]) ?: continue; val c = m.groupValues[2].toDouble(); if (v.isFinite() && Math.abs(v - c) > maxOf(0.02 * Math.abs(v), 0.0105)) bad.add("${m.groupValues[1].trim()} = ${m.groupValues[2]}") }
        return bad
    }
    fun clean(it: Item) = it.copy(question = cleanSymbols(it.question), options = it.options.map(::cleanSymbols), explanation = cleanSymbols(it.explanation),
        parts = it.parts.map { p -> p.copy(text = cleanSymbols(p.text)) }, orParts = it.orParts.map { p -> p.copy(text = cleanSymbols(p.text)) }, rubric = cleanSymbols(it.rubric))
    /** empty list = item accepted */
    fun verify(it: Item, unit: String, lexicon: Set<String>? = null): List<String> {
        val issues = ArrayList<String>()
        val text = (listOf(it.question) + it.options + it.explanation + it.parts.map { p -> p.text } + it.orParts.map { p -> p.text } + it.rubric).joinToString(" ")
        if (it.kind == "mcq") { if (words(it.question).size < 2) issues.add("question too short"); issues += checkOptions(it.options, it.question); issues += checkKey(it.options, it.key, it.explanation) }
        else { if (words(it.question + " " + it.parts.joinToString(" ") { p -> p.text }).size < 3) issues.add("written item too short"); if (it.parts.any { p -> p.text.length < 8 }) issues.add("part too short"); if (it.parts.size > 6) issues.add("too many parts") }
        checkArith(text).firstOrNull()?.let { b -> issues.add("arithmetic error: $b") }
        if (lexicon != null && lexicon.size > 50) { val ws = words(text).toSet(); if (ws.size > 8 && ws.none { w -> w in lexicon }) issues.add("no syllabus concept in item") }
        if (Regex("(.)\\1{5,}").containsMatchIn(text)) issues.add("character run")
        return issues
    }
}

/** Official blueprints (full marks): NEB 11/12 = 75, SEE = 75, IOE = 100, BLE 8 = 48. Group, type, marks each, count. */
object Blueprints {
    val ALL: Map<String, List<Triple<String, String, Pair<Int, Int>>>> = mapOf(
        "C8" to listOf(Triple("A", "MCQ", 1 to 10), Triple("B", "SHORT", 2 to 6), Triple("C", "CONCEPTUAL", 4 to 4), Triple("D", "LONG", 5 to 2)),
        "C10" to listOf(Triple("A", "MCQ", 1 to 10), Triple("B", "SHORT", 2 to 8), Triple("C", "CONCEPTUAL", 4 to 6), Triple("D", "LONG", 5 to 5)),
        "C11" to listOf(Triple("A", "MCQ", 1 to 11), Triple("B", "SHORT", 5 to 8), Triple("C", "OR", 8 to 3)),
        "C12" to listOf(Triple("A", "MCQ", 1 to 11), Triple("B", "SHORT", 5 to 8), Triple("C", "OR", 8 to 3)),
        "IOE" to listOf(Triple("A", "MCQ", 1 to 100)), "CEE" to listOf(Triple("A", "MCQ", 1 to 100)), "BCA" to listOf(Triple("A", "MCQ", 1 to 100)),
        "BSN" to listOf(Triple("A", "MCQ", 1 to 100)), "BE" to listOf(Triple("A", "OR", 10 to 8)))
    fun fullMarks(level: String) = ALL[level]?.sumOf { it.third.first * it.third.second } ?: 0
}
