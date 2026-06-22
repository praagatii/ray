package com.example.ray.network

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

object RayApiClient {
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    private const val BASE_URL = "http://10.132.228.100:8000"
    private val JSON_MEDIA_TYPE = "application/json; charset=utf-8".toMediaType()

    suspend fun sendMessage(message: String): String {
        return withContext(Dispatchers.IO) {
            try {
                val requestBody = JSONObject().apply {
                    put("message", message)
                }.toString().toRequestBody(JSON_MEDIA_TYPE)

                val request = Request.Builder()
                    .url("$BASE_URL/chat")
                    .post(requestBody)
                    .build()

                val response = client.newCall(request).execute()
                val responseBody = response.body?.string()
                if (response.isSuccessful && responseBody != null) {
                    JSONObject(responseBody).getString("response")
                } else {
                    "Error: server returned ${response.code}"
                }
            } catch (e: Exception) {
                "Error: ${e.message ?: "Unknown error"}"
            }
        }
    }
}
