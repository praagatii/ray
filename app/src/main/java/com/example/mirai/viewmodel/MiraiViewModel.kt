package com.example.mirai.viewmodel

import android.app.Application
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.util.Log
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.mirai.data.api.ApiError
import com.example.mirai.data.api.MiraiApi
import com.example.mirai.data.api.ProbeResult
import com.example.mirai.data.api.toApiError
import com.example.mirai.data.models.*
import kotlinx.coroutines.*
import java.util.Locale

private const val TAG = "MiraiVM"

enum class UiState { IDLE, LISTENING, THINKING, SPEAKING }

class MiraiViewModel(application: Application) : AndroidViewModel(application) {

    private var api: MiraiApi = MiraiApi.getInstance()
    private var healthCheckJob: Job? = null

    var isLoggedIn by mutableStateOf(false)
    var isFirstTime by mutableStateOf(true)
    var passwordError by mutableStateOf("")

    var uiState by mutableStateOf(UiState.IDLE)
        private set
    var lastResponse by mutableStateOf("")
        private set
    var transcript by mutableStateOf("")
        private set

    var graphNodes by mutableStateOf(listOf<NexusNode>())
        private set
    var graphEdges by mutableStateOf(listOf<NexusEdge>())
        private set
    var selectedNode by mutableStateOf<NexusNode?>(null)
        private set
    var nodeConnections by mutableStateOf<List<Map<String, Any?>>>(emptyList())
        private set
    var nexusStats by mutableStateOf<NexusStatsResponse?>(null)
        private set
    var nexusQuery by mutableStateOf("")
    var nexusSearchResults by mutableStateOf(listOf<NexusNode>())
        private set

    var serverUrl by mutableStateOf("http://10.0.2.2:8765/")
    var serverConnected by mutableStateOf(false)
        private set
    var serverError by mutableStateOf("")
        private set
    var lastApiError by mutableStateOf<ApiError?>(null)
        private set
    var memoryEnabled by mutableStateOf(true)
    var voiceEnabled by mutableStateOf(true)
    var ttsReady by mutableStateOf(false)
        private set
    var isHealthChecking by mutableStateOf(false)
        private set
    var probeResults by mutableStateOf(listOf<ProbeResult>())
        private set
    var crashLog by mutableStateOf("")
        private set

    private var tts: TextToSpeech? = null
    private var speechRecognizer: SpeechRecognizer? = null

    init {
        Log.d(TAG, "ViewModel init")
        initTts()
        initSpeechRecognizer()
        startHealthCheckLoop()
        loadMindGraph()
        try {
            val prefs = getApplication<Application>().getSharedPreferences("mirai_crash", 0)
            val lastCrash = prefs.getString("last_crash", "") ?: ""
            if (lastCrash.isNotBlank()) {
                crashLog = lastCrash.take(300)
                Log.w(TAG, "Previous crash detected:\n$lastCrash")
            }
        } catch (_: Exception) {}
    }

    private fun startHealthCheckLoop() {
        healthCheckJob?.cancel()
        healthCheckJob = viewModelScope.launch {
            while (isActive) {
                isHealthChecking = true
                val found = probeServersConcurrent()
                isHealthChecking = false
                if (!found) {
                    Log.d(TAG, "All probes failed, retrying in 5s")
                }
                delay(5000)
            }
        }
    }

    private suspend fun probeServersConcurrent(): Boolean {
        return coroutineScope {
            val urlsToTry = (listOf(this@MiraiViewModel.serverUrl) + MiraiApi.probeUrls).distinct()
            Log.d(TAG, "Probing ${urlsToTry.size} URLs concurrently: $urlsToTry")

            val deferreds = urlsToTry.map { url ->
                async {
                    MiraiApi.probe(url)
                }
            }
            val results = deferreds.awaitAll()
            this@MiraiViewModel.probeResults = results

            for (r in results) {
                if (r.success) {
                    Log.i(TAG, "PROBE_OK [${r.url}] ${r.latencyMs}ms")
                } else {
                    Log.w(TAG, "PROBE_FAIL [${r.url}] ${r.latencyMs}ms ${r.errorType}:${r.errorMessage}")
                }
            }

            val ok = results.firstOrNull { it.success }
            if (ok != null) {
                if (this@MiraiViewModel.serverUrl != ok.url) {
                    Log.i(TAG, "Switching to working URL: ${ok.url}")
                    this@MiraiViewModel.serverUrl = ok.url
                }
                if (!this@MiraiViewModel.serverConnected) {
                    this@MiraiViewModel.serverConnected = true
                    Log.i(TAG, "Server connected at ${ok.url}")
                }
                this@MiraiViewModel.serverError = ""
                this@MiraiViewModel.lastApiError = null
                this@MiraiViewModel.api = MiraiApi.getInstance(ok.url)
                return@coroutineScope true
            }

            val lastErr = results.lastOrNull { it.errorMessage.isNotBlank() }
            if (lastErr != null) {
                val msg = "[${lastErr.url}] ${lastErr.errorType}: ${lastErr.errorMessage}"
                this@MiraiViewModel.lastApiError = ApiError(msg, lastErr.errorType)
                Log.e(TAG, "Probe all failed: $msg")
            } else {
                this@MiraiViewModel.lastApiError = ApiError("All servers unreachable", "network")
                Log.e(TAG, "Probe all failed: no errors captured")
            }

            if (this@MiraiViewModel.serverConnected) {
                this@MiraiViewModel.serverConnected = false
                Log.w(TAG, "Server connection lost")
            }
            return@coroutineScope false
        }
    }

