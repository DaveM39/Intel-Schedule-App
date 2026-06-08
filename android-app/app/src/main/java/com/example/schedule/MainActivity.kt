package com.example.schedule

import android.os.Bundle
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.schedule.ui.ScheduleSuiteApp
import com.example.schedule.ui.theme.ScheduleTheme

class MainActivity : ComponentActivity() {
    private val scheduleViewModel: ScheduleViewModel by viewModels()
    private val taskChartViewModel: TaskChartViewModel by viewModels()
    private lateinit var scheduleExportLauncher: ActivityResultLauncher<String>
    private lateinit var scheduleImportLauncher: ActivityResultLauncher<Array<String>>
    private lateinit var taskChartExportLauncher: ActivityResultLauncher<String>

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        scheduleExportLauncher =
            registerForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
                if (uri != null) {
                    scheduleViewModel.exportScheduleToUri(applicationContext, uri)
                }
            }
        scheduleImportLauncher = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
            if (uri != null) {
                scheduleViewModel.importScheduleFromUri(applicationContext, uri)
            }
        }
        taskChartExportLauncher =
            registerForActivityResult(ActivityResultContracts.CreateDocument("text/markdown")) { uri ->
                if (uri != null) {
                    taskChartViewModel.exportMarkdownToUri(applicationContext, uri)
                }
            }

        setContent {
            val scheduleState by scheduleViewModel.uiState.collectAsStateWithLifecycle()
            val taskChartState by taskChartViewModel.uiState.collectAsStateWithLifecycle()
            ScheduleTheme(darkTheme = scheduleState.isDarkTheme) {
                ScheduleSuiteApp(
                    scheduleState = scheduleState,
                    taskChartState = taskChartState,
                    onScheduleEvent = ::handleScheduleEvent,
                    onTaskChartEvent = ::handleTaskChartEvent,
                    onExportSchedule = { scheduleExportLauncher.launch("intel_schedule.json") },
                    onImportSchedule = {
                        scheduleImportLauncher.launch(arrayOf("application/json", "text/plain"))
                    },
                    onExportTaskChart = { taskChartExportLauncher.launch("task_chart.md") }
                )
            }
        }
    }

    private fun handleScheduleEvent(event: ScheduleEvent) {
        scheduleViewModel.onEvent(event, applicationContext)
        if (event == ScheduleEvent.ToggleTheme) {
            taskChartViewModel.onEvent(TaskChartEvent.ToggleTheme, applicationContext)
        }
    }

    private fun handleTaskChartEvent(event: TaskChartEvent) {
        taskChartViewModel.onEvent(event, applicationContext)
        if (event == TaskChartEvent.ToggleTheme) {
            scheduleViewModel.onEvent(ScheduleEvent.ToggleTheme, applicationContext)
        }
    }
}
