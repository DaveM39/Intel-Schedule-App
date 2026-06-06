package com.example.schedule.ui

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.EventNote
import androidx.compose.material.icons.filled.Checklist
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.example.schedule.ScheduleEvent
import com.example.schedule.ScheduleUiState
import com.example.schedule.TaskChartEvent
import com.example.schedule.TaskChartUiState

enum class AppSection {
    PLANNER,
    TASKS
}

@Composable
fun ScheduleSuiteApp(
    scheduleState: ScheduleUiState,
    taskChartState: TaskChartUiState,
    onScheduleEvent: (ScheduleEvent) -> Unit,
    onTaskChartEvent: (TaskChartEvent) -> Unit,
    onExportSchedule: () -> Unit,
    onImportSchedule: () -> Unit,
    onExportTaskChart: () -> Unit
) {
    var selectedSection by rememberSaveable { mutableStateOf(AppSection.PLANNER) }

    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = selectedSection == AppSection.PLANNER,
                    onClick = { selectedSection = AppSection.PLANNER },
                    icon = { Icon(Icons.AutoMirrored.Filled.EventNote, contentDescription = null) },
                    label = { Text("Planner") }
                )
                NavigationBarItem(
                    selected = selectedSection == AppSection.TASKS,
                    onClick = { selectedSection = AppSection.TASKS },
                    icon = { Icon(Icons.Filled.Checklist, contentDescription = null) },
                    label = { Text("Tasks") }
                )
            }
        }
    ) { paddingValues ->
        Box(modifier = Modifier.padding(paddingValues)) {
            when (selectedSection) {
                AppSection.PLANNER -> ScheduleApp(
                    state = scheduleState,
                    onEvent = onScheduleEvent,
                    onExportJson = onExportSchedule,
                    onImportJson = onImportSchedule
                )
                AppSection.TASKS -> TaskChartApp(
                    state = taskChartState,
                    onEvent = onTaskChartEvent,
                    onExportMarkdown = onExportTaskChart
                )
            }
        }
    }
}
