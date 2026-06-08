package com.example.schedule

import android.content.Context
import android.net.Uri
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

private const val TASK_CHART_DATASTORE_NAME = "task_chart_store"
private const val TASK_CHART_JSON_KEY = "task_chart_json"
private val Context.taskChartDataStore by preferencesDataStore(name = TASK_CHART_DATASTORE_NAME)
private val taskChartJsonPreferenceKey = stringPreferencesKey(TASK_CHART_JSON_KEY)
private val taskChartJson = Json {
    prettyPrint = true
    ignoreUnknownKeys = true
}

data class TaskChartUiState(
    val categories: List<TaskCategoryGroup> = defaultTaskChart(),
    val selectedCategoryIndex: Int = 0,
    val isDarkTheme: Boolean = false,
    val hasUnsavedChanges: Boolean = false,
    val message: String? = null
) {
    val selectedCategory: TaskCategoryGroup
        get() = categories.getOrElse(selectedCategoryIndex) { categories.first() }

    val totalTasks: Int
        get() = categories.sumOf { it.tasks.size }

    val completedTasks: Int
        get() = categories.sumOf { category -> category.tasks.count { it.done } }

    val completionProgress: Float
        get() = progressFor(completedTasks, totalTasks)

    val summaries: List<TaskCategorySummary>
        get() = categories.map { category ->
            val done = category.tasks.count { it.done }
            TaskCategorySummary(
                categoryName = category.name,
                completed = done,
                total = category.tasks.size,
                progress = progressFor(done, category.tasks.size)
            )
        }
}

data class TaskCategorySummary(
    val categoryName: String,
    val completed: Int,
    val total: Int,
    val progress: Float
)

class TaskChartViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(TaskChartUiState())
    val uiState = _uiState.asStateFlow()

    fun onEvent(event: TaskChartEvent, context: Context) {
        when (event) {
            TaskChartEvent.ToggleTheme -> toggleTheme()
            is TaskChartEvent.SelectCategory -> selectCategory(event.index)
            is TaskChartEvent.ToggleTaskDone -> toggleTaskDone(
                categoryName = event.categoryName,
                taskId = event.taskId,
                done = event.done
            )
            is TaskChartEvent.AddTask -> addTask(
                categoryName = event.categoryName,
                name = event.name,
                priority = event.priority
            )
            is TaskChartEvent.EditTask -> editTask(
                originalCategoryName = event.originalCategoryName,
                taskId = event.taskId,
                updatedCategoryName = event.updatedCategoryName,
                name = event.name,
                priority = event.priority
            )
            is TaskChartEvent.DeleteTask -> deleteTask(event.categoryName, event.taskId)
            TaskChartEvent.ResetStatuses -> resetStatuses()
            TaskChartEvent.SaveLocal -> saveLocally(context)
            TaskChartEvent.LoadLocal -> loadLocally(context)
            TaskChartEvent.AcknowledgeMessage -> clearMessage()
        }
    }

    fun exportMarkdownToUri(context: Context, destinationUri: Uri) {
        viewModelScope.launch(Dispatchers.IO) {
            runCatching {
                val raw = buildTaskChartMarkdown(_uiState.value.categories)
                context.contentResolver.openOutputStream(destinationUri)?.use { stream ->
                    stream.write(raw.toByteArray())
                } ?: error("Unable to open destination file.")
            }.onSuccess {
                _uiState.update { it.copy(message = "Task chart exported to Markdown") }
            }.onFailure { error ->
                _uiState.update {
                    it.copy(message = "Export failed: ${error.localizedMessage ?: "Unknown error"}")
                }
            }
        }
    }

    private fun toggleTheme() {
        _uiState.update { it.copy(isDarkTheme = !it.isDarkTheme) }
    }

    private fun selectCategory(index: Int) {
        _uiState.update { state ->
            state.copy(selectedCategoryIndex = index.coerceIn(state.categories.indices))
        }
    }

    private fun toggleTaskDone(categoryName: String, taskId: String, done: Boolean) {
        _uiState.update { state ->
            state.copy(
                categories = state.categories.map { category ->
                    if (category.name != categoryName) {
                        category
                    } else {
                        category.copy(
                            tasks = category.tasks.map { task ->
                                if (task.id == taskId) task.copy(done = done) else task
                            }
                        )
                    }
                },
                hasUnsavedChanges = true
            )
        }
    }

    private fun addTask(categoryName: String, name: String, priority: TaskPriority) {
        val trimmedName = name.trim()
        if (trimmedName.isEmpty()) return

        _uiState.update { state ->
            val nextId = nextTaskId(state.categories)
            state.copy(
                categories = state.categories.withUpdatedCategory(categoryName) { category ->
                    category.copy(
                        tasks = sortTasks(category.tasks + TaskChartItem(nextId, trimmedName, priority))
                    )
                },
                hasUnsavedChanges = true
            )
        }
    }

    private fun editTask(
        originalCategoryName: String,
        taskId: String,
        updatedCategoryName: String,
        name: String,
        priority: TaskPriority
    ) {
        val trimmedName = name.trim()
        if (trimmedName.isEmpty()) return

        _uiState.update { state ->
            val existingTask = state.categories
                .firstOrNull { it.name == originalCategoryName }
                ?.tasks
                ?.firstOrNull { it.id == taskId }
                ?: return@update state
            val updatedTask = existingTask.copy(name = trimmedName, priority = priority)

            val removedFromOriginal = state.categories.withUpdatedCategory(originalCategoryName) { category ->
                category.copy(tasks = category.tasks.filterNot { it.id == taskId })
            }
            val updatedCategories = removedFromOriginal.withUpdatedCategory(updatedCategoryName) { category ->
                category.copy(tasks = sortTasks(category.tasks + updatedTask))
            }
            val selectedIndex = updatedCategories.indexOfFirst { it.name == updatedCategoryName }
                .takeIf { it >= 0 }
                ?: state.selectedCategoryIndex

            state.copy(
                categories = updatedCategories,
                selectedCategoryIndex = selectedIndex,
                hasUnsavedChanges = true
            )
        }
    }

    private fun deleteTask(categoryName: String, taskId: String) {
        _uiState.update { state ->
            state.copy(
                categories = state.categories.withUpdatedCategory(categoryName) { category ->
                    category.copy(tasks = category.tasks.filterNot { it.id == taskId })
                },
                hasUnsavedChanges = true
            )
        }
    }

    private fun resetStatuses() {
        _uiState.update { state ->
            state.copy(
                categories = state.categories.map { category ->
                    category.copy(tasks = category.tasks.map { it.copy(done = false) })
                },
                hasUnsavedChanges = true
            )
        }
    }

    private fun saveLocally(context: Context) {
        viewModelScope.launch(Dispatchers.IO) {
            runCatching {
                context.taskChartDataStore.edit { preferences ->
                    preferences[taskChartJsonPreferenceKey] = encodeTaskChartPayload(_uiState.value.categories)
                }
            }.onSuccess {
                _uiState.update { it.copy(message = "Task chart saved locally", hasUnsavedChanges = false) }
            }.onFailure { error ->
                _uiState.update {
                    it.copy(message = "Save failed: ${error.localizedMessage ?: "Unknown error"}")
                }
            }
        }
    }

    private fun loadLocally(context: Context) {
        viewModelScope.launch(Dispatchers.IO) {
            val storedJson = runCatching {
                context.taskChartDataStore.data.first()[taskChartJsonPreferenceKey]
            }.getOrElse { error ->
                _uiState.update {
                    it.copy(message = "Load failed: ${error.localizedMessage ?: "Unknown error"}")
                }
                return@launch
            }

            if (storedJson.isNullOrBlank()) {
                _uiState.update { it.copy(message = "No local task chart found") }
                return@launch
            }

            val categories = runCatching { decodeTaskChartPayload(storedJson) }.getOrElse { error ->
                _uiState.update {
                    it.copy(message = "Load failed: ${error.localizedMessage ?: "Invalid saved data"}")
                }
                return@launch
            }

            _uiState.update {
                it.copy(
                    categories = categories.ifEmpty { defaultTaskChart() },
                    selectedCategoryIndex = 0,
                    hasUnsavedChanges = false,
                    message = "Task chart loaded"
                )
            }
        }
    }

    private fun clearMessage() {
        _uiState.update { it.copy(message = null) }
    }
}

