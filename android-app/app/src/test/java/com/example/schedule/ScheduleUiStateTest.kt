package com.example.schedule

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ScheduleUiStateTest {

    @Test
    fun defaultState_exposesFourDaysAndEmptyNotes() {
        val state = ScheduleUiState()

        assertEquals(4, state.days.size)
        assertEquals("1", state.selectedDay.id)
        assertEquals("", state.notes)
    }

    @Test
    fun cycleSummary_coversEightDayWindow() {
        val state = ScheduleUiState()

        assertEquals(8, state.cycleSummary.size)
        assertTrue(state.cycleSummary.first().contains("Off day 1"))
        assertTrue(state.cycleSummary[4].contains("On day 1"))
    }

    @Test
    fun filteredActivities_returnsEntriesMatchingActiveCategory() {
        val state = ScheduleUiState()
        val mealState = state.copy(activeFilter = ScheduleCategory.MEAL)

        val filtered = mealState.filteredActivities

        assertTrue(filtered.isNotEmpty())
        assertTrue(filtered.all { it.category == ScheduleCategory.MEAL })
    }
}
