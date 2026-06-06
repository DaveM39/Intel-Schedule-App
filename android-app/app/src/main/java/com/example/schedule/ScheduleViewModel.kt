package com.example.schedule

import android.content.Context
import android.net.Uri
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.Locale
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

private const val DATASTORE_NAME = "schedule_store"
private const val DATASTORE_SCHEDULE_JSON_KEY = "schedule_json"
private val storageFormatter: DateTimeFormatter = DateTimeFormatter.ofPattern("MM/dd/yyyy")
private val isoFormatter: DateTimeFormatter = DateTimeFormatter.ISO_LOCAL_DATE
private val scheduleJson = Json {
    prettyPrint = true
    ignoreUnknownKeys = true
}
private val Context.scheduleDataStore by preferencesDataStore(name = DATASTORE_NAME)
private val scheduleJsonPreferenceKey = stringPreferencesKey(DATASTORE_SCHEDULE_JSON_KEY)

/**
 * Core application state exposed to the UI layer.
 */
data class ScheduleUiState(
    val days: List<ScheduleDay> = defaultSchedule(),
    val selectedDayIndex: Int = 0,
    val activeFilter: ScheduleCategory? = null,
    val notes: String = DEFAULT_NOTES,
    val startDate: LocalDate = LocalDate.now(),
    val workMode: WorkMode = WorkMode.DAY_SHIFT,
    val userName: String = "",
    val isDarkTheme: Boolean = false,
    val message: String? = null,
    val calendarYear: Int = LocalDate.now().year,
    val hasUnsavedChanges: Boolean = false
) {
    val title: String
        get() = if (userName.isBlank()) {
            "Intel Technician • 4-On / 4-Off Planner"
        } else {
            "$userName • 4-On / 4-Off Planner"
        }

    val startDateLabel: String
        get() = storageFormatter.format(startDate)

    val cycleSummary: List<String>
        get() {
            val formatter = DateTimeFormatter.ofPattern("EEEE, MMM dd, yyyy", Locale.getDefault())
            return (0 until 8).map { offset ->
                val date = startDate.plusDays(offset.toLong())
                val phase = if (offset < 4) "Off" else "On"
                val dayNumber = offset % 4 + 1
                "${formatter.format(date)} – $phase day $dayNumber"
            }
        }

    val predictedTodayDayIndex: Int
        get() = predictTodayScheduleIndex(startDate = startDate, workMode = workMode)

    val predictedTodayDayLabel: String
        get() = "Predicted today tab: Day ${predictedTodayDayIndex + 1} (${workMode.displayName})"

    val selectedDay: ScheduleDay
        get() = days.getOrElse(selectedDayIndex) { days.first() }

    val filteredActivities: List<ActivityEntry>
        get() = activeFilter?.let { filter ->
            selectedDay.activities.filter { it.category == filter }
        } ?: selectedDay.activities
}

class ScheduleViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(ScheduleUiState())
    val uiState = _uiState.asStateFlow()

    fun onEvent(event: ScheduleEvent, context: Context) {
        when (event) {
            ScheduleEvent.ToggleTheme -> toggleTheme()
            is ScheduleEvent.SelectDay -> selectDay(event.index)
            is ScheduleEvent.FilterByCategory -> filterByCategory(event.category)
            ScheduleEvent.ClearFilter -> clearFilter()
            is ScheduleEvent.UpdateNotes -> updateNotes(event.value)
            is ScheduleEvent.UpdateStartDate -> updateStartDate(event.date)
            ScheduleEvent.SaveSchedule -> saveLocally(context)
            ScheduleEvent.LoadSchedule -> loadLocally(context)
            is ScheduleEvent.UpdateUserName -> updateUserName(event.name)
            is ScheduleEvent.UpdateWorkMode -> updateWorkMode(event.mode)
            is ScheduleEvent.CommitActivityEdit -> commitActivityEdit(
                dayId = event.dayId,
                activityIndex = event.activityIndex,
                replacement = event.entry
            )
            is ScheduleEvent.AddActivity -> addActivity(
                dayId = event.dayId,
                entry = event.entry
            )
            is ScheduleEvent.DeleteActivity -> deleteActivity(
                dayId = event.dayId,
                activityIndex = event.activityIndex
            )
            is ScheduleEvent.ResetDay -> resetDay(event.dayId)
            is ScheduleEvent.ChangeCalendarYear -> shiftCalendarYear(event.delta)
            ScheduleEvent.GoToTodayOnCalendar -> goToToday()
            ScheduleEvent.SelectPredictedDay -> selectPredictedDay()
            ScheduleEvent.AcknowledgeMessage -> clearMessage()
        }
    }

    private fun toggleTheme() {
        _uiState.update {
            it.copy(
                isDarkTheme = !it.isDarkTheme,
                activeFilter = null
            )
        }
    }

    private fun selectDay(index: Int) {
        _uiState.update { it.copy(selectedDayIndex = index.coerceIn(it.days.indices)) }
    }

    private fun filterByCategory(category: ScheduleCategory?) {
        _uiState.update { state ->
            val nextFilter = if (state.activeFilter == category) null else category
            state.copy(activeFilter = nextFilter)
        }
    }

    private fun clearFilter() {
        _uiState.update { it.copy(activeFilter = null) }
    }

    private fun updateNotes(notes: String) {
        _uiState.update { it.copy(notes = notes, hasUnsavedChanges = true) }
    }

    private fun updateUserName(name: String) {
        _uiState.update { it.copy(userName = name.trim(), hasUnsavedChanges = true) }
    }

    private fun updateStartDate(date: LocalDate) {
        _uiState.update { current ->
            current.copy(
                startDate = date,
                hasUnsavedChanges = true
            )
        }
    }

    private fun updateWorkMode(mode: WorkMode) {
        _uiState.update { current -> current.copy(workMode = mode, hasUnsavedChanges = true) }
    }

    private fun shiftCalendarYear(delta: Int) {
        _uiState.update {
            it.copy(calendarYear = (it.calendarYear + delta).coerceIn(1900, 2200))
        }
    }

    private fun goToToday() {
        val today = LocalDate.now()
        _uiState.update { it.copy(calendarYear = today.year) }
    }

    private fun commitActivityEdit(dayId: String, activityIndex: Int, replacement: ActivityEntry) {
        _uiState.update { state ->
            val targetIndex = state.days.indexOfFirst { it.id == dayId }
            if (targetIndex == -1) return@update state
            val updatedDay = state.days[targetIndex].let { day ->
                val newActivities = day.activities.toMutableList().apply {
                    if (activityIndex in indices) {
                        this[activityIndex] = replacement
                    }
                }
                day.copy(activities = newActivities)
            }
            val updatedDays = state.days.toMutableList().apply {
                if (targetIndex in indices) this[targetIndex] = updatedDay
            }
            state.copy(days = updatedDays, hasUnsavedChanges = true)
        }
    }

    private fun addActivity(dayId: String, entry: ActivityEntry) {
        _uiState.update { state ->
            val targetIndex = state.days.indexOfFirst { it.id == dayId }
            if (targetIndex == -1) return@update state
            val updatedDay = state.days[targetIndex].let { day ->
                day.copy(activities = day.activities + entry)
            }
            val updatedDays = state.days.toMutableList().apply {
                if (targetIndex in indices) this[targetIndex] = updatedDay
            }
            state.copy(days = updatedDays, hasUnsavedChanges = true)
        }
    }

    private fun deleteActivity(dayId: String, activityIndex: Int) {
        _uiState.update { state ->
            val targetIndex = state.days.indexOfFirst { it.id == dayId }
            if (targetIndex == -1) return@update state
            val updatedDay = state.days[targetIndex].let { day ->
                val activities = day.activities
                if (activityIndex !in activities.indices) return@update state
                val updatedActivities = activities.toMutableList().apply {
                    removeAt(activityIndex)
                }
                day.copy(activities = updatedActivities)
            }
            val updatedDays = state.days.toMutableList().apply {
                if (targetIndex in indices) this[targetIndex] = updatedDay
            }
            state.copy(days = updatedDays, hasUnsavedChanges = true)
        }
    }

    private fun resetDay(dayId: String) {
        val defaultDay = defaultSchedule().firstOrNull { it.id == dayId } ?: return
        _uiState.update { state ->
            val targetIndex = state.days.indexOfFirst { it.id == dayId }
            if (targetIndex == -1) return@update state
            val updatedDays = state.days.toMutableList().apply {
                this[targetIndex] = defaultDay
            }
            state.copy(days = updatedDays, hasUnsavedChanges = true)
        }
    }

    fun exportScheduleToUri(context: Context, destinationUri: Uri) {
        viewModelScope.launch(Dispatchers.IO) {
            runCatching {
                val raw = encodeSchedulePayload(_uiState.value)
                context.contentResolver.openOutputStream(destinationUri)?.use { stream ->
                    stream.write(raw.toByteArray())
                } ?: error("Unable to open destination file.")
            }.onSuccess {
                _uiState.update { it.copy(message = "Schedule exported to JSON") }
            }.onFailure { error ->
                _uiState.update {
                    it.copy(message = "Export failed: ${error.localizedMessage ?: "Unknown error"}")
                }
            }
        }
    }

    fun importScheduleFromUri(context: Context, sourceUri: Uri) {
        viewModelScope.launch(Dispatchers.IO) {
            val content = runCatching {
                context.contentResolver.openInputStream(sourceUri)?.use { stream ->
                    stream.readUtf8WithLimit()
                } ?: error("Unable to open selected file.")
            }.getOrElse { error ->
                _uiState.update {
                    it.copy(message = "Import failed: ${error.localizedMessage ?: "Unknown error"}")
                }
                return@launch
            }

            val payload = runCatching { decodeSchedulePayload(content) }.getOrElse { error ->
                _uiState.update {
                    it.copy(message = "Import failed: ${error.localizedMessage ?: "Invalid JSON format"}")
                }
                return@launch
            }

            applyLoadedPayload(payload, successMessage = "Schedule imported")
            runCatching { persistPayload(context, payload) }.onFailure { error ->
                _uiState.update {
                    it.copy(message = "Imported but local save failed: ${error.localizedMessage ?: "Unknown error"}")
                }
            }
        }
    }

    private fun saveLocally(context: Context) {
        viewModelScope.launch(Dispatchers.IO) {
            val payload = _uiState.value.toFilePayload()
            val saveResult = runCatching { persistPayload(context, payload) }
            saveResult.onSuccess {
                _uiState.update { it.copy(message = "Schedule saved locally", hasUnsavedChanges = false) }
            }.onFailure { error ->
                _uiState.update {
                    it.copy(message = "Save failed: ${error.localizedMessage ?: "Unknown error"}")
                }
            }
        }
    }

    private fun loadLocally(context: Context) {
        viewModelScope.launch(Dispatchers.IO) {
            val storedJson = runCatching {
                context.scheduleDataStore.data.first()[scheduleJsonPreferenceKey]
            }.getOrElse { error ->
                _uiState.update {
                    it.copy(message = "Load failed: ${error.localizedMessage ?: "Unknown error"}")
                }
                return@launch
            }

            if (storedJson.isNullOrBlank()) {
                _uiState.update { it.copy(message = "No local schedule found") }
                return@launch
            }

            val payload = runCatching { decodeSchedulePayload(storedJson) }.getOrElse { error ->
                _uiState.update {
                    it.copy(message = "Load failed: ${error.localizedMessage ?: "Invalid JSON format"}")
                }
                return@launch
            }

            applyLoadedPayload(payload, successMessage = "Schedule loaded")
        }
    }

    private suspend fun persistPayload(context: Context, payload: ScheduleFilePayload) {
        context.scheduleDataStore.edit { preferences ->
            preferences[scheduleJsonPreferenceKey] = scheduleJson.encodeToString(payload)
        }
    }

    private fun applyLoadedPayload(payload: ScheduleFilePayload, successMessage: String) {
        val parsedDays = payload.toScheduleDays()
        val parsedDate = parseStartDate(payload.startDate)
        val parsedWorkMode = WorkMode.fromStorage(payload.workMode)

        _uiState.update { current ->
            val activeDays = parsedDays.ifEmpty { defaultSchedule() }
            current.copy(
                days = activeDays,
                notes = payload.notes.ifBlank { DEFAULT_NOTES },
                startDate = parsedDate,
                workMode = parsedWorkMode,
                userName = payload.userName.orEmpty(),
                calendarYear = LocalDate.now().year,
                selectedDayIndex = 0,
                hasUnsavedChanges = false,
                message = successMessage
            )
        }
    }

    private fun selectPredictedDay() {
        _uiState.update { current ->
            val predictedIndex = predictTodayScheduleIndex(current.startDate, current.workMode)
            current.copy(selectedDayIndex = predictedIndex.coerceIn(current.days.indices))
        }
    }

    private fun clearMessage() {
        _uiState.update { it.copy(message = null) }
    }
}