sealed interface TaskChartEvent {
    data object ToggleTheme : TaskChartEvent
    data class SelectCategory(val index: Int) : TaskChartEvent
    data class ToggleTaskDone(
        val categoryName: String,
        val taskId: String,
        val done: Boolean
    ) : TaskChartEvent
    data class AddTask(
        val categoryName: String,
        val name: String,
        val priority: TaskPriority
    ) : TaskChartEvent
    data class EditTask(
        val originalCategoryName: String,
        val taskId: String,
        val updatedCategoryName: String,
        val name: String,
        val priority: TaskPriority
    ) : TaskChartEvent
    data class DeleteTask(val categoryName: String, val taskId: String) : TaskChartEvent
    data object ResetStatuses : TaskChartEvent
    data object SaveLocal : TaskChartEvent
    data object LoadLocal : TaskChartEvent
    data object AcknowledgeMessage : TaskChartEvent
}

@Serializable
data class TaskCategoryGroup(
    val name: String,
    val tasks: List<TaskChartItem>
)

@Serializable
data class TaskChartItem(
    val id: String,
    val name: String,
    val priority: TaskPriority,
    val done: Boolean = false
) {
    val status: String
        get() = if (done) STATUS_DONE else STATUS_NOT_DONE
}

@Serializable
enum class TaskPriority {
    @SerialName("High") HIGH,
    @SerialName("Medium") MEDIUM,
    @SerialName("Low") LOW;

    val displayName: String
        get() = when (this) {
            HIGH -> "High"
            MEDIUM -> "Medium"
            LOW -> "Low"
        }

    val rank: Int
        get() = when (this) {
            HIGH -> 1
            MEDIUM -> 2
            LOW -> 3
        }

    companion object {
        fun fromDisplayName(raw: String): TaskPriority {
            return values().firstOrNull { it.displayName.equals(raw, ignoreCase = true) } ?: MEDIUM
        }
    }
}

private const val STATUS_NOT_DONE = "☐ Not done"
private const val STATUS_DONE = "☑ Done"

internal fun buildTaskChartMarkdown(categories: List<TaskCategoryGroup>): String {
    val lines = mutableListOf(
        "# Task Chart",
        "",
        "| Category | Task | Priority | Status |",
        "|---|---|---|---|"
    )

    categories.forEach { category ->
        category.tasks.forEach { task ->
            lines += "| **${escapeMarkdownTableCell(category.name)}** | " +
                "${escapeMarkdownTableCell(task.name)} | ${task.priority.displayName} | ${task.status} |"
        }
    }

    lines += listOf(
        "",
        "## Summary",
        "",
        "| Category | Number of Tasks |",
        "|---|---:|"
    )

    categories.forEach { category ->
        lines += "| **${escapeMarkdownTableCell(category.name)}** | ${category.tasks.size} |"
    }

    return lines.joinToString(separator = "\n", postfix = "\n")
}

internal fun escapeMarkdownTableCell(value: String): String {
    return value
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r\n", "<br>")
        .replace("\n", "<br>")
        .replace("\r", "<br>")
}

internal fun encodeTaskChartPayload(categories: List<TaskCategoryGroup>): String {
    return taskChartJson.encodeToString(TaskChartPayload(categories = categories))
}

