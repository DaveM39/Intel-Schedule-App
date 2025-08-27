"""Reusable dialog builders."""
from typing import Callable

from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

from ..models import CATEGORY_COLORS


class ActivityDialogContent(BoxLayout):
    """Content of the activity edit dialog."""
    time = StringProperty()
    description = StringProperty()
    category = StringProperty()


class ActivityEditDialog:
    """Helper that shows a dialog to edit an activity."""

    def __init__(self, time: str, description: str, category: str, callback: Callable):
        self.callback = callback
        self.content = ActivityDialogContent(time=time, description=description, category=category)
        self.dialog = MDDialog(
            title="Edit Activity",
            type="custom",
            content_cls=self.content,
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda *x: self.dialog.dismiss()),
                MDFlatButton(text="Save", on_release=self._save),
            ],
        )

    def open(self):
        self.dialog.open()

    def _save(self, *_):
        self.dialog.dismiss()
        self.callback(
            self.content.ids.time_field.text,
            self.content.ids.desc_field.text,
            self.content.ids.cat_field.text,
        )
