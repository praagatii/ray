package com.example.mirai.data.models

data class ChatRequest(
    val message: String,
    val history: List<Map<String, String>> = emptyList()
)

data class ChatResponse(
    val content: String = "",
    val turns: Int = 1,
    val success: Boolean = true
)

data class HealthResponse(
    val status: String = "",
    val engine: String = "",
    val model: String = ""
)

data class NexusNode(
    val id: String = "",
    val type: String = "note",
    val name: String = "",
    val properties: Map<String, Any> = emptyMap(),
    val created_at: String = "",
    val updated_at: String = ""
)

data class NexusEdge(
    val id: String = "",
    val source_id: String = "",
    val target_id: String = "",
    val type: String = "related_to",
    val properties: Map<String, Any> = emptyMap(),
    val created_at: String = ""
)

data class NexusGraphResponse(
    val nodes: List<NexusNode> = emptyList(),
    val edges: List<NexusEdge> = emptyList()
)

data class NexusNodeResponse(
    val node: NexusNode? = null,
    val success: Boolean = true,
    val error: String? = null
)

data class NexusNodesResponse(
    val nodes: List<NexusNode> = emptyList(),
    val total: Int = 0
)

data class NexusEdgeResponse(
    val edge: NexusEdge? = null,
    val success: Boolean = true,
    val error: String? = null
)

data class NexusConnectionsResponse(
    val node: NexusNode? = null,
    val connections: List<Map<String, Any?>> = emptyList()
)

data class NexusSearchResponse(
    val results: List<NexusNode> = emptyList()
)

data class NexusStatsResponse(
    val total_nodes: Int = 0,
    val total_edges: Int = 0,
    val nodes_by_type: Map<String, Int> = emptyMap(),
    val edges_by_type: Map<String, Int> = emptyMap()
)

data class EchoThoughtRequest(val text: String)

data class EchoThoughtResponse(
    val saved: Boolean = false,
    val node: NexusNode? = null
)

data class ThoughtItem(
    val id: String = "",
    val text: String = "",
    val type: String = "thought",
    val timestamp: String = ""
)
