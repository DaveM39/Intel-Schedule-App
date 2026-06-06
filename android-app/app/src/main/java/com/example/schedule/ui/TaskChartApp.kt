package com.example.schedule.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.LightMode
import androidx.compose.material.icons.filled.RestartAlt
import androidx.compose.material.icons.filled.Save
import androidx.compose.material.icons.outlined.Download
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.luminance
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.example.schedule.TaskCategoryGroup
import com.example.schedule.TaskChartEvent
import com.example.schedule.TaskChartItem
import com.example.schedule.TaskChartUiState
import com.example.schedule.TaskPriority
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TaskChartApp(
    state: TaskChartUiState,
    onEvent: (TaskChartEvent) -> Unit,
    onExportMarkdown: () -> Unit
) {
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()
    var pendingEdit by remember { mutableStateOf<TaskEditRequest?>(null) }
    var pendingDelete by remember { mutableStateOf<TaskDeleteRequest?>(null) }
    var showResetDialog by rememberSaveable { mutableStateOf(false) }

    LaunchedEffect(state.message) {
        state.message?.let { message ->
            coroutineScope.launch { snackbarHostState.showSnackbar(message) }
            onEvent(TaskChartEvent.AcknowledgeMessage)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "Task Chart",
                            style = MaterialTheme.typography.titleLarge,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        Text(
                            text = "${state.completedTasks}/${state.totalTasks} done",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { onEvent(TaskChartEvent.ToggleTheme) }) {
                        Icon(
                            imageVector = if (state.isDarkTheme) Icons.Filled.LightMode else Icons.Filled.DarkMode,
                            contentDescription = "Toggle theme"
                        )
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .padding(16.dp)
                .fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            TaskActionRow(
                onAdd = {
                    pendingEdit = TaskEditRequest(
                        originalCategoryName = state.selectedCategory.name,
                        task = null
                    )
                },
                onSave = { onEvent(TaskChartEvent.SaveLocal) },
                onLoad = { onEvent(TaskChartEvent.LoadLocal) },
                onExportMarkdown = onExportMarkdown,
                onReset = { showResetDialog = true }
            )

            ProgressSummary(state = state)

            TabRow(selectedTabIndex = state.selectedCategoryIndex) {
                state.categories.forEachIndexed { index, category ->
                    Tab(
                        selected = index == state.selectedCategoryIndex,
                        onClick = { onEvent(TaskChartEvent.SelectCategory(index)) },
                        text = {
                            Text(
                                text = "${category.name} (${category.tasks.size})",
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    )
                }
            }

            TaskList(
                category = state.selectedCategory,
                onToggleTask = { task, done ->
                    onEvent(
                        TaskChartEvent.ToggleTaskDone(
                            categoryName = state.selectedCategory.name,
                            taskId = task.id,
                            done = done
                        )
                    )
                },
                onEditTask = { task ->
                    pendingEdit = TaskEditRequest(
                        originalCategoryName = state.selectedCategory.name,
                        task = task
                    )
                },
                onDeleteTask = { task ->
                    pendingDelete = TaskDeleteRequest(
                        categoryName = state.selectedCategory.name,
                        task = task
                    )
                },
                modifier = Modifier.weight(1f)
            )
        }
    }

    pendingEdit?.let { request ->
        TaskEditDialog(
            request = request,
            categories = state.categories,
            onDismiss = { pendingEdit = null },
            onSave = { categoryName, name, priority ->
                val task = request.task
                if (task == null) {
                    onEvent(TaskChartEvent.AddTask(categoryName, name, priority))
                } else {
                    onEvent(
                        TaskChartEvent.EditTask(
                            originalCategoryName = request.originalCategoryName,
                            taskId = task.id,
                            updatedCategoryName = categoryName,
                            name = name,
                            priority = priority
                        )
                    )
                }
                pendingEdit = null
            }
        )
    }

    pendingDelete?.let { request ->
        AlertDialog(
            onDismissRequest = { pendingDelete = null },
            confirmButton = {
                TextButton(
                    onClick = {
                        onEvent(TaskChartEvent.DeleteTask(request.categoryName, request.task.id))
                        pendingDelete = null
                    }
                ) {
                    Text("Delete")
                }
            },
            dismissButton = {
                TextButton(onClick = { pendingDelete = null }) { Text("Cancel") }
            },
            title = { Text("Delete task?") },
            text = { Text("Remove \"${request.task.name}\" from ${request.categoryName}?") }
        )
    }

    if (showResetDialog) {
        AlertDialog(
            onDismissRequest = { showResetDialog = false },
            confirmButton = {
                TextButton(
                    onClick = {
                        onEvent(TaskChartEvent.ResetStatuses)
                        showResetDialog = false
                    }
                ) {
                    Text("Reset")
                }
            },
            dismissButton = {
                TextButton(onClick = { showResetDialog = false }) { Text("Cancel") }
            },
            title = { Text("Reset status?") },
            text = { Text("Mark every task as not done.") }
        )
    }
}

@Composable
private fun TaskActionRow(
    onAdd: () -> Unit,
    onSave: () -> Unit,
    onLoad: () -> Unit,
    onExportMarkdown: () -> Unit,
    onReset: () -> Unit
) {
    Row(
        modifier = Modifier.horizontalScroll(rememberScrollState()),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Button(onClick = onAdd) {
            Icon(Icons.Filled.Add, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("Add Task")
        }
        OutlinedButton(onClick = onSave) {
            Icon(Icons.Filled.Save, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("Save Local")
        }
        OutlinedButton(onClick = onLoad) {
            Icon(Icons.Outlined.Download, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("Load Local")
        }
        OutlinedButton(onClick = onExportMarkdown) {
            Text("Export Markdown")
        }
        OutlinedButton(onClick = onReset) {
            Icon(Icons.Filled.RestartAlt, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("Reset Status")
        }
    }
}

@Composable
private fun ProgressSummary(state: TaskChartUiState) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(8.dp),
        tonalElevation = 2.dp,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Summary", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text(
                    text = "${(state.completionProgress * 100).toInt()}%",
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            LinearProgressIndicator(
                progress = { state.completionProgress },
                modifier = Modifier.fillMaxWidth()
            )
            state.summaries.forEach { summary ->
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(summary.categoryName, style = MaterialTheme.typography.bodyMedium)
                        Text("${summary.completed}/${summary.total}", style = MaterialTheme.typography.bodyMedium)
                    }
                    LinearProgressIndicator(
                        progress = { summary.progress },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }
        }
    }
}

@Composable
private fun TaskList(
    category: TaskCategoryGroup,
    onToggleTask: (TaskChartItem, Boolean) -> Unit,
    onEditTask: (TaskChartItem) -> Unit,
    onDeleteTask: (TaskChartItem) -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        LazyColumn(modifier = Modifier.fillMaxSize()) {
            items(category.tasks, key = { it.id }) { task ->
                TaskRow(
                    task = task,
                    onCheckedChange = { done -> onToggleTask(task, done) },
                    onEdit = { onEditTask(task) },
                    onDelete = { onDeleteTask(task) }
                )
                HorizontalDivider()
            }
        }
    }
}

@Composable
private fun TaskRow(
    task: TaskChartItem,
    onCheckedChange: (Boolean) -> Unit,
    onEdit: () -> Unit,
    onDelete: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 12.dp, vertical = 10.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Checkbox(
            checked = task.done,
            onCheckedChange = onCheckedChange
        )
        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Text(
                text = task.name,
                style = MaterialTheme.typography.bodyLarge,
                textDecoration = if (task.done) TextDecoration.LineThrough else TextDecoration.None,
                color = if (task.done) MaterialTheme.colorScheme.onSurfaceVariant else MaterialTheme.colorScheme.onSurface
            )
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                PriorityChip(priority = task.priority)
                Text(
                    text = task.status,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
        IconButton(onClick = onEdit) {
            Icon(Icons.Filled.Edit, contentDescription = "Edit ${task.name}")
        }
        IconButton(onClick = onDelete) {
            Icon(Icons.Filled.Delete, contentDescription = "Delete ${task.name}")
        }
    }
}

@Composable
private fun PriorityChip(priority: TaskPriority) {
    val background = priorityColor(priority)
    Surface(
        shape = RoundedCornerShape(8.dp),
        color = background,
        contentColor = background.readableContentColor()
    ) {
        Text(
            text = priority.displayName,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            style = MaterialTheme.typography.labelLarge
        )
    }
}

@Composable
private fun TaskEditDialog(
    request: TaskEditRequest,
    categories: List<TaskCategoryGroup>,
    onDismiss: () -> Unit,
    onSave: (String, String, TaskPriority) -> Unit
) {
    val task = request.task
    var name by rememberSaveable(request.originalCategoryName, task?.id) {
        mutableStateOf(task?.name.orEmpty())
    }
    var categoryName by rememberSaveable(request.originalCategoryName, task?.id) {
        mutableStateOf(request.originalCategoryName)
    }
    var priorityName by rememberSaveable(request.originalCategoryName, task?.id) {
        mutableStateOf(task?.priority?.displayName ?: TaskPriority.MEDIUM.displayName)
    }
    var categoryExpanded by remember { mutableStateOf(false) }
    var priorityExpanded by remember { mutableStateOf(false) }
    val trimmedName = name.trim()
    val isFormValid = trimmedName.isNotEmpty()

    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            TextButton(
                onClick = {
                    if (isFormValid) {
                        onSave(categoryName, trimmedName, TaskPriority.fromDisplayName(priorityName))
                    }
                },
                enabled = isFormValid
            ) {
                Text("Save")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancel") }
        },
        title = { Text(if (task == null) "Add Task" else "Edit Task") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("Task Name") },
                    isError = !isFormValid,
                    singleLine = false,
                    modifier = Modifier.fillMaxWidth()
                )
                DropdownField(
                    label = "Category",
                    value = categoryName,
                    expanded = categoryExpanded,
                    onExpandedChange = { categoryExpanded = it },
                    options = categories.map { it.name },
                    onSelect = { categoryName = it }
                )
                DropdownField(
                    label = "Priority",
                    value = priorityName,
                    expanded = priorityExpanded,
                    onExpandedChange = { priorityExpanded = it },
                    options = TaskPriority.values().map { it.displayName },
                    onSelect = { priorityName = it }
                )
            }
        }
    )
}