sealed interface ScheduleEvent {
    data object ToggleTheme : ScheduleEvent
    data class SelectDay(val index: Int) : ScheduleEvent
    data class FilterByCategory(val category: ScheduleCategory?) : ScheduleEvent
    data object ClearFilter : ScheduleEvent
    data class UpdateNotes(val value: String) : ScheduleEvent
    data class UpdateStartDate(val date: LocalDate) : ScheduleEvent
    data class UpdateWorkMode(val mode: WorkMode) : ScheduleEvent
    data object SaveSchedule : ScheduleEvent
    data object LoadSchedule : ScheduleEvent
    data class UpdateUserName(val name: String) : ScheduleEvent
    data class CommitActivityEdit(
        val dayId: String,
        val activityIndex: Int,
        val entry: ActivityEntry
    ) : ScheduleEvent
    data class AddActivity(
        val dayId: String,
        val entry: ActivityEntry
    ) : ScheduleEvent
    data class DeleteActivity(
        val dayId: String,
        val activityIndex: Int
    ) : ScheduleEvent
    data class ResetDay(val dayId: String) : ScheduleEvent
    data class ChangeCalendarYear(val delta: Int) : ScheduleEvent
    data object GoToTodayOnCalendar : ScheduleEvent
    data object SelectPredictedDay : ScheduleEvent
    data object AcknowledgeMessage : ScheduleEvent
}

