package com.example.schedule

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.schedule.ui.ScheduleSuiteApp
import com.example.schedule.ui.theme.ScheduleTheme
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class ScheduleSuiteAppTest {

    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun bottomNavigation_exposesPlannerAndTaskChart() {
        composeRule.setContent {
            ScheduleTheme(darkTheme = false) {
                ScheduleSuiteApp(
                    scheduleState = ScheduleUiState(),
                    taskChartState = TaskChartUiState(),
                    onScheduleEvent = { },
                    onTaskChartEvent = { },
                    onExportSchedule = { },
                    onImportSchedule = { },
                    onExportTaskChart = { }
                )
            }
        }

        composeRule.onNodeWithText("Current cycle").assertIsDisplayed()
        composeRule.onNodeWithText("Tasks").performClick()
        composeRule.onNodeWithText("Task Chart").assertIsDisplayed()
        composeRule.onNodeWithText("Planner").performClick()
        composeRule.onNodeWithText("Current cycle").assertIsDisplayed()
    }
}
