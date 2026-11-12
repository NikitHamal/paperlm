package ai.paperlm

import org.json.JSONArray
import org.json.JSONObject
import java.io.File

/** One row of docs/packs/pack_registry.json (the same file the web playground reads). */
data class PackInfo(val id: String, val title: String, val level: String, val subject: String,
                    val params: Long, val onnxMb: Double, val valLoss: Double)

/** A fully loaded specialist pack: only ONE of these is kept in memory (see [PackRegistry.open]). */
class LoadedPack(val info: PackInfo, val dir: File) : AutoCloseable {
    val meta = PackMeta(JSONObject(File(dir, "pack.json").readText()))
    val tokJson = JSONObject(File(dir, "tokenizer.json").readText())
    val graph = JSONObject(File(dir, "syllabus_graph.json").readText())
    val bank: List<BankItem> = BankItem.parse(JSONArray(File(dir, "bank.json").readText()))
    val numeric: List<BankItem> = File(dir, "numeric_bank.json").let { if (it.exists()) BankItem.parse(JSONArray(it.readText())) else emptyList() }
    val units: List<UnitInfo> = (0 until graph.getJSONArray("units").length()).map {
        val u = graph.getJSONArray("units").getJSONObject(it)
        UnitInfo(u.getString("name"), u.optDouble("share", 0.0), (0 until u.optJSONArray("terms")!!.length()).map { i -> u.getJSONArray("terms").getString(i) })
    }
    /** Lazily created: building the TFLite interpreter costs ~100 ms and ~25 MB, so it is created on first neural request only. */
    val runner: TflitePackRunner by lazy { TflitePackRunner(File(dir, "model.tflite"), meta.layers, meta.heads, meta.headDim, meta.maxSeq, meta.vocab) }
    val engine: PackEngine by lazy { PackEngine(meta, PaperTokenizer(tokJson.toString()), TokTable(tokJson, meta.vocab), runner::feed, runner::reset) }
    override fun close() { /* interpreter + tables are garbage collected with this object */ }
}

data class UnitInfo(val name: String, val share: Double, val terms: List<String>)

data class BankItem(val type: String, val marks: Int, val unit: String, val question: String, val answer: String,
                    val anchor: String, val distractors: List<String>, val why: String, val src: String, val tpl: String = "") {
    companion object {
        fun parse(a: JSONArray): List<BankItem> = (0 until a.length()).map {
            val o = a.getJSONObject(it); val d = o.optJSONArray("distractors")
            BankItem(o.getString("type"), o.optInt("marks", 1), o.getString("unit"), o.getString("question"), o.getString("answer"),
                o.optString("anchor"), if (d == null) emptyList() else (0 until d.length()).map { i -> d.getString(i) }, o.optString("why"), o.optString("src"), o.optString("tpl"))
        }
    }
}

/**
 * Dynamic on-demand pack loader. Pack bundles are downloaded once into [root]/<pack_id>/ (or shipped as assets) and
 * opened lazily; opening a second pack closes the first, so memory stays bounded by ONE specialist model (~10 MB INT8).
 */
class PackRegistry(private val root: File) {
    val packs: List<PackInfo> by lazy {
        val a = JSONObject(File(root, "pack_registry.json").readText()).getJSONArray("packs")
        (0 until a.length()).map { val o = a.getJSONObject(it)
            PackInfo(o.getString("pack_id"), o.getString("title"), o.getString("level"), o.getString("subject"),
                o.optLong("params"), o.optDouble("onnx_mb"), o.optDouble("val_loss")) }
    }
    private var active: LoadedPack? = null

    fun forGrade(level: String, subject: String) = packs.firstOrNull { it.level == level && it.subject == subject }

    @Synchronized fun open(id: String): LoadedPack {
        active?.let { if (it.info.id == id) return it; it.close(); active = null }
        val info = packs.first { it.id == id }
        return LoadedPack(info, File(root, id)).also { active = it }
    }
}