@Composable
private fun DropdownField(
    label: String,
    value: String,
    expanded: Boolean,
    onExpandedChange: (Boolean) -> Unit,
    options: List<String>,
    onSelect: (String) -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(label, style = MaterialTheme.typography.labelLarge)
        Box(modifier = Modifier.fillMaxWidth()) {
            OutlinedButton(
                onClick = { onExpandedChange(true) },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = value,
                    modifier = Modifier.fillMaxWidth(),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }
            DropdownMenu(
                expanded = expanded,
                onDismissRequest = { onExpandedChange(false) }
            ) {
                options.forEach { option ->
                    DropdownMenuItem(
                        text = { Text(option) },
                        onClick = {
                            onSelect(option)
                            onExpandedChange(false)
                        }
                    )
                }
            }
        }
    }
}

private data class TaskEditRequest(
    val originalCategoryName: String,
    val task: TaskChartItem?
)

private data class TaskDeleteRequest(
    val categoryName: String,
    val task: TaskChartItem
)

private fun priorityColor(priority: TaskPriority): Color {
    return when (priority) {
        TaskPriority.HIGH -> Color(0xFFFFDAD6)
        TaskPriority.MEDIUM -> Color(0xFFFFE8A3)
        TaskPriority.LOW -> Color(0xFFCDEFD8)
    }
}

private fun Color.readableContentColor(): Color {
    return if (luminance() > 0.5f) Color(0xFF1C1B1F) else Color.White
}
