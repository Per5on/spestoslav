package bg.spestoslav.receiptscanner

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.IntentSender
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.activity.result.ActivityResult
import androidx.activity.result.IntentSenderRequest
import androidx.activity.result.contract.ActivityResultContracts.StartIntentSenderForResult
import com.google.android.gms.tasks.Task
import com.google.mlkit.vision.documentscanner.GmsDocumentScannerOptions
import com.google.mlkit.vision.documentscanner.GmsDocumentScanning
import com.google.mlkit.vision.documentscanner.GmsDocumentScanningResult
import expo.modules.kotlin.activityresult.AppContextActivityResultContract
import expo.modules.kotlin.activityresult.AppContextActivityResultLauncher
import expo.modules.kotlin.functions.Coroutine
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.withContext
import java.io.File
import java.io.IOException
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

class ReceiptScannerModule : Module() {
  private lateinit var launcher: AppContextActivityResultLauncher<Int, ActivityResult>
  private val scanLock = Mutex()
  private var sender: IntentSender? = null

  override fun definition() = ModuleDefinition {
    Name("SpestovnikReceiptScanner")

    RegisterActivityContracts {
      launcher = registerForActivityResult(object : AppContextActivityResultContract<Int, ActivityResult> {
        override fun createIntent(context: Context, input: Int): Intent =
          StartIntentSenderForResult().createIntent(
            context, IntentSenderRequest.Builder(checkNotNull(sender)).build()
          )

        override fun parseResult(input: Int, resultCode: Int, intent: Intent?) =
          ActivityResult(resultCode, intent)
      }) { _, _ -> /* A recreated JS screen has no active receipt draft. */ }
    }

    AsyncFunction("scanAsync") Coroutine { ->
      if (!scanLock.tryLock()) error("A receipt scan is already open")
      try {
        val uri = withContext(Dispatchers.Main) {
          val activity = checkNotNull(appContext.currentActivity)
          val options = GmsDocumentScannerOptions.Builder()
            .setGalleryImportAllowed(false)
            .setPageLimit(1)
            .setResultFormats(GmsDocumentScannerOptions.RESULT_FORMAT_JPEG)
            .setScannerMode(GmsDocumentScannerOptions.SCANNER_MODE_BASE)
            .build()
          sender = GmsDocumentScanning.getClient(options).getStartScanIntent(activity).awaitResult()
          val result = launcher.launch(0)
          if (result.data?.hasExtra(StartIntentSenderForResult.EXTRA_SEND_INTENT_EXCEPTION) == true) {
            error("Unable to open the document scanner")
          }
          when (result.resultCode) {
            Activity.RESULT_CANCELED -> null
            Activity.RESULT_OK -> {
              checkNotNull(GmsDocumentScanningResult.fromActivityResultIntent(result.data)
                ?.pages?.singleOrNull()?.imageUri) { "Expected one scanned receipt page" }
            }
            else -> error("Document scan failed")
          }
        }
        if (uri == null) null else copyScan(uri)
      } finally {
        sender = null
        scanLock.unlock()
      }
    }
  }

  private suspend fun copyScan(uri: Uri): Map<String, Any> = withContext(Dispatchers.IO) {
    val context = checkNotNull(appContext.reactContext)
    val directory = File(context.cacheDir, "receipt-scans")
    if (!directory.isDirectory && !directory.mkdirs()) throw IOException("Cannot open scanner cache")
    val image = File.createTempFile("scan-", ".jpg", directory)
    try {
      checkNotNull(context.contentResolver.openInputStream(uri)).use { input ->
        image.outputStream().use { output ->
          val buffer = ByteArray(8192)
          var bytes = 0
          while (true) {
            val count = input.read(buffer)
            if (count < 0) break
            bytes += count
            if (bytes > 8 * 1024 * 1024) throw IOException("Receipt image is too large")
            output.write(buffer, 0, count)
          }
        }
      }
      val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
      BitmapFactory.decodeFile(image.path, bounds)
      if (bounds.outMimeType != "image/jpeg" || bounds.outWidth <= 0 || bounds.outHeight <= 0 ||
        bounds.outWidth.toLong() * bounds.outHeight > 20_000_000) {
        throw IOException("Unsupported receipt image")
      }
      mapOf(
        "uri" to Uri.fromFile(image).toString(),
        "width" to bounds.outWidth,
        "height" to bounds.outHeight,
        "fileSize" to image.length(),
        "mimeType" to "image/jpeg"
      )
    } catch (error: Exception) {
      image.delete()
      throw error
    }
  }

  private suspend fun <T> Task<T>.awaitResult(): T = suspendCancellableCoroutine { continuation ->
    addOnCompleteListener { task ->
      if (!continuation.isActive) return@addOnCompleteListener
      if (task.isSuccessful) continuation.resume(task.result)
      else continuation.resumeWithException(task.exception ?: IOException("Scanner unavailable"))
    }
  }
}