internal fun decodeTaskChartPayload(raw: String): List<TaskCategoryGroup> {
    return taskChartJson.decodeFromString<TaskChartPayload>(raw).categories.map { category ->
        category.copy(tasks = sortTasks(category.tasks))
    }
}

private fun progressFor(completed: Int, total: Int): Float {
    return if (total == 0) 0f else completed.toFloat() / total.toFloat()
}

private fun List<TaskCategoryGroup>.withUpdatedCategory(
    categoryName: String,
    transform: (TaskCategoryGroup) -> TaskCategoryGroup
): List<TaskCategoryGroup> {
    return map { category ->
        if (category.name == categoryName) transform(category) else category
    }
}

private fun sortTasks(tasks: List<TaskChartItem>): List<TaskChartItem> {
    return tasks.sortedWith(
        compareBy<TaskChartItem> { it.priority.rank }
            .thenBy { it.name.lowercase() }
    )
}

private fun nextTaskId(categories: List<TaskCategoryGroup>): String {
    val maxId = categories
        .flatMap { it.tasks }
        .mapNotNull { it.id.removePrefix("task-").toIntOrNull() }
        .maxOrNull()
        ?: 0
    return "task-${maxId + 1}"
}

@Serializable
private data class TaskChartPayload(
    val categories: List<TaskCategoryGroup> = defaultTaskChart()
)

private fun defaultTaskChart(): List<TaskCategoryGroup> = listOf(
    TaskCategoryGroup(
        name = "Short-Term",
        tasks = sortTasks(
            listOf(
                TaskChartItem("task-1", "Clean and organize room/work area", TaskPriority.MEDIUM),
                TaskChartItem("task-2", "Buy groceries", TaskPriority.HIGH),
                TaskChartItem("task-3", "Buy supplements/medicine", TaskPriority.HIGH),
                TaskChartItem("task-4", "Do laundry", TaskPriority.MEDIUM),
                TaskChartItem("task-5", "Pay bills", TaskPriority.HIGH),
                TaskChartItem("task-6", "Check bank/credit card charges", TaskPriority.MEDIUM),
                TaskChartItem("task-7", "Schedule gym sessions", TaskPriority.MEDIUM),
                TaskChartItem("task-8", "Prepare meals for the next few days", TaskPriority.MEDIUM),
                TaskChartItem("task-9", "Buy new clothes for gym or social events", TaskPriority.MEDIUM),
                TaskChartItem("task-10", "Buy new shirts for work", TaskPriority.MEDIUM),
                TaskChartItem("task-11", "Buy cleaning spray for glasses", TaskPriority.LOW)
            )
        )
    ),
    TaskCategoryGroup(
        name = "Long-Term",
        tasks = sortTasks(
            listOf(
                TaskChartItem("task-12", "Save money every month", TaskPriority.HIGH),
                TaskChartItem("task-13", "Work on career/job progress", TaskPriority.HIGH),
                TaskChartItem("task-14", "Improve English/Chinese/programming skills", TaskPriority.MEDIUM),
                TaskChartItem("task-15", "Build or improve personal app/project", TaskPriority.MEDIUM),
                TaskChartItem("task-16", "Get a driver's license", TaskPriority.HIGH),
                TaskChartItem("task-17", "Plan future travel", TaskPriority.LOW),
                TaskChartItem("task-18", "Find rental housing — Ashkelon/other city", TaskPriority.HIGH)
            )
        )
    ),
    TaskCategoryGroup(
        name = "House Renovation",
        tasks = sortTasks(
            listOf(
                TaskChartItem("task-19", "Fill gaps/holes between floor tiles", TaskPriority.HIGH),
                TaskChartItem("task-20", "Seal shower with silicone", TaskPriority.HIGH),
                TaskChartItem("task-21", "Paint walls", TaskPriority.MEDIUM),
                TaskChartItem("task-22", "Check bathroom water leaks", TaskPriority.HIGH),
                TaskChartItem("task-23", "Buy renovation supplies", TaskPriority.HIGH)
            )
        )
    )
)
