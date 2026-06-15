package com.example.mirai.data.api

import com.example.mirai.data.models.*
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import java.util.concurrent.TimeUnit

interface MiraiApi {

    @GET("health")
    suspend fun health(): HealthResponse

    @POST("api/chat")
    suspend fun chat(@Body request: ChatRequest): ChatResponse

    @POST("api/nexus/nodes")
    suspend fun nexusAddNode(@Body body: Map<String, Any>): NexusNodeResponse

    @GET("api/nexus/nodes")
    suspend fun nexusListNodes(@Query("type") type: String = "", @Query("query") query: String = ""): NexusNodesResponse

    @DELETE("api/nexus/nodes/{nodeId}")
    suspend fun nexusDeleteNode(@Path("nodeId") nodeId: String): Map<String, Any>

    @POST("api/nexus/edges")
    suspend fun nexusAddEdge(@Body body: Map<String, Any>): NexusEdgeResponse

    @GET("api/nexus/connections/{nodeId}")
    suspend fun nexusConnections(@Path("nodeId") nodeId: String): NexusConnectionsResponse

    @GET("api/nexus/graph")
    suspend fun nexusGraph(): NexusGraphResponse

    @GET("api/nexus/search")
    suspend fun nexusSearch(@Query("query") query: String): NexusSearchResponse

    @GET("api/nexus/stats")
    suspend fun nexusStats(): NexusStatsResponse

    @POST("api/echo/thought")
    suspend fun echoSaveThought(@Body body: EchoThoughtRequest): EchoThoughtResponse

    companion object {
        private var instance: MiraiApi? = null
        private var currentBaseUrl: String = ""
        private val probeClient = OkHttpClient.Builder()
            .connectTimeout(3, TimeUnit.SECONDS)
            .readTimeout(3, TimeUnit.SECONDS)
            .writeTimeout(3, TimeUnit.SECONDS)
            .followRedirects(false)
            .build()

        fun getInstance(baseUrl: String = "http://10.0.2.2:8765/"): MiraiApi {
            val normalized = if (baseUrl.endsWith("/")) baseUrl else "$baseUrl/"
            if (instance == null || currentBaseUrl != normalized) {
                val logging = HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BODY
                }
                val client = OkHttpClient.Builder()
                    .addInterceptor(logging)
                    .connectTimeout(10, TimeUnit.SECONDS)
                    .readTimeout(120, TimeUnit.SECONDS)
                    .writeTimeout(30, TimeUnit.SECONDS)
                    .build()
                val retrofit = Retrofit.Builder()
                    .baseUrl(normalized)
                    .client(client)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build()
                instance = retrofit.create(MiraiApi::class.java)
                currentBaseUrl = normalized
            }
            return instance!!
        }

        fun resetInstance() {
            instance = null
            currentBaseUrl = ""
        }

        fun probe(url: String): ProbeResult {
            val healthUrl = if (url.endsWith("/")) "${url}health" else "$url/health"
            val request = okhttp3.Request.Builder().url(healthUrl).get().build()
            val start = System.currentTimeMillis()
            return try {
                val response = probeClient.newCall(request).execute()
                val latency = System.currentTimeMillis() - start
                val body = response.body?.string() ?: ""
                val success = response.isSuccessful && body.contains("\"ok\"")
                if (success) {
                    ProbeResult(true, url, latency, response.code, "", "")
                } else {
                    ProbeResult(false, url, latency, response.code, "http",
                        "HTTP ${response.code}: ${body.take(100)}")
                }
            } catch (e: Exception) {
                val latency = System.currentTimeMillis() - start
                val err = e.toApiError()
                ProbeResult(false, url, latency, 0, err.type, err.message)
            }
        }

        val probeUrls: List<String> get() = listOf(
            "http://10.0.2.2:8765/",
            "http://127.0.0.1:8765/",
            "http://localhost:8765/",
            "http://10.255.192.100:8765/",
            "http://192.168.1.100:8765/",
            "http://10.0.0.2:8765/"
        )
    }
}

data class ProbeResult(
    val success: Boolean,
    val url: String,
    val latencyMs: Long,
    val statusCode: Int,
    val errorType: String,
    val errorMessage: String
)

data class ApiError(
    val message: String,
    val type: String
)

fun Throwable.toApiError(): ApiError {
    val msg = (message ?: "").take(120)
    return when (this) {
        is UnknownHostException -> ApiError("DNS: server host not found — check URL", "dns")
        is ConnectException -> ApiError("Refused: no server at this address", "refused")
        is SocketTimeoutException -> ApiError("Timeout: server not responding (3s)", "timeout")
        is java.net.SocketException -> ApiError("Socket: ${msg}", "socket")
        is java.net.ProtocolException -> ApiError("Protocol: ${msg}", "protocol")
        is javax.net.ssl.SSLException -> ApiError("SSL: ${msg}", "ssl")
        is retrofit2.HttpException -> {
            val code = code()
            when {
                code == 401 -> ApiError("Auth: API key rejected (401)", "auth")
                code == 404 -> ApiError("Missing: endpoint not found (404)", "not_found")
                code >= 500 -> ApiError("Server error ($code)", "server")
                else -> ApiError("HTTP $code", "http")
            }
        }
        else -> ApiError("${this::class.simpleName}: $msg", "unknown")
    }
}
