package ai.paperlm

import org.tensorflow.lite.Interpreter
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.FloatBuffer
import java.nio.IntBuffer

/**
 * LiteRT / TFLite backend for a PaperLM subject pack (`docs/packs/<id>/model.tflite`, exported by `packs/tools/export_tflite.py`).
 * Two signatures with identical I/O names: `decode` (S=1) and `prefill` (S=64).  Cache tensors are [L,1,H,P,Dh] float32, P = pack.json `max_seq`.
 * Parity of this exact graph against PyTorch is verified on the VM with the TFLite interpreter (see `tflite_report.json`).
 * NOTE: this Kotlin file has not been compiled in CI yet (no Android toolchain on the training VM); the graph itself has been run and checked in Python.
 */
class TflitePackRunner(modelFile: File, private val layers: Int, private val heads: Int, private val headDim: Int, private val maxSeq: Int, private val vocab: Int) : AutoCloseable {
    private val interp = Interpreter(modelFile, Interpreter.Options().setNumThreads(4))
    private val cacheLen = layers * heads * maxSeq * headDim
    private var pk = direct(cacheLen); private var pv = direct(cacheLen)
    private var nk = direct(cacheLen); private var nv = direct(cacheLen)
    var pos = 0; private set

    private fun direct(n: Int): FloatBuffer = ByteBuffer.allocateDirect(n * 4).order(ByteOrder.nativeOrder()).asFloatBuffer()
    private fun ints(vararg v: Int): IntBuffer = ByteBuffer.allocateDirect(v.size * 4).order(ByteOrder.nativeOrder()).asIntBuffer().also { it.put(v); it.rewind() }

    fun reset() { pk = direct(cacheLen); pv = direct(cacheLen); pos = 0 }

    /** Feeds [ids] (any length) and returns the logits of the LAST real token. Prompt chunks are padded to 64 and the padding is masked by position. */
    fun feed(ids: IntArray): FloatArray {
        var last = FloatArray(vocab); var i = 0
        while (i < ids.size) {
            val one = ids.size - i == 1 && false
            val s = if (ids.size - i >= 64 || ids.size - i > 1) 64 else 1
            val n = minOf(s, ids.size - i); val chunk = IntArray(s).also { System.arraycopy(ids, i, it, 0, n) }
            val logits = direct(s * vocab); pk.rewind(); pv.rewind(); nk.rewind(); nv.rewind()
            interp.runSignature(mapOf("ids" to ints(*chunk).also { it.rewind() }, "pos" to ints(pos), "past_k" to pk, "past_v" to pv),
                mapOf("logits" to logits, "present_k" to nk, "present_v" to nv), if (s == 1) "decode" else "prefill")
            val t = pk; pk = nk; nk = t; val u = pv; pv = nv; nv = u
            logits.rewind(); logits.position((n - 1) * vocab); last = FloatArray(vocab).also { logits.get(it) }
            pos += n; i += n; if (one) break
        }
        return last
    }

    override fun close() = interp.close()
}
