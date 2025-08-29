"""Legend view displaying category chips for filtering schedule."""
from __future__ import annotations

from typing import Optional

from kivy.app import App
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.chip import MDChip

from app import models


class Legend(MDBoxLayout):
    """Row of chips allowing the user to filter activities by category."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(8)
        self._build_chips()

    def _build_chips(self) -> None:
        """Create one chip per category plus a *clear* chip."""
        for category, color in models.CATEGORY_COLORS.items():
            chip = MDChip(
                text=category.capitalize(),
                md_bg_color=self._hex_to_rgba(color),
                on_release=lambda chip, c=category: self._on_chip(c),
            )
            self.add_widget(chip)
        self.add_widget(
            MDChip(text="Clear Filter", on_release=lambda *_: self._on_chip(None))
        )

    def _on_chip(self, category: Optional[str]) -> None:
        """Notify the app about a new filter selection."""
        app = App.get_running_app()
        app.set_filter(category)

    @staticmethod
    def _hex_to_rgba(hex_color: str):
        """Convert a ``#RRGGBB`` colour string to an RGBA tuple."""
        return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)) + (1.0,)
