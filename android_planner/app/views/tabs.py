"""UI widgets for day schedule tabs."""
from kivy.properties import StringProperty, ListProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.recycleview import RecycleView


class DayTab(MDBoxLayout):
    """Container for a single day's schedule inside the MDTabs widget."""
    day_key = StringProperty()
    title = StringProperty()
    activities = ListProperty()


class ScheduleRecycleView(RecycleView):
    """RecycleView subclass used within each tab to display activities."""
    pass
