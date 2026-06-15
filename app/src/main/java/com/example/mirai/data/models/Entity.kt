package com.example.mirai.data.models

data class Project(
    val id: String = "",
    val title: String = "",
    val status: String? = null,
    val progress: Int = 0,
    val completed: Boolean = false,
    val completed_at: String? = null,
    val priority: Int? = null,
    val deadline: String? = null,
    val created_at: String = ""
)

data class Task(
    val id: String = "",
    val title: String = "",
    val completed: Boolean = false,
    val completed_at: String? = null,
    val priority: Int? = null,
    val deadline: String? = null,
    val project_id: String? = null,
    val tags: List<String> = emptyList(),
    val created_at: String = ""
)

data class Learning(
    val id: String = "",
    val topic: String = "",
    val progress: Int = 0,
    val completed: Boolean = false,
    val completed_at: String? = null,
    val resources: List<String> = emptyList(),
    val subtopics: List<String> = emptyList(),
    val streak: Int = 0,
    val last_practiced: String? = null,
    val created_at: String = ""
)

data class Personal(
    val id: String = "",
    val content: String? = null,
    val created_at: String = ""
)

data class Idea(
    val id: String = "",
    val title: String = "",
    val notes: String? = null,
    val project_id: String? = null,
    val created_at: String = ""
)

data class MemoryLink(
    val id: String = "",
    val source_type: String = "",
    val source_id: String = "",
    val target_type: String = "",
    val target_id: String = "",
    val link_type: String = "related_to",
    val created_at: String = ""
)

data class MemoryItem(
    val id: String = "",
    val content: String = "",
    val source: String = "",
    val metadata: Map<String, Any> = emptyMap(),
    val timestamp: String = ""
)

data class AppState(
    val projects: List<Project> = emptyList(),
    val tasks: List<Task> = emptyList(),
    val learnings: List<Learning> = emptyList(),
    val personals: List<Personal> = emptyList(),
    val ideas: List<Idea> = emptyList(),
    val memoryLinks: List<MemoryLink> = emptyList()
)