@Serializable
data class ScheduleDay(
    val id: String,
    val title: String,
    val activities: List<ActivityEntry>
)

@Serializable
data class ActivityEntry(
    val time: String,
    val description: String,
    val category: ScheduleCategory
)

@Serializable
enum class WorkMode {
    @SerialName("dayshift") DAY_SHIFT,
    @SerialName("nightshift") NIGHT_SHIFT;

    val displayName: String
        get() = when (this) {
            DAY_SHIFT -> "Day Shift"
            NIGHT_SHIFT -> "Night Shift"
        }

    val storageName: String
        get() = when (this) {
            DAY_SHIFT -> "dayshift"
            NIGHT_SHIFT -> "nightshift"
        }

    companion object {
        fun fromStorage(raw: String?): WorkMode {
            return values().firstOrNull { it.storageName.equals(raw, ignoreCase = true) } ?: DAY_SHIFT
        }
    }
}

@Serializable
enum class ScheduleCategory {
    @SerialName("sleep") SLEEP,
    @SerialName("morning") MORNING,
    @SerialName("afternoon") AFTERNOON,
    @SerialName("evening") EVENING,
    @SerialName("medicine") MEDICINE,
    @SerialName("gym") GYM,
    @SerialName("coding") CODING,
    @SerialName("meal") MEAL;

