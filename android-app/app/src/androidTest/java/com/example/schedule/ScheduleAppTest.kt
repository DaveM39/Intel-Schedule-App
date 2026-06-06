package com.example.schedule

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.schedule.ui.ScheduleApp
import com.example.schedule.ui.theme.ScheduleTheme
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class ScheduleAppTest {

    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun scheduleTitle_updatesWhenUserNameProvided() {
        val baseState = ScheduleUiState().copy(userName = "Casey")

        composeRule.setContent {
            ScheduleTheme(darkTheme = baseState.isDarkTheme) {
                ScheduleApp(
                    state = baseState,
                    onEvent = { },
                    onExportJson = { },
                    onImportJson = { }
                )
            }
        }

        composeRule.onNodeWithText("Casey • 4-On / 4-Off Planner").assertIsDisplayed()
    }

    @Test
    fun defaultPlannerScreen_showsCorePythonPortActions() {
        val baseState = ScheduleUiState()

        composeRule.setContent {
            ScheduleTheme(darkTheme = baseState.isDarkTheme) {
                ScheduleApp(
                    state = baseState,
                    onEvent = { },
                    onExportJson = { },
                    onImportJson = { }
                )
            }
        }

        composeRule.onNodeWithText("Set off-cycle date").assertIsDisplayed()
        composeRule.onNodeWithText("Save Local").assertIsDisplayed()
        composeRule.onNodeWithText("Load Local").assertIsDisplayed()
        composeRule.onNodeWithText("Export JSON").assertIsDisplayed()
        composeRule.onNodeWithText("Import JSON").assertIsDisplayed()
        composeRule.onNodeWithText("Yearly calendar").assertIsDisplayed()
        composeRule.onNodeWithText("Current cycle").assertIsDisplayed()
        composeRule.onNodeWithText("Personal notes").assertIsDisplayed()
        composeRule.onNodeWithText("Day 1").assertIsDisplayed()
        composeRule.onNodeWithText("Recovery after Night Shift").assertIsDisplayed()
    }

    @Test
    fun tappingDayTab_emitsSelectDayEvent() {
        val baseState = ScheduleUiState()
        val receivedEvents = mutableListOf<ScheduleEvent>()

        composeRule.setContent {
            ScheduleTheme(darkTheme = baseState.isDarkTheme) {
                ScheduleApp(
                    state = baseState,
                    onEvent = { receivedEvents += it },
                    onExportJson = { },
                    onImportJson = { }
                )
            }
        }

        composeRule.onNodeWithText("Day 3").performClick()

        assertTrue(receivedEvents.last() is ScheduleEvent.SelectDay)
        assertEquals(2, (receivedEvents.last() as ScheduleEvent.SelectDay).index)
    }

    @Test
    fun tappingFilterChip_emitsCategoryFilterEvent() {
        val baseState = ScheduleUiState()
        val receivedEvents = mutableListOf<ScheduleEvent>()

        composeRule.setContent {
            ScheduleTheme(darkTheme = baseState.isDarkTheme) {
                ScheduleApp(
                    state = baseState,
                    onEvent = { receivedEvents += it },
                    onExportJson = { },
                    onImportJson = { }
                )
            }
        }

        composeRule.onNodeWithText("Meal").performClick()

        assertTrue(receivedEvents.last() is ScheduleEvent.FilterByCategory)
        assertEquals(
            ScheduleCategory.MEAL,
            (receivedEvents.last() as ScheduleEvent.FilterByCategory).category
        )
    }

    @Test
    fun tappingCalendarButton_opensDialogAndRequestsTodayYear() {
        val baseState = ScheduleUiState()
        val receivedEvents = mutableListOf<ScheduleEvent>()

        composeRule.setContent {
            ScheduleTheme(darkTheme = baseState.isDarkTheme) {
                ScheduleApp(
                    state = baseState,
                    onEvent = { receivedEvents += it },
                    onExportJson = { },
                    onImportJson = { }
                )
            }
        }

        composeRule.onNodeWithText("Yearly calendar").performClick()

        assertTrue(receivedEvents.first() is ScheduleEvent.GoToTodayOnCalendar)
        composeRule.onNodeWithText("${baseState.calendarYear} Calendar").assertIsDisplayed()
    }

    @Test
    fun tappingThemeToggle_emitsToggleThemeEvent() {
        val baseState = ScheduleUiState()
        val receivedEvents = mutableListOf<ScheduleEvent>()

        composeRule.setContent {
            ScheduleTheme(darkTheme = baseState.isDarkTheme) {
                ScheduleApp(
                    state = baseState,
                    onEvent = { receivedEvents += it },
                    onExportJson = { },
                    onImportJson = { }
                )
            }
        }

        composeRule.onNodeWithContentDescription("Toggle theme").performClick()

        assertEquals(ScheduleEvent.ToggleTheme, receivedEvents.single())
    }
}
