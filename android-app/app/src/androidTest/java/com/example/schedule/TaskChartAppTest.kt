package com.example.schedule

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.schedule.ui.TaskChartApp
import com.example.schedule.ui.theme.ScheduleTheme
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class TaskChartAppTest {

    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun defaultTaskChartScreen_showsConvertedPythonActions() {
        val baseState = TaskChartUiState()

        composeRule.setContent {
            ScheduleTheme(darkTheme = baseState.isDarkTheme) {
                TaskChartApp(
                    state = baseState,
                    onEvent = { },
                    onExportMarkdown = { }
                )
            }
        }

        composeRule.onNodeWithText("Task Chart").assertIsDisplayed()
        composeRule.onNodeWithText("Add Task").assertIsDisplayed()
        composeRule.onNodeWithText("Save Local").assertIsDisplayed()
        composeRule.onNodeWithText("Load Local").assertIsDisplayed()
        composeRule.onNodeWithText("Export Markdown").assertIsDisplayed()
        composeRule.onNodeWithText("Reset Status").assertIsDisplayed()
        composeRule.onNodeWithText("Short-Term (11)").assertIsDisplayed()
        composeRule.onNodeWithText("Buy groceries").assertIsDisplayed()
    }

    @Test
    fun tappingCategoryTab_emitsSelectCategoryEvent() {
        val baseState = TaskChartUiState()
        val receivedEvents = mutableListOf<TaskChartEvent>()

        composeRule.setContent {
            ScheduleTheme(darkTheme = baseState.isDarkTheme) {
                TaskChartApp(
                    state = baseState,
                    onEvent = { receivedEvents += it },
                    onExportMarkdown = { }
                )
            }
        }

        composeRule.onNodeWithText("Long-Term (7)").performClick()

        assertTrue(receivedEvents.last() is TaskChartEvent.SelectCategory)
        assertEquals(1, (receivedEvents.last() as TaskChartEvent.SelectCategory).index)
    }

    @Test
    fun tappingThemeToggle_emitsToggleThemeEvent() {
        val baseState = TaskChartUiState()
        val receivedEvents = mutableListOf<TaskChartEvent>()

        composeRule.setContent {
            ScheduleTheme(darkTheme = baseState.isDarkTheme) {
                TaskChartApp(
                    state = baseState,
                    onEvent = { receivedEvents += it },
                    onExportMarkdown = { }
                )
            }
        }

        composeRule.onNodeWithContentDescription("Toggle theme").performClick()

        assertEquals(TaskChartEvent.ToggleTheme, receivedEvents.single())
    }
}