    val displayName: String
        get() = storageName.replaceFirstChar { it.uppercase(Locale.getDefault()) }

    val storageName: String
        get() = name.lowercase(Locale.ROOT)

    companion object {
        fun fromStorage(raw: String?): ScheduleCategory {
            if (raw.isNullOrBlank()) return MORNING
            return values().firstOrNull { it.storageName.equals(raw, ignoreCase = true) } ?: MORNING
        }
    }
}

private const val DEFAULT_NOTES = "This is a scratchpad for any notes you want to keep."
private const val MAX_SCHEDULE_IMPORT_BYTES = 1_048_576

internal fun InputStream.readUtf8WithLimit(maxBytes: Int = MAX_SCHEDULE_IMPORT_BYTES): String {
    require(maxBytes > 0) { "Import size limit must be positive." }
    val output = ByteArrayOutputStream()
    val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
    var totalBytes = 0

    while (true) {
        val count = read(buffer)
        if (count == -1) break
        totalBytes += count
        require(totalBytes <= maxBytes) { "Schedule file is larger than 1 MB." }
        output.write(buffer, 0, count)
    }
    return output.toString(Charsets.UTF_8.name())
}

internal fun encodeSchedulePayload(state: ScheduleUiState): String {
    return scheduleJson.encodeToString(state.toFilePayload())
}

internal fun decodeSchedulePayload(raw: String): ScheduleFilePayload {
    return runCatching {
        scheduleJson.decodeFromString<ScheduleFilePayload>(raw)
    }.recoverCatching {
        val legacy = scheduleJson.decodeFromString<LegacySchedulePayload>(raw)
        legacy.toFilePayload()
    }.getOrThrow()
}

internal fun ScheduleUiState.toFilePayload(): ScheduleFilePayload {
    val scheduleMap = linkedMapOf<String, ScheduleDayFile>()
    days.forEach { day ->
        scheduleMap[day.id] = ScheduleDayFile(
            title = day.title,
            activities = day.activities.map { entry ->
                listOf(entry.time, entry.description, entry.category.storageName)
            }
        )
    }
    return ScheduleFilePayload(
        schedule = scheduleMap,
        notes = notes,
        startDate = storageFormatter.format(startDate),
        workMode = workMode.storageName,
        userName = userName
    )
}

internal fun ScheduleFilePayload.toScheduleDays(): List<ScheduleDay> {
    if (schedule.isEmpty()) return emptyList()
    return schedule.entries
        .sortedBy { entry -> entry.key.toIntOrNull() ?: Int.MAX_VALUE }
        .map { (id, payload) ->
            val activities = payload.activities.mapNotNull { triple ->
                val time = triple.getOrNull(0)?.takeIf { it.isNotBlank() } ?: return@mapNotNull null
                val description = triple.getOrNull(1)?.takeIf { it.isNotBlank() } ?: return@mapNotNull null
                val categoryName = triple.getOrNull(2)
                ActivityEntry(
                    time = time,
                    description = description,
                    category = ScheduleCategory.fromStorage(categoryName)
                )
            }
            ScheduleDay(
                id = id,
                title = payload.title,
                activities = activities
            )
        }
}

private fun LegacySchedulePayload.toFilePayload(): ScheduleFilePayload {
    val scheduleMap = linkedMapOf<String, ScheduleDayFile>()
    if (days.isNotEmpty()) {
        days.forEach { day ->
            scheduleMap[day.id] = ScheduleDayFile(
                title = day.title,
                activities = day.activities.map { entry ->
                    listOf(entry.time, entry.description, entry.category.storageName)
                }
            )
        }
    }
    return ScheduleFilePayload(
        schedule = scheduleMap,
        notes = notes,
        startDate = startDate,
        workMode = workMode,
        userName = userName
    )
}

