package com.example.schedule.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.LightMode
import androidx.compose.material.icons.filled.RestartAlt
import androidx.compose.material.icons.filled.Save
import androidx.compose.material.icons.outlined.Download
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.AssistChip
import androidx.compose.material3.AssistChipDefaults
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextFieldDefaults
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
import androidx.compose.material3.rememberDatePickerState
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
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import com.example.schedule.ActivityEntry
import com.example.schedule.ScheduleCategory
import com.example.schedule.ScheduleEvent
import com.example.schedule.ScheduleUiState
import com.example.schedule.WorkMode
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScheduleApp(
    state: ScheduleUiState,
    onEvent: (ScheduleEvent) -> Unit,
    onExportJson: () -> Unit,
    onImportJson: () -> Unit
) {
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()
    var showDatePicker by rememberSaveable { mutableStateOf(false) }
    var showNameDialog by rememberSaveable { mutableStateOf(false) }
    var showCalendar by rememberSaveable { mutableStateOf(false) }
    var pendingEdit by remember { mutableStateOf<ActivityEditRequest?>(null) }
    var pendingDelete by remember { mutableStateOf<ActivityDeleteRequest?>(null) }
    var pendingReset by remember { mutableStateOf<ResetDayRequest?>(null) }

    LaunchedEffect(state.message) {
        state.message?.let { message ->
            coroutineScope.launch { snackbarHostState.showSnackbar(message) }
            onEvent(ScheduleEvent.AcknowledgeMessage)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column(modifier = Modifier.fillMaxWidth()) {
                        Text(
                            text = state.title,
                            style = MaterialTheme.typography.titleLarge,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        Text(
                            text = "Start of off-cycle: ${state.startDateLabel}",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { onEvent(ScheduleEvent.ToggleTheme) }) {
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
                .fillMaxSize()
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                OutlinedButton(onClick = { showDatePicker = true }) {
                    Text("Set off-cycle date")
                }
                TextButton(onClick = { showNameDialog = true }) {
                    Text(if (state.userName.isBlank()) "Set name" else "Update name")
                }
            }

            WorkModeRow(
                selected = state.workMode,
                predictedLabel = state.predictedTodayDayLabel,
                onSelectMode = { mode -> onEvent(ScheduleEvent.UpdateWorkMode(mode)) },
                onSelectPredictedDay = { onEvent(ScheduleEvent.SelectPredictedDay) }
            )

            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Button(onClick = { onEvent(ScheduleEvent.SaveSchedule) }) {
                    Icon(Icons.Filled.Save, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text("Save Local")
                }
                OutlinedButton(onClick = { onEvent(ScheduleEvent.LoadSchedule) }) {
                    Icon(Icons.Outlined.Download, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text("Load Local")
                }
                OutlinedButton(onClick = onExportJson) {
                    Text("Export JSON")
                }
                OutlinedButton(onClick = onImportJson) {
                    Text("Import JSON")
                }
                OutlinedButton(onClick = {
                    onEvent(ScheduleEvent.GoToTodayOnCalendar)
                    showCalendar = true
                }) {
                    Icon(Icons.Filled.CalendarMonth, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text("Yearly calendar")
                }
            }

            CycleSummaryCard(lines = state.cycleSummary)

            TabRow(selectedTabIndex = state.selectedDayIndex) {
                state.days.forEachIndexed { index, day ->
                    Tab(
                        selected = index == state.selectedDayIndex,
                        onClick = { onEvent(ScheduleEvent.SelectDay(index)) },
                        text = { Text("Day ${day.id}") }
                    )
                }
            }

            Text(
                text = state.selectedDay.title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )

            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Button(
                    onClick = {
                        pendingEdit = ActivityEditRequest(
                            dayId = state.selectedDay.id,
                            activityIndex = -1,
                            original = ActivityEntry("", "", ScheduleCategory.MORNING),
                            isNew = true
                        )
                    }
                ) {
                    Icon(Icons.Filled.Add, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text("Add activity")
                }
                OutlinedButton(
                    onClick = {
                        pendingReset = ResetDayRequest(
                            dayId = state.selectedDay.id,
                            dayTitle = state.selectedDay.title
                        )
                    }
                ) {
                    Icon(Icons.Filled.RestartAlt, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text("Reset day")
                }
            }

            LegendRow(
                selected = state.activeFilter,
                onFilter = { category -> onEvent(ScheduleEvent.FilterByCategory(category)) },
                clearFilter = { onEvent(ScheduleEvent.ClearFilter) }
            )

            val activitiesToShow = remember(state.selectedDay, state.activeFilter) {
                val all = state.selectedDay.activities
                if (state.activeFilter == null) {
                    all.mapIndexed { idx, entry -> idx to entry }
                } else {
                    all.mapIndexedNotNull { idx, entry ->
                        if (entry.category == state.activeFilter) idx to entry else null
                    }
                }
            }

            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = 220.dp, max = 420.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                LazyColumn(modifier = Modifier.fillMaxSize()) {
                    itemsIndexed(activitiesToShow) { displayIndex, (originalIndex, activity) ->
                        ActivityRow(
                            entry = activity,
                            onEdit = {
                                pendingEdit = ActivityEditRequest(
                                    dayId = state.selectedDay.id,
                                    activityIndex = originalIndex,
                                    original = activity,
                                    isNew = false
                                )
                            },
                            onDelete = {
                                pendingDelete = ActivityDeleteRequest(
                                    dayId = state.selectedDay.id,
                                    activityIndex = originalIndex,
                                    activityLabel = activity.description
                                )
                            }
                        )
                        if (displayIndex < activitiesToShow.lastIndex) {
                            HorizontalDivider()
                        }
                    }
                }
            }

            NotesSection(
                value = state.notes,
                onValueChange = { onEvent(ScheduleEvent.UpdateNotes(it)) },
                hasUnsavedChanges = state.hasUnsavedChanges
            )
        }
    }

    if (showDatePicker) {
        val datePickerState = rememberDatePickerState(
            initialSelectedDateMillis = state.startDate.atStartOfDay(ZoneId.systemDefault()).toInstant().toEpochMilli()
        )
        DatePickerDialog(
            onDismissRequest = { showDatePicker = false },
            confirmButton = {
                TextButton(onClick = {
                    val millis = datePickerState.selectedDateMillis
                    if (millis != null) {
                        val pickedDate = Instant.ofEpochMilli(millis).atZone(ZoneId.systemDefault()).toLocalDate()
                        onEvent(ScheduleEvent.UpdateStartDate(pickedDate))
                    }
                    showDatePicker = false
                }) {
                    Text("Confirm")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDatePicker = false }) {
                    Text("Cancel")
                }
            }
        ) {
            DatePicker(state = datePickerState)
        }
    }

    if (showNameDialog) {
        NameDialog(
            currentName = state.userName,
            onConfirm = { name ->
                onEvent(ScheduleEvent.UpdateUserName(name))
                showNameDialog = false
            },
            onDismiss = { showNameDialog = false }
        )
    }

    if (showCalendar) {
        YearlyCalendarDialog(
            startDate = state.startDate,
            targetYear = state.calendarYear,
            isDarkTheme = state.isDarkTheme,
            onClose = { showCalendar = false },
            onYearChange = { delta -> onEvent(ScheduleEvent.ChangeCalendarYear(delta)) },
            onToday = { onEvent(ScheduleEvent.GoToTodayOnCalendar) }
        )
    }

    pendingEdit?.let { request ->
        ActivityEditDialog(
            request = request,
            onDismiss = { pendingEdit = null },
            onSave = { updated ->
                if (request.isNew) {
                    onEvent(
                        ScheduleEvent.AddActivity(
                            dayId = request.dayId,
                            entry = updated
                        )
                    )
                } else {
                    onEvent(
                        ScheduleEvent.CommitActivityEdit(
                            dayId = request.dayId,
                            activityIndex = request.activityIndex,
                            entry = updated
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
                        onEvent(
                            ScheduleEvent.DeleteActivity(
                                dayId = request.dayId,
                                activityIndex = request.activityIndex
                            )
                        )
                        pendingDelete = null
                    }
                ) {
                    Text("Delete")
                }
            },
            dismissButton = {
                TextButton(onClick = { pendingDelete = null }) { Text("Cancel") }
            },
            title = { Text("Delete activity?") },
            text = { Text("Remove \"${request.activityLabel}\" from Day ${request.dayId}?") }
        )
    }

    pendingReset?.let { request ->
        AlertDialog(
            onDismissRequest = { pendingReset = null },
            confirmButton = {
                TextButton(
                    onClick = {
                        onEvent(ScheduleEvent.ResetDay(dayId = request.dayId))
                        pendingReset = null
                    }
                ) {
                    Text("Reset")
                }
            },
            dismissButton = {
                TextButton(onClick = { pendingReset = null }) { Text("Cancel") }
            },
            title = { Text("Reset day?") },
            text = { Text("Restore default activities for ${request.dayTitle}.") }
        )
    }
}

@Composable
private fun CycleSummaryCard(lines: List<String>) {
    Card(shape = RoundedCornerShape(12.dp)) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("Current cycle", style = MaterialTheme.typography.titleMedium)
            lines.forEach { line ->
                Text(text = line, style = MaterialTheme.typography.bodyMedium)
            }
        }
    }
}

@Composable
private fun WorkModeRow(
    selected: WorkMode,
    predictedLabel: String,
    onSelectMode: (WorkMode) -> Unit,
    onSelectPredictedDay: () -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(text = "On-cycle mode", style = MaterialTheme.typography.labelLarge)
        Row(
            modifier = Modifier.horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            WorkMode.values().forEach { mode ->
                val isSelected = selected == mode
                AssistChip(
                    label = {
                        Text(
                            text = mode.displayName,
                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                        )
                    },
                    onClick = { onSelectMode(mode) },
                    colors = AssistChipDefaults.assistChipColors(
                        containerColor = if (isSelected)
                            MaterialTheme.colorScheme.primary.copy(alpha = 0.15f) else MaterialTheme.colorScheme.surface,
                        labelColor = if (isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                    ),
                    border = BorderStroke(
                        width = 1.dp,
                        color = if (isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline
                    )
                )
            }
            TextButton(onClick = onSelectPredictedDay) { Text("Go to predicted") }
        }
        Text(
            text = predictedLabel,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun LegendRow(
    selected: ScheduleCategory?,
    onFilter: (ScheduleCategory?) -> Unit,
    clearFilter: () -> Unit
) {
    Column {
        Text(text = "Filter by", style = MaterialTheme.typography.labelLarge)
        Spacer(Modifier.height(8.dp))
        Row(
            modifier = Modifier.horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ScheduleCategory.values().forEach { category ->
                val isSelected = selected == category
                val swatchColor = categoryColor(category)
                AssistChip(
                    label = {
                        Text(
                            text = category.displayName,
                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                        )
                    },
                    onClick = { onFilter(category) },
                    leadingIcon = {
                        Box(
                            modifier = Modifier
                                .background(
                                    color = swatchColor,
                                    shape = RoundedCornerShape(50)
                                )
                                .height(16.dp)
                                .width(16.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            if (isSelected) {
                                Text(
                                    text = "✓",
                                    color = swatchColor.contentColor(),
                                    style = MaterialTheme.typography.labelSmall
                                )
                            }
                        }
                    },
                    colors = AssistChipDefaults.assistChipColors(
                        containerColor = if (isSelected)
                            MaterialTheme.colorScheme.primary.copy(alpha = 0.15f) else MaterialTheme.colorScheme.surface,
                        labelColor = if (isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                    ),
                    border = BorderStroke(
                        width = 1.dp,
                        color = if (isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline
                    )
                )
            }
            TextButton(onClick = clearFilter) { Text("Clear") }
        }
    }
}

@Composable
private fun ActivityRow(
    entry: ActivityEntry,
    onEdit: () -> Unit,
    onDelete: () -> Unit
) {
    val background = categoryColor(entry.category)
    val contentColor = background.contentColor()
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(color = background)
            .clickable(onClick = onEdit)
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(text = entry.time, style = MaterialTheme.typography.labelLarge, color = contentColor)
            Text(text = entry.description, style = MaterialTheme.typography.bodyMedium, color = contentColor)
        }
        Row(horizontalArrangement = Arrangement.spacedBy(4.dp), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onEdit) {
                Icon(
                    imageVector = Icons.Filled.Edit,
                    contentDescription = "Edit ${entry.description}",
                    tint = contentColor
                )
            }
            IconButton(onClick = onDelete) {
                Icon(
                    imageVector = Icons.Filled.Delete,
                    contentDescription = "Delete ${entry.description}",
                    tint = contentColor
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun NotesSection(
    value: String,
    onValueChange: (String) -> Unit,
    hasUnsavedChanges: Boolean
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Personal notes", style = MaterialTheme.typography.titleMedium)
            if (hasUnsavedChanges) {
                Text("Unsaved", color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodySmall)
            }
        }
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier
                .fillMaxWidth()
                .heightIn(min = 140.dp),
            placeholder = { Text("This is a scratchpad for any notes you want to keep.") },
            colors = OutlinedTextFieldDefaults.colors()
        )
    }
}

private data class ActivityEditRequest(
    val dayId: String,
    val activityIndex: Int,
    val original: ActivityEntry,
    val isNew: Boolean
)

private data class ActivityDeleteRequest(
    val dayId: String,
    val activityIndex: Int,
    val activityLabel: String
)

private data class ResetDayRequest(
    val dayId: String,
    val dayTitle: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ActivityEditDialog(
    request: ActivityEditRequest,
    onDismiss: () -> Unit,
    onSave: (ActivityEntry) -> Unit
) {
    var time by rememberSaveable(request.dayId, request.activityIndex, request.isNew) {
        mutableStateOf(request.original.time)
    }
    var description by rememberSaveable(request.dayId, request.activityIndex, request.isNew) {
        mutableStateOf(request.original.description)
    }
    var expanded by remember { mutableStateOf(false) }
    var category by rememberSaveable(request.dayId, request.activityIndex, request.isNew) {
        mutableStateOf(request.original.category)
    }
    val trimmedTime = time.trim()
    val trimmedDescription = description.trim()
    val isTimeValid = trimmedTime.isNotEmpty()
    val isDescriptionValid = trimmedDescription.isNotEmpty()
    val isFormValid = isTimeValid && isDescriptionValid

    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            TextButton(
                onClick = {
                    if (isFormValid) {
                        onSave(
                            ActivityEntry(
                                time = trimmedTime,
                                description = trimmedDescription,
                                category = category
                            )
                        )
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
        title = { Text(if (request.isNew) "Add activity" else "Edit activity") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = time,
                    onValueChange = { time = it },
                    label = { Text("Time") },
                    isError = !isTimeValid,
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                    supportingText = {
                        if (!isTimeValid) {
                            Text("Required", style = MaterialTheme.typography.bodySmall)
                        }
                    }
                )
                OutlinedTextField(
                    value = description,
                    onValueChange = { description = it },
                    label = { Text("Activity") },
                    isError = !isDescriptionValid,
                    modifier = Modifier.fillMaxWidth(),
                    supportingText = {
                        if (!isDescriptionValid) {
                            Text("Required", style = MaterialTheme.typography.bodySmall)
                        }
                    }
                )
                ExposedDropdownMenuBox(expanded = expanded, onExpandedChange = { expanded = !expanded }) {
                    Box(modifier = Modifier.fillMaxWidth()) {
                        OutlinedButton(
                            onClick = { expanded = !expanded },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                text = "Category: ${category.displayName}",
                                modifier = Modifier.fillMaxWidth()
                            )
                        }
                        DropdownMenu(
                            expanded = expanded,
                            onDismissRequest = { expanded = false }
                        ) {
                            ScheduleCategory.values().forEach { option ->
                                DropdownMenuItem(
                                    text = { Text(option.displayName) },
                                    onClick = {
                                        category = option
                                        expanded = false
                                    }
                                )
                            }
                        }
                    }
                }
            }
        }
    )
}

@Composable
private fun NameDialog(
    currentName: String,
    onConfirm: (String) -> Unit,
    onDismiss: () -> Unit
) {
    var firstName by rememberSaveable { mutableStateOf("") }
    var lastName by rememberSaveable { mutableStateOf("") }

    LaunchedEffect(currentName) {
        if (currentName.isNotBlank()) {
            val parts = currentName.split(" ", limit = 2)
            firstName = parts.getOrNull(0) ?: ""
            lastName = parts.getOrNull(1) ?: ""
        }
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            TextButton(onClick = { onConfirm("$firstName $lastName".trim()) }) {
                Text("Save")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Cancel") }
        },
        title = { Text("Set your name") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = firstName,
                    onValueChange = { firstName = it },
                    label = { Text("First name") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )
                OutlinedTextField(
                    value = lastName,
                    onValueChange = { lastName = it },
                    label = { Text("Last name") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
    )
}

@Composable
private fun YearlyCalendarDialog(
    startDate: LocalDate,
    targetYear: Int,
    isDarkTheme: Boolean,
    onClose: () -> Unit,
    onYearChange: (Int) -> Unit,
    onToday: () -> Unit
) {
    val configuration = LocalConfiguration.current
    val monthColumns = calendarMonthColumnCount(configuration.screenWidthDp)
    val months = (1..12).chunked(monthColumns)
    val offBackground = Color(0xFFFFFFFF)
    val onEarlyBackground = Color(0xFFFFF200)
    val onLateBackground = Color(0xFFFF9900)
    val todayHighlight = if (isDarkTheme) Color(0xFF55502A) else Color(0xFFFFFACD)

    Dialog(onDismissRequest = onClose) {
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .heightIn(max = configuration.screenHeightDp.dp * 0.92f),
            shape = RoundedCornerShape(24.dp),
            tonalElevation = 6.dp
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text("$targetYear Calendar", style = MaterialTheme.typography.titleLarge)

                Row(
                    modifier = Modifier.horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    OutlinedButton(onClick = { onYearChange(-1) }) { Text("Previous") }
                    OutlinedButton(onClick = { onYearChange(1) }) { Text("Next") }
                    TextButton(onClick = onToday) { Text("Today") }
                    TextButton(onClick = onClose) { Text("Close") }
                }

                Row(
                    modifier = Modifier.horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    CalendarLegendItem(color = offBackground, label = "Off-Cycle")
                    CalendarLegendItem(color = onEarlyBackground, label = "On-Cycle (Day)")
                    CalendarLegendItem(color = onLateBackground, label = "On-Cycle (Night)")
                }

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState()),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    months.forEach { rowMonths ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            rowMonths.forEach { month ->
                                CalendarMonth(
                                    month = month,
                                    year = targetYear,
                                    startDate = startDate,
                                    offColor = offBackground,
                                    onEarlyColor = onEarlyBackground,
                                    onLateColor = onLateBackground,
                                    todayColor = todayHighlight,
                                    modifier = Modifier.weight(1f)
                                )
                            }
                            repeat(monthColumns - rowMonths.size) {
                                Spacer(modifier = Modifier.weight(1f))
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun CalendarLegendItem(
    color: Color,
    label: String
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Box(
            modifier = Modifier
                .background(color = color, shape = RoundedCornerShape(2.dp))
                .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(2.dp))
                .height(12.dp)
                .width(12.dp)
        )
        Text(text = label, style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
private fun CalendarMonth(
    month: Int,
    year: Int,
    startDate: LocalDate,
    offColor: Color,
    onEarlyColor: Color,
    onLateColor: Color,
    todayColor: Color,
    modifier: Modifier = Modifier
) {
    val monthName = DateTimeFormatter.ofPattern("MMMM").format(LocalDate.of(year, month, 1))
    val calendar = generateCalendar(year, month)
    Card(modifier = modifier) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Text(monthName, style = MaterialTheme.typography.titleSmall)
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                listOf("Su", "Mo", "Tu", "We", "Th", "Fr", "Sa").forEach { dayAbbrev ->
                    Text(dayAbbrev, style = MaterialTheme.typography.labelSmall, modifier = Modifier.weight(1f))
                }
            }
            calendar.forEach { week ->
                Row(modifier = Modifier.fillMaxWidth()) {
                    week.forEach { date ->
                        val isCurrentMonth = date.monthValue == month
                        val background = if (!isCurrentMonth) Color.Transparent else {
                            val delta = ChronoUnit.DAYS.between(startDate, date).toInt()
                            val position = Math.floorMod(delta, 8)
                            when {
                                date == LocalDate.now() -> todayColor
                                position in 0..3 -> offColor
                                position in 4..5 -> onEarlyColor
                                else -> onLateColor
                            }
                        }
                        val textColor = if (background == Color.Transparent) {
                            MaterialTheme.colorScheme.onSurfaceVariant
                        } else {
                            background.contentColor()
                        }
                        Box(
                            modifier = Modifier
                                .weight(1f)
                                .padding(2.dp)
                                .background(background, shape = RoundedCornerShape(4.dp))
                                .height(32.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = date.dayOfMonth.toString(),
                                style = MaterialTheme.typography.bodySmall,
                                color = if (isCurrentMonth) textColor else MaterialTheme.colorScheme.outline
                            )
                        }
                    }
                }
            }
        }
    }
}

internal fun generateCalendar(year: Int, month: Int): List<List<LocalDate>> {
    val firstDay = LocalDate.of(year, month, 1)
    val lastDay = firstDay.withDayOfMonth(firstDay.lengthOfMonth())
    val start = firstDay.minusDays(firstDay.dayOfWeek.value % 7L)
    val trailingDays = 6 - (lastDay.dayOfWeek.value % 7)
    val end = lastDay.plusDays(trailingDays.toLong())
    val dayCount = ChronoUnit.DAYS.between(start, end).toInt() + 1
    return (0 until dayCount).map { offset -> start.plusDays(offset.toLong()) }.chunked(7)
}

private fun calendarMonthColumnCount(screenWidthDp: Int): Int {
    return when {
        screenWidthDp < 600 -> 1
        screenWidthDp < 960 -> 2
        else -> 3
    }
}

private val categoryPalette: Map<ScheduleCategory, Color> = mapOf(
    ScheduleCategory.SLEEP to Color(0xFFD0E8FF),
    ScheduleCategory.MORNING to Color(0xFFCFF5E7),
    ScheduleCategory.AFTERNOON to Color(0xFFFFE5B4),
    ScheduleCategory.EVENING to Color(0xFFFFC1C1),
    ScheduleCategory.MEDICINE to Color(0xFFF7B5B8),
    ScheduleCategory.GYM to Color(0xFFE0D4FD),
    ScheduleCategory.CODING to Color(0xFFC7E6FF),
    ScheduleCategory.MEAL to Color(0xFFFFF8B8)
)

@Composable
private fun categoryColor(category: ScheduleCategory): Color {
    return categoryPalette[category] ?: MaterialTheme.colorScheme.surfaceVariant
}

@Composable
private fun Color.contentColor(): Color {
    return if (!isSpecified || this == Color.Transparent) {
        MaterialTheme.colorScheme.onSurface
    } else {
        if (luminance() > 0.5f) Color.Black else Color.White
    }
}

private val Color.isSpecified: Boolean
    get() = this != Color.Unspecified