    private fun initTts() {
        tts = TextToSpeech(getApplication()) { status ->
            ttsReady = status == TextToSpeech.SUCCESS
            tts?.language = Locale.US
            tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                override fun onStart(uttId: String?) {
                    Log.d(TAG, "RAY_SPEAKING_STARTED: $uttId")
                    uiState = UiState.SPEAKING
                }
                override fun onDone(uttId: String?) {
                    Log.d(TAG, "RAY_SPEAKING_DONE")
                    uiState = UiState.IDLE
                }
                override fun onError(uttId: String?) {
                    Log.e(TAG, "RAY_SPEAKING_ERROR: $uttId")
                    uiState = UiState.IDLE
                }
            })
        }
    }

    private fun initSpeechRecognizer() {
        try {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(getApplication())
            speechRecognizer?.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {
                    Log.d(TAG, "RAY_LISTENING_STARTED")
                    uiState = UiState.LISTENING
                }
                override fun onBeginningOfSpeech() {}
                override fun onRmsChanged(rmsdB: Float) {}
                override fun onBufferReceived(buffer: ByteArray?) {}
                override fun onEndOfSpeech() {
                    Log.d(TAG, "RAY_LISTENING_ENDED")
                }
                override fun onError(error: Int) {
                    val msg = when (error) {
                        SpeechRecognizer.ERROR_AUDIO -> "Audio error"
                        SpeechRecognizer.ERROR_CLIENT -> "Client error"
                        SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "No mic permission"
                        SpeechRecognizer.ERROR_NETWORK -> "Network error"
                        SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Network timeout"
                        SpeechRecognizer.ERROR_NO_MATCH -> "No speech detected"
                        SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "Recognizer busy"
                        SpeechRecognizer.ERROR_SERVER -> "Server error"
                        SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "No speech"
                        else -> "Unknown error $error"
                    }
                    Log.e(TAG, "RAY_ERROR: $msg")
                    if (uiState == UiState.LISTENING) {
                        uiState = UiState.IDLE
                    }
                }
                override fun onResults(results: Bundle?) {
                    val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    val text = if (!matches.isNullOrEmpty()) matches[0] else ""
                    Log.d(TAG, "RAY_TRANSCRIPT: \"$text\"")
                    transcript = text
                    if (text.isNotBlank()) {
                        processTranscript(text)
                    } else {
                        uiState = UiState.IDLE
                    }
                }
                override fun onPartialResults(partialResults: Bundle?) {
                    val matches = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    if (!matches.isNullOrEmpty()) {
                        transcript = matches[0]
                    }
                }
                override fun onEvent(eventType: Int, params: Bundle?) {}
            })
            Log.d(TAG, "SpeechRecognizer initialized")
        } catch (e: Exception) {
            Log.e(TAG, "SpeechRecognizer init failed: $e")
        }
    }

    fun speak(text: String) {
        if (!voiceEnabled || !ttsReady) {
            Log.w(TAG, "TTS not ready (voice=$voiceEnabled, ready=$ttsReady)")
            uiState = UiState.IDLE
            return
        }
        Log.d(TAG, "RAY_SPEAKING: $text")
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "ray_response")
    }

    fun startListening() {
        if (speechRecognizer == null) {
            Log.e(TAG, "SpeechRecognizer is null")
            return
        }
        uiState = UiState.LISTENING
        transcript = ""
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
        }
        speechRecognizer?.startListening(intent)
        Log.d(TAG, "startListening() called")
    }

    fun stopListening() {
        speechRecognizer?.stopListening()
        if (uiState == UiState.LISTENING) {
            val text = transcript.trim()
            if (text.isNotBlank()) {
                processTranscript(text)
            } else {
                uiState = UiState.IDLE
            }
        }
    }

    private fun processTranscript(text: String) {
        Log.d(TAG, "RAY_PROCESS: \"$text\"")
        if (!serverConnected) {
            Log.e(TAG, "RAY_ERROR: Server offline, cannot send request")
            lastApiError = ApiError("Server is offline — check connection", "connection")
            uiState = UiState.IDLE
            return
        }
        uiState = UiState.THINKING
        Log.d(TAG, "RAY_REQUEST_SENT: $text")

        viewModelScope.launch {
            try {
                api.echoSaveThought(EchoThoughtRequest(text = text))
                Log.d(TAG, "Thought saved to echo")
            } catch (_: Exception) {}

            try {
                val resp = api.chat(ChatRequest(message = text))
                lastResponse = resp.content
                lastApiError = null
                Log.d(TAG, "RAY_RESPONSE_RECEIVED: ${resp.content.take(100)}")

                if (memoryEnabled) {
                    saveToMind(text)
                }

                speak(resp.content)
                loadMindGraph()
            } catch (e: Exception) {
                val err = e.toApiError()
                lastApiError = err
                Log.e(TAG, "RAY_REQUEST_FAILED: ${err.message}")
                lastResponse = err.message
                speak("Sorry, I couldn't reach the server")
            }
        }
    }

    private suspend fun saveToMind(text: String) {
        try {
            val mainNode = api.nexusAddNode(mapOf(
                "type" to "memory",
                "name" to text.take(60),
                "properties" to mapOf("full_text" to text, "source" to "voice")
            ))
            if (mainNode.success && mainNode.node != null) {
                val words = text.split("\\s+".toRegex()).filter { it.length > 3 }.distinct()
                for (word in words.take(10)) {
                    val childNode = api.nexusAddNode(mapOf(
                        "type" to "note",
                        "name" to word,
                        "properties" to mapOf("context" to text.take(100))
                    ))
                    if (childNode.success && childNode.node != null) {
                        api.nexusAddEdge(mapOf(
                            "source_id" to mainNode.node.id,
                            "target_id" to childNode.node.id,
                            "type" to "mentions"
                        ))
                    }
                }
                Log.d(TAG, "Mind save complete: ${words.size} words linked")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Mind save error: $e")
        }
    }

    fun tapOrb() {
        when (uiState) {
            UiState.IDLE -> startListening()
            UiState.LISTENING -> stopListening()
            else -> {}
        }
    }

    override fun onCleared() {
        healthCheckJob?.cancel()
        speechRecognizer?.destroy()
        tts?.stop()
        tts?.shutdown()
        super.onCleared()
    }

    // --- Server ---

    fun testConnection() {
        viewModelScope.launch {
            isHealthChecking = true
            val found = probeServersConcurrent()
            isHealthChecking = false
            serverError = if (found) "" else lastApiError?.message ?: "Connection failed"
            Log.i(TAG, "testConnection: found=$found error='$serverError'")
        }
    }

    fun updateServerUrl(url: String) {
        serverUrl = url
        MiraiApi.resetInstance()
        api = MiraiApi.getInstance(url)
        testConnection()
    }

    // --- Auth ---

    fun login(password: String) {
        val prefs = getApplication<Application>().getSharedPreferences("mirai_auth", 0)
        val storedHash = prefs.getString("password_hash", null)
        if (storedHash == null) {
            prefs.edit().putString("password_hash", password).apply()
            isFirstTime = false; isLoggedIn = true
        } else if (storedHash == password) {
            isLoggedIn = true; passwordError = ""
        } else {
            passwordError = "Incorrect password"
        }
    }

    fun logout() {
        getApplication<Application>().getSharedPreferences("mirai_auth", 0).edit().clear().apply()
        isLoggedIn = false
    }

    fun changePassword(newPassword: String) {
        getApplication<Application>().getSharedPreferences("mirai_auth", 0)
            .edit().putString("password_hash", newPassword).apply()
    }

    // --- Mind ---

    fun loadMindGraph() {
        viewModelScope.launch {
            try {
                val graph = api.nexusGraph()
                graphNodes = graph.nodes
                graphEdges = graph.edges
                nexusStats = api.nexusStats()
            } catch (_: Exception) {}
        }
    }

    fun selectNode(node: NexusNode) {
        selectedNode = node
        viewModelScope.launch {
            try { nodeConnections = api.nexusConnections(node.id).connections } catch (_: Exception) { nodeConnections = emptyList() }
        }
    }

    fun clearNodeSelection() { selectedNode = null; nodeConnections = emptyList() }

    fun addNode(type: String, name: String) {
        viewModelScope.launch { try { api.nexusAddNode(mapOf("type" to type, "name" to name)); loadMindGraph() } catch (_: Exception) {} }
    }

    fun deleteNode(nodeId: String) {
        viewModelScope.launch {
            try {
                if (nodeId.isBlank()) { logCrash("deleteNode: blank nodeId"); return@launch }
                if (selectedNode != null && selectedNode!!.id == nodeId) {
                    clearNodeSelection()
                }
                api.nexusDeleteNode(nodeId)
                loadMindGraph()
                Log.i(TAG, "deleteNode OK: $nodeId")
            } catch (e: Exception) {
                logCrash("deleteNode: ${e::class.simpleName} - ${e.message}")
                Log.e(TAG, "deleteNode failed: $nodeId", e)
            }
        }
    }

    fun logCrash(msg: String) {
        val ts = java.text.SimpleDateFormat("HH:mm:ss", Locale.US).format(java.util.Date())
        crashLog = "[$ts] $msg"
        Log.e(TAG, "CRASH_LOG: $msg")
    }

    fun searchMind(query: String) {
        nexusQuery = query
        if (query.isBlank()) { nexusSearchResults = emptyList(); return }
        viewModelScope.launch { try { nexusSearchResults = api.nexusSearch(query).results } catch (_: Exception) {} }
    }

    fun toggleMemory() { memoryEnabled = !memoryEnabled }
    fun toggleVoice() { voiceEnabled = !voiceEnabled; if (!voiceEnabled) { tts?.stop(); uiState = UiState.IDLE } }
}