internal fun parseStartDate(raw: String?): LocalDate {
    val value = raw?.trim().orEmpty()
    if (value.isEmpty()) return LocalDate.now()
    return runCatching { LocalDate.parse(value, storageFormatter) }
        .recoverCatching { LocalDate.parse(value, isoFormatter) }
        .getOrElse { LocalDate.now() }
}

internal fun predictTodayScheduleIndex(
    startDate: LocalDate,
    workMode: WorkMode,
    today: LocalDate = LocalDate.now()
): Int {
    val deltaDays = ChronoUnit.DAYS.between(startDate, today).toInt()
    val cyclePosition = Math.floorMod(deltaDays, 8)
    if (cyclePosition in 0..3) return cyclePosition
    if (workMode == WorkMode.DAY_SHIFT && cyclePosition in 4..5) return cyclePosition - 4
    if (workMode == WorkMode.NIGHT_SHIFT && cyclePosition in 6..7) return cyclePosition - 6
    return 0
}

@Serializable
internal data class ScheduleFilePayload(
    val schedule: Map<String, ScheduleDayFile> = emptyMap(),
    val notes: String = DEFAULT_NOTES,
    val startDate: String = "",
    val workMode: String = "dayshift",
    val userName: String? = ""
)

@Serializable
internal data class ScheduleDayFile(
    val title: String,
    val activities: List<List<String>> = emptyList()
)

@Serializable
private data class LegacySchedulePayload(
    val days: List<ScheduleDay> = emptyList(),
    val notes: String = DEFAULT_NOTES,
    val startDate: String = "",
    val workMode: String = "dayshift",
    val userName: String? = ""
)

