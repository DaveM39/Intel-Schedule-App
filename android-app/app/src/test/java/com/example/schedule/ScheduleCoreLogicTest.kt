package com.example.schedule

import com.example.schedule.ui.generateCalendar
import java.io.ByteArrayInputStream
import java.time.LocalDate
import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test

class ScheduleCoreLogicTest {

    @Test
    fun predictTodayScheduleIndex_matchesEightDayCycleRules() {
        val startDate = LocalDate.of(2026, 2, 1)

        assertEquals(0, predictTodayScheduleIndex(startDate, WorkMode.DAY_SHIFT, today = startDate))
        assertEquals(3, predictTodayScheduleIndex(startDate, WorkMode.DAY_SHIFT, today = startDate.plusDays(3)))
        assertEquals(0, predictTodayScheduleIndex(startDate, WorkMode.DAY_SHIFT, today = startDate.plusDays(4)))
        assertEquals(1, predictTodayScheduleIndex(startDate, WorkMode.DAY_SHIFT, today = startDate.plusDays(5)))
        assertEquals(0, predictTodayScheduleIndex(startDate, WorkMode.NIGHT_SHIFT, today = startDate.plusDays(6)))
        assertEquals(1, predictTodayScheduleIndex(startDate, WorkMode.NIGHT_SHIFT, today = startDate.plusDays(7)))
    }

    @Test
    fun encodeDecodeSchedulePayload_roundTripsPythonCompatibleSchema() {
        val startDate = LocalDate.of(2026, 2, 10)
        val state = ScheduleUiState(
            days = listOf(
                ScheduleDay(
                    id = "1",
                    title = "Example Day",
                    activities = listOf(
                        ActivityEntry("8:00 AM", "Gym", ScheduleCategory.GYM),
                        ActivityEntry("10:00 AM", "Meal", ScheduleCategory.MEAL)
                    )
                )
            ),
            notes = "Keep this note",
            startDate = startDate,
            workMode = WorkMode.NIGHT_SHIFT,
            userName = "Alex Rivera"
        )

        val rawJson = encodeSchedulePayload(state)
        val payload = decodeSchedulePayload(rawJson)

        assertEquals("02/10/2026", payload.startDate)
        assertEquals("nightshift", payload.workMode)
        assertEquals("Alex Rivera", payload.userName)
        assertEquals("Example Day", payload.schedule.getValue("1").title)
        assertEquals("gym", payload.schedule.getValue("1").activities.first()[2])

        val rebuiltDays = payload.toScheduleDays()
        assertEquals(1, rebuiltDays.size)
        assertEquals(2, rebuiltDays.first().activities.size)
        assertEquals(ScheduleCategory.GYM, rebuiltDays.first().activities.first().category)
    }

    @Test
    fun encodeDecodeSchedulePayload_preservesClearedNotes() {
        val payload = decodeSchedulePayload(
            encodeSchedulePayload(ScheduleUiState(notes = ""))
        )

        assertEquals("", payload.notes)
    }

    @Test
    fun decodeSchedulePayload_acceptsPythonShape_andSkipsInvalidRows() {
        val rawJson =
            """
            {
              "schedule": {
                "1": {
                  "title": "Imported Day",
                  "activities": [
                    ["7:00 AM", "Wake up", "morning"],
                    ["", "", "meal"],
                    ["9:00 AM", "Unknown category defaults", "not-a-real-category"]
                  ]
                }
              },
              "notes": "From Python export",
              "startDate": "02/12/2026",
              "userName": "Pat Lee"
            }
            """.trimIndent()

        val payload = decodeSchedulePayload(rawJson)
        val days = payload.toScheduleDays()

        assertEquals("From Python export", payload.notes)
        assertEquals("02/12/2026", payload.startDate)
        assertEquals("Pat Lee", payload.userName)

        assertEquals(1, days.size)
        assertEquals("Imported Day", days.first().title)
        assertEquals(2, days.first().activities.size)
        assertEquals(ScheduleCategory.MORNING, days.first().activities.last().category)
        assertEquals(WorkMode.DAY_SHIFT, WorkMode.fromStorage(payload.workMode))
    }

    @Test
    fun parseStartDate_supportsUsAndIsoFormats() {
        assertEquals(LocalDate.of(2026, 2, 12), parseStartDate("02/12/2026"))
        assertEquals(LocalDate.of(2026, 2, 12), parseStartDate("2026-02-12"))
        assertTrue(parseStartDate("bad-date") <= LocalDate.now())
    }

    @Test
    fun parseStartDate_blankValueFallsBackToToday() {
        assertEquals(LocalDate.now(), parseStartDate(""))
        assertEquals(LocalDate.now(), parseStartDate("   "))
        assertEquals(LocalDate.now(), parseStartDate(null))
    }

    @Test
    fun generateCalendar_expandsToSixWeeksWhenMonthNeedsIt() {
        val calendar = generateCalendar(year = 2025, month = 3)

        assertEquals(6, calendar.size)
        assertEquals(LocalDate.of(2025, 2, 23), calendar.first().first())
        assertEquals(LocalDate.of(2025, 4, 5), calendar.last().last())
    }

    @Test
    fun decodeSchedulePayload_ignoresUnknownFields() {
        val rawJson =
            """
            {
              "schedule": {},
              "notes": "Compatible",
              "futureField": { "enabled": true }
            }
            """.trimIndent()

        assertEquals("Compatible", decodeSchedulePayload(rawJson).notes)
    }

    @Test
    fun readUtf8WithLimit_rejectsOversizedImports() {
        val input = ByteArrayInputStream("12345".toByteArray())

        val error = assertThrows(IllegalArgumentException::class.java) {
            input.readUtf8WithLimit(maxBytes = 4)
        }

        assertTrue(error.message.orEmpty().contains("larger than 1 MB"))
    }
}
