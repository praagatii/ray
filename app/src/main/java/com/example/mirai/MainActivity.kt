package com.example.mirai

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.compose.rememberNavController
import com.example.mirai.ui.navigation.MiraiNavGraph
import com.example.mirai.ui.theme.Background
import com.example.mirai.ui.theme.MiraiTheme

private const val TAG = "MiraiApp"

class MainActivity : ComponentActivity() {

    private var originalHandler: Thread.UncaughtExceptionHandler? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        originalHandler = Thread.getDefaultUncaughtExceptionHandler()
        Thread.setDefaultUncaughtExceptionHandler { thread, throwable ->
            try {
                Log.e(TAG, "UNCAUGHT_EXCEPTION on ${thread.name}", throwable)
                val sw = java.io.StringWriter()
                val pw = java.io.PrintWriter(sw)
                throwable.printStackTrace(pw)
                pw.flush()
                val trace = sw.toString().take(500)
                val prefs = getSharedPreferences("mirai_crash", 0)
                prefs.edit().putString("last_crash", trace).apply()
            } catch (_: Exception) {}
            originalHandler?.uncaughtException(thread, throwable)
        }

        enableEdgeToEdge()
        setContent {
            MiraiTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = Background
                ) {
                    val navController = rememberNavController()
                    MiraiNavGraph(navController = navController)
                }
            }
        }
    }
}