private fun defaultSchedule(): List<ScheduleDay> = listOf(
    ScheduleDay(
        id = "1",
        title = "Recovery after Night Shift",
        activities = listOf(
            ActivityEntry("10:00 AM", "Sleep (post‑shift, until ≈3:30 PM)", ScheduleCategory.SLEEP),
            ActivityEntry("3:30 PM", "Wake up", ScheduleCategory.MORNING),
            ActivityEntry("4:00 PM", "Protein‑rich meal", ScheduleCategory.MEAL),
            ActivityEntry("4:30 PM", "Take medicine (after meal)", ScheduleCategory.MEDICINE),
            ActivityEntry("5:00 PM", "Light stretching / mobility", ScheduleCategory.MORNING),
            ActivityEntry("5:30 PM", "Grocery shopping", ScheduleCategory.AFTERNOON),
            ActivityEntry("7:00 PM", "Pre‑workout snack", ScheduleCategory.MEAL),
            ActivityEntry("8:00 PM", "Gym – Chest & Triceps", ScheduleCategory.GYM),
            ActivityEntry("10:00 PM", "Post‑workout meal", ScheduleCategory.MEAL),
            ActivityEntry("10:30 PM", "Take medicine (after meal)", ScheduleCategory.MEDICINE),
            ActivityEntry("11:00 PM", "Relaxation", ScheduleCategory.EVENING),
            ActivityEntry("12:30 AM", "Bedtime", ScheduleCategory.EVENING)
        )
    ),
    ScheduleDay(
        id = "2",
        title = "Productive Focus",
        activities = listOf(
            ActivityEntry("9:30 AM", "Wake up", ScheduleCategory.MORNING),
            ActivityEntry("10:00 AM", "Protein breakfast", ScheduleCategory.MEAL),
            ActivityEntry("10:30 AM", "Take medicine (after breakfast)", ScheduleCategory.MEDICINE),
            ActivityEntry("10:45 AM", "Home maintenance / cleaning", ScheduleCategory.MORNING),
            ActivityEntry("12:30 PM", "Lunch", ScheduleCategory.MEAL),
            ActivityEntry("1:00 PM", "Take medicine (after lunch)", ScheduleCategory.MEDICINE),
            ActivityEntry("1:30 PM", "Deep coding session (2–3 h)", ScheduleCategory.CODING),
            ActivityEntry("4:30 PM", "Learning – online course", ScheduleCategory.AFTERNOON),
            ActivityEntry("5:30 PM", "Rest / pre‑workout prep", ScheduleCategory.AFTERNOON),
            ActivityEntry("6:00 PM", "Pre‑workout meal", ScheduleCategory.MEAL),
            ActivityEntry("7:00 PM", "Gym – Back & Biceps", ScheduleCategory.GYM),
            ActivityEntry("9:00 PM", "Post‑workout dinner", ScheduleCategory.MEAL),
            ActivityEntry("9:30 PM", "Take medicine (after dinner)", ScheduleCategory.MEDICINE),
            ActivityEntry("10:00 PM", "Relaxation", ScheduleCategory.EVENING),
            ActivityEntry("12:00 AM", "Bedtime", ScheduleCategory.EVENING)
        )
    ),
    ScheduleDay(
        id = "3",
        title = "Balance Day",
        activities = listOf(
            ActivityEntry("9:30 AM", "Wake up", ScheduleCategory.MORNING),
            ActivityEntry("10:00 AM", "Protein breakfast", ScheduleCategory.MEAL),
            ActivityEntry("10:30 AM", "Take medicine (after breakfast)", ScheduleCategory.MEDICINE),
            ActivityEntry("10:45 AM", "Meal prep for remaining days", ScheduleCategory.MORNING),
            ActivityEntry("12:30 PM", "Lunch", ScheduleCategory.MEAL),
            ActivityEntry("1:00 PM", "Take medicine (after lunch)", ScheduleCategory.MEDICINE),
            ActivityEntry("1:30 PM", "Coding session (2–3 h)", ScheduleCategory.CODING),
            ActivityEntry("4:30 PM", "Outdoor hobby / walk", ScheduleCategory.AFTERNOON),
            ActivityEntry("5:30 PM", "Rest / pre‑workout prep", ScheduleCategory.AFTERNOON),
            ActivityEntry("6:00 PM", "Pre‑workout snack", ScheduleCategory.MEAL),
            ActivityEntry("7:00 PM", "Gym – Shoulders & Abs", ScheduleCategory.GYM),
            ActivityEntry("9:00 PM", "Post‑workout dinner", ScheduleCategory.MEAL),
            ActivityEntry("9:30 PM", "Take medicine (after dinner)", ScheduleCategory.MEDICINE),
            ActivityEntry("10:00 PM", "Reading / downtime", ScheduleCategory.EVENING),
            ActivityEntry("12:00 AM", "Bedtime", ScheduleCategory.EVENING)
        )
    ),
    ScheduleDay(
        id = "4",
        title = "Social / Rest",
        activities = listOf(
            ActivityEntry("9:30 AM", "Wake up", ScheduleCategory.MORNING),
            ActivityEntry("10:00 AM", "Easy breakfast", ScheduleCategory.MEAL),
            ActivityEntry("10:30 AM", "Take medicine (after breakfast)", ScheduleCategory.MEDICINE),
            ActivityEntry("11:00 AM", "Laundry & chores", ScheduleCategory.MORNING),
            ActivityEntry("12:30 PM", "Lunch – meet a friend", ScheduleCategory.MEAL),
            ActivityEntry("1:30 PM", "Free time / errands", ScheduleCategory.AFTERNOON),
            ActivityEntry("4:30 PM", "Prep for upcoming work block", ScheduleCategory.AFTERNOON),
            ActivityEntry("6:00 PM", "Light gym – Stretch & Cardio", ScheduleCategory.GYM),
            ActivityEntry("7:30 PM", "Cheat‑meal dinner out", ScheduleCategory.MEAL),
            ActivityEntry("9:00 PM", "Relax with family / friends", ScheduleCategory.EVENING),
            ActivityEntry("11:00 PM", "Early bedtime", ScheduleCategory.EVENING)
        )
    )
)
