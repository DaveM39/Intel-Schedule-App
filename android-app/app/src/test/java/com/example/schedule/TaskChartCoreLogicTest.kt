package com.example.schedule

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class TaskChartCoreLogicTest {

    @Test
    fun defaultState_matchesPythonTaskCounts() {
        val state = TaskChartUiState()

        assertEquals(3, state.categories.size)
        assertEquals(23, state.totalTasks)
        assertEquals(0, state.completedTasks)
        assertEquals("Short-Term", state.selectedCategory.name)
        assertEquals(11, state.selectedCategory.tasks.size)
    }

    @Test
    fun defaultTasks_areSortedByPriorityThenName() {
        val shortTermTasks = TaskChartUiState().selectedCategory.tasks

        assertEquals("Buy groceries", shortTermTasks[0].name)
        assertEquals(TaskPriority.HIGH, shortTermTasks[0].priority)
        assertEquals("Pay bills", shortTermTasks[2].name)
        assertEquals(TaskPriority.HIGH, shortTermTasks[2].priority)
        assertEquals("Buy cleaning spray for glasses", shortTermTasks.last().name)
        assertEquals(TaskPriority.LOW, shortTermTasks.last().priority)
    }

    @Test
    fun buildTaskChartMarkdown_matchesPythonExportShape() {
        val categories = listOf(
            TaskCategoryGroup(
                name = "Short-Term",
                tasks = listOf(
                    TaskChartItem("task-1", "Buy groceries", TaskPriority.HIGH, done = true),
                    TaskChartItem("task-2", "Do laundry", TaskPriority.MEDIUM)
                )
            )
        )

        val markdown = buildTaskChartMarkdown(categories)

        assertTrue(markdown.startsWith("# Task Chart\n\n| Category | Task | Priority | Status |"))
        assertTrue(markdown.contains("| **Short-Term** | Buy groceries | High | ☑ Done |"))
        assertTrue(markdown.contains("| **Short-Term** | Do laundry | Medium | ☐ Not done |"))
        assertTrue(markdown.contains("## Summary"))
        assertTrue(markdown.contains("| **Short-Term** | 2 |"))
    }

    @Test
    fun encodeDecodeTaskChartPayload_roundTripsCategoriesAndSortsTasks() {
        val categories = listOf(
            TaskCategoryGroup(
                name = "Example",
                tasks = listOf(
                    TaskChartItem("task-2", "Medium task", TaskPriority.MEDIUM),
                    TaskChartItem("task-1", "High task", TaskPriority.HIGH, done = true)
                )
            )
        )

        val decoded = decodeTaskChartPayload(encodeTaskChartPayload(categories))

        assertEquals(1, decoded.size)
        assertEquals("Example", decoded.first().name)
        assertEquals("High task", decoded.first().tasks.first().name)
        assertEquals(true, decoded.first().tasks.first().done)
    }

    @Test
    fun buildTaskChartMarkdown_escapesUserTextForTableCells() {
        val categories = listOf(
            TaskCategoryGroup(
                name = "Work | Home",
                tasks = listOf(
                    TaskChartItem("task-1", "Plan | review\nFollow up", TaskPriority.HIGH)
                )
            )
        )

        val markdown = buildTaskChartMarkdown(categories)

        assertTrue(markdown.contains("**Work \\| Home**"))
        assertTrue(markdown.contains("Plan \\| review<br>Follow up"))
    }

    @Test
    fun decodeTaskChartPayload_ignoresUnknownFields() {
        val rawJson =
            """
            {
              "categories": [],
              "futureField": true
            }
            """.trimIndent()

        assertTrue(decodeTaskChartPayload(rawJson).isEmpty())
    }
}
