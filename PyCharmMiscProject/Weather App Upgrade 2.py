import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog
import requests
import json
from datetime import datetime, timedelta
import os
import pickle
import webbrowser
from PIL import Image, ImageTk
import io
import threading
import time
import platform


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Weather Forecast")
        self.root.geometry("600x750")
        self.root.resizable(False, False)

        # Set color schemes
        self.color_schemes = {
            "light": {
                "bg_color": "#E8F1F5",
                "accent_color": "#005B96",
                "text_color": "#333333",
                "card_bg": "#FFFFFF"
            },
            "dark": {
                "bg_color": "#1E1E1E",
                "accent_color": "#0078D7",
                "text_color": "#FFFFFF",
                "card_bg": "#2D2D2D"
            },
            "nature": {
                "bg_color": "#E8F5E9",
                "accent_color": "#388E3C",
                "text_color": "#212121",
                "card_bg": "#FFFFFF"
            },
            "sunset": {
                "bg_color": "#FBE9E7",
                "accent_color": "#D84315",
                "text_color": "#212121",
                "card_bg": "#FFFFFF"
            }
        }

        # Default to light theme
        self.current_theme = "light"
        scheme = self.color_schemes[self.current_theme]

        self.bg_color = scheme["bg_color"]
        self.accent_color = scheme["accent_color"]
        self.text_color = scheme["text_color"]
        self.card_bg = scheme["card_bg"]

        self.root.configure(bg=self.bg_color)

        # API key for OpenWeatherMap
        self.api_key = "9d28222a8f9d1633f4b8b81e61f290ae"

        # Temperature unit (metric by default)
        self.temp_unit = "metric"  # can be "metric" or "imperial"

        # Favorite cities list
        self.fav_cities = []
        self.load_favorites()

        # Weather alerts and notification status
        self.notifications_enabled = False
        self.last_alert_check = None

        # History data storage
        self.history_data = []

        # Current city data
        self.current_city = None
        self.current_weather_data = None
        self.current_lat = None
        self.current_lon = None

        # Create weather icon representations using text symbols
        self.weather_icons = {
            "01": "☀️",  # clear sky
            "02": "🌤️",  # few clouds
            "03": "☁️",  # scattered clouds
            "04": "☁️",  # broken clouds
            "09": "🌧️",  # shower rain
            "10": "🌦️",  # rain
            "11": "⛈️",  # thunderstorm
            "13": "❄️",  # snow
            "50": "🌫️"  # mist
        }

        # Menu bar
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Weather Data", command=self.export_weather_data)
        file_menu.add_command(label="Export History Data", command=self.export_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Weather Map", command=self.open_weather_map)

        # Settings menu
        settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=settings_menu)

        # Theme submenu
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Light Theme", command=lambda: self.change_theme("light"))
        theme_menu.add_command(label="Dark Theme", command=lambda: self.change_theme("dark"))
        theme_menu.add_command(label="Nature Theme", command=lambda: self.change_theme("nature"))
        theme_menu.add_command(label="Sunset Theme", command=lambda: self.change_theme("sunset"))

        # Notifications menu option
        self.notification_var = tk.BooleanVar(value=False)
        settings_menu.add_checkbutton(label="Enable Notifications", variable=self.notification_var,
                                      command=self.toggle_notifications)

        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Weather Terminology", command=self.show_weather_terms)

        # Header frame
        self.header_frame = tk.Frame(root, bg=self.accent_color, height=60)
        self.header_frame.pack(fill=tk.X)

        self.title_label = tk.Label(
            self.header_frame,
            text="Enhanced Weather Forecast",
            font=("Helvetica", 18, "bold"),
            bg=self.accent_color,
            fg="white",
            pady=10
        )
        self.title_label.pack(side=tk.LEFT, padx=20)

        # Location button
        self.location_button = tk.Button(
            self.header_frame,
            text="📍 My Location",
            font=("Helvetica", 10),
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=5,
            command=self.get_current_location
        )
        self.location_button.pack(side=tk.RIGHT, padx=20)

        # Search frame
        self.search_frame = tk.Frame(root, bg=self.bg_color, pady=15)
        self.search_frame.pack(fill=tk.X, padx=20)

        self.search_entry = tk.Entry(
            self.search_frame,
            font=("Helvetica", 14),
            bg="white",
            fg=self.text_color,
            width=25,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#CCCCCC",
            highlightcolor=self.accent_color
        )
        self.search_entry.insert(0, "Enter city name...")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<Return>", lambda event: self.get_weather())
        self.search_entry.pack(side=tk.LEFT, ipady=8)

        self.search_button = tk.Button(
            self.search_frame,
            text="Search",
            font=("Helvetica", 12, "bold"),
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.get_weather
        )
        self.search_button.pack(side=tk.LEFT, padx=5)

        # Favorites button
        self.fav_button = tk.Button(
            self.search_frame,
            text="★",
            font=("Helvetica", 16, "bold"),
            bg="#FFD700",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=5,
            command=self.toggle_favorite
        )
        self.fav_button.pack(side=tk.LEFT, padx=5)

        # Unit toggle button
        self.unit_button = tk.Button(
            self.search_frame,
            text="°C",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=8,
            command=self.toggle_unit
        )
        self.unit_button.pack(side=tk.LEFT, padx=5)

        # Favorites dropdown
        self.fav_var = tk.StringVar()
        self.fav_dropdown = ttk.Combobox(
            self.search_frame,
            textvariable=self.fav_var,
            font=("Helvetica", 12),
            width=15,
            state="readonly"
        )
        self.update_favorites_dropdown()
        self.fav_dropdown.bind("<<ComboboxSelected>>", self.select_favorite)
        self.fav_dropdown.pack(side=tk.LEFT, padx=5)

        # Tabs for different sections
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Content container with border for current weather
        self.content_container = tk.Frame(
            self.notebook,
            bg=self.bg_color,
            padx=10,
            pady=10
        )

        # Content container for forecast
        self.forecast_container = tk.Frame(
            self.notebook,
            bg=self.bg_color,
            padx=10,
            pady=10
        )

        # Content container for additional info
        self.extra_container = tk.Frame(
            self.notebook,
            bg=self.bg_color,
            padx=10,
            pady=10
        )

        # Content container for history
        self.history_container = tk.Frame(
            self.notebook,
            bg=self.bg_color,
            padx=10,
            pady=10
        )

        # Content container for map
        self.map_container = tk.Frame(
            self.notebook,
            bg=self.bg_color,
            padx=10,
            pady=10
        )

        # Add tabs to notebook
        self.notebook.add(self.content_container, text="Current")
        self.notebook.add(self.forecast_container, text="5-Day Forecast")
        self.notebook.add(self.extra_container, text="Additional Info")
        self.notebook.add(self.history_container, text="Weather History")
        self.notebook.add(self.map_container, text="Weather Map")

        # Weather info card
        self.info_card = tk.Frame(
            self.content_container,
            bg=self.card_bg,
            padx=25,
            pady=25,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#DDDDDD"
        )
        self.info_card.pack(fill=tk.BOTH, expand=True)

        # City and date frame
        self.city_frame = tk.Frame(self.info_card, bg=self.card_bg)
        self.city_frame.pack(fill=tk.X)

        self.result_city = tk.Label(
            self.city_frame,
            text="",
            font=("Helvetica", 24, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            anchor="w"
        )
        self.result_city.pack(side=tk.LEFT)

        self.result_time = tk.Label(
            self.city_frame,
            text="",
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg="#777777",
            anchor="e"
        )
        self.result_time.pack(side=tk.RIGHT, pady=10)

        # Main weather info frame
        self.main_weather_frame = tk.Frame(self.info_card, bg=self.card_bg, pady=20)
        self.main_weather_frame.pack(fill=tk.X)

        self.weather_icon_label = tk.Label(
            self.main_weather_frame,
            text="",
            font=("Arial Unicode MS", 48),
            bg=self.card_bg
        )
        self.weather_icon_label.pack(side=tk.LEFT, padx=(0, 15))

        self.temp_desc_frame = tk.Frame(self.main_weather_frame, bg=self.card_bg)
        self.temp_desc_frame.pack(side=tk.LEFT)

        self.result_temp = tk.Label(
            self.temp_desc_frame,
            text="",
            font=("Helvetica", 42, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        self.result_temp.pack(anchor="w")

        self.result_desc = tk.Label(
            self.temp_desc_frame,
            text="",
            font=("Helvetica", 16),
            bg=self.card_bg,
            fg="#555555"
        )
        self.result_desc.pack(anchor="w")

        # Weather alerts frame
        self.alert_frame = tk.Frame(self.info_card, bg="#FFF3CD", padx=10, pady=10)

        self.alert_icon = tk.Label(
            self.alert_frame,
            text="⚠️",
            font=("Arial Unicode MS", 18),
            bg="#FFF3CD",
            fg="#856404"
        )
        self.alert_icon.pack(side=tk.LEFT, padx=(0, 10))

        self.alert_text = tk.Label(
            self.alert_frame,
            text="",
            font=("Helvetica", 12),
            bg="#FFF3CD",
            fg="#856404",
            wraplength=450,
            justify=tk.LEFT
        )
        self.alert_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Separator
        self.separator = ttk.Separator(self.info_card, orient='horizontal')
        self.separator.pack(fill=tk.X, pady=10)

        # Weather details grid
        self.details_frame = tk.Frame(self.info_card, bg=self.card_bg)
        self.details_frame.pack(fill=tk.X, pady=10)

        # Configure grid columns with equal width
        self.details_frame.columnconfigure(0, weight=1)
        self.details_frame.columnconfigure(1, weight=1)

        # Create detail items
        self.create_detail_item(0, 0, "Feels Like")
        self.create_detail_item(0, 1, "Humidity")
        self.create_detail_item(1, 0, "Wind Speed")
        self.create_detail_item(1, 1, "Pressure")
        self.create_detail_item(2, 0, "Sunrise")
        self.create_detail_item(2, 1, "Sunset")

        # Forecast Container Setup
        self.forecast_frame = tk.Frame(
            self.forecast_container,
            bg=self.card_bg,
            padx=15,
            pady=15,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#DDDDDD"
        )
        self.forecast_frame.pack(fill=tk.BOTH, expand=True)

        self.forecast_title = tk.Label(
            self.forecast_frame,
            text="5-Day Weather Forecast",
            font=("Helvetica", 16, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            pady=10
        )
        self.forecast_title.pack()

        # Forecast days will be added dynamically
        self.forecast_days_frame = tk.Frame(
            self.forecast_frame,
            bg=self.card_bg
        )
        self.forecast_days_frame.pack(fill=tk.BOTH, expand=True)

        # Extra info container setup
        self.extra_frame = tk.Frame(
            self.extra_container,
            bg=self.card_bg,
            padx=15,
            pady=15,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#DDDDDD"
        )
        self.extra_frame.pack(fill=tk.BOTH, expand=True)

        # Air quality section
        self.air_quality_title = tk.Label(
            self.extra_frame,
            text="Air Quality Information",
            font=("Helvetica", 16, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            pady=10
        )
        self.air_quality_title.pack(anchor="w")

        self.air_quality_frame = tk.Frame(
            self.extra_frame,
            bg=self.card_bg
        )
        self.air_quality_frame.pack(fill=tk.X, pady=10)

        # Configure air quality grid columns with equal width
        self.air_quality_frame.columnconfigure(0, weight=1)
        self.air_quality_frame.columnconfigure(1, weight=1)

        # Create air quality items
        self.create_aqi_item(0, 0, "AQI Level")
        self.create_aqi_item(0, 1, "Main Pollutant")
        self.create_aqi_item(1, 0, "Health Impact")
        self.create_aqi_item(1, 1, "Recommendation")

        # History container setup
        self.history_frame = tk.Frame(
            self.history_container,
            bg=self.card_bg,
            padx=15,
            pady=15,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#DDDDDD"
        )
        self.history_frame.pack(fill=tk.BOTH, expand=True)

        self.history_title = tk.Label(
            self.history_frame,
            text="Weather History (Last 5 Days)",
            font=("Helvetica", 16, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            pady=10
        )
        self.history_title.pack()

        # History control frame
        self.history_control_frame = tk.Frame(
            self.history_frame,
            bg=self.card_bg,
            pady=10
        )
        self.history_control_frame.pack(fill=tk.X)

        self.history_fetch_button = tk.Button(
            self.history_control_frame,
            text="Fetch Historical Data",
            font=("Helvetica", 12),
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.fetch_history
        )
        self.history_fetch_button.pack(side=tk.LEFT, padx=(0, 10))

        # History data frame - will be populated dynamically
        self.history_data_frame = tk.Frame(
            self.history_frame,
            bg=self.card_bg
        )
        self.history_data_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Map container setup
        self.map_frame = tk.Frame(
            self.map_container,
            bg=self.card_bg,
            padx=15,
            pady=15,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#DDDDDD"
        )
        self.map_frame.pack(fill=tk.BOTH, expand=True)

        self.map_title = tk.Label(
            self.map_frame,
            text="Weather Map",
            font=("Helvetica", 16, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            pady=10
        )
        self.map_title.pack()

        # Map options frame
        self.map_options_frame = tk.Frame(
            self.map_frame,
            bg=self.card_bg,
            pady=10
        )
        self.map_options_frame.pack(fill=tk.X)

        # Map type selection
        self.map_type_label = tk.Label(
            self.map_options_frame,
            text="Map Type:",
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg=self.text_color
        )
        self.map_type_label.pack(side=tk.LEFT, padx=(0, 5))

        self.map_types = ["Temperature", "Clouds", "Precipitation", "Wind", "Pressure"]
        self.map_type_var = tk.StringVar(value=self.map_types[0])
        self.map_type_dropdown = ttk.Combobox(
            self.map_options_frame,
            textvariable=self.map_type_var,
            values=self.map_types,
            font=("Helvetica", 12),
            width=15,
            state="readonly"
        )
        self.map_type_dropdown.pack(side=tk.LEFT, padx=5)
        self.map_type_dropdown.bind("<<ComboboxSelected>>", self.update_map)

        # Load map button
        self.load_map_button = tk.Button(
            self.map_options_frame,
            text="Load Map",
            font=("Helvetica", 12),
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.load_weather_map
        )
        self.load_map_button.pack(side=tk.LEFT, padx=10)

        # Open in browser button
        self.open_map_button = tk.Button(
            self.map_options_frame,
            text="Open in Browser",
            font=("Helvetica", 12),
            bg="#5C6BC0",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.open_weather_map
        )
        self.open_map_button.pack(side=tk.LEFT, padx=10)

        # Map image frame
        self.map_image_frame = tk.Frame(
            self.map_frame,
            bg=self.card_bg,
            pady=10
        )
        self.map_image_frame.pack(fill=tk.BOTH, expand=True)

        self.map_image_label = tk.Label(
            self.map_image_frame,
            text="Select a city and load map to view weather patterns",
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg="#777777",
            wraplength=500
        )
        self.map_image_label.pack(expand=True)

        # Status bar
        self.status_frame = tk.Frame(root, bg="#F5F5F5", height=30)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_bar = tk.Label(
            self.status_frame,
            text="Ready",
            font=("Helvetica", 10),
            bg="#F5F5F5",
            fg="#777777",
            anchor="w",
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.LEFT)

        # Notification indicator
        self.notification_indicator = tk.Label(
            self.status_frame,
            text="🔕 Notifications Off",
            font=("Helvetica", 10),
            bg="#F5F5F5",
            fg="#777777",
            padx=10
        )
        self.notification_indicator.pack(side=tk.RIGHT)

        # Initially hide weather card
        self.info_card.pack_forget()

        # Loading indicators
        self.loading_label = tk.Label(
            self.content_container,
            text="Enter a city to get weather information",
            font=("Helvetica", 14),
            bg=self.bg_color,
            fg="#777777"
        )
        self.loading_label.pack(expand=True)

        self.forecast_loading = tk.Label(
            self.forecast_container,
            text="Enter a city to get forecast information",
            font=("Helvetica", 14),
            bg=self.bg_color,
            fg="#777777"
        )
        self.forecast_loading.pack(expand=True)

        self.extra_loading = tk.Label(
            self.extra_container,
            text="Enter a city to get additional information",
            font=("Helvetica", 14),
            bg=self.bg_color,
            fg="#777777"
        )
        self.extra_loading.pack(expand=True)

        self.history_loading = tk.Label(
            self.history_container,
            text="Fetch historical weather data using the button above",
            font=("Helvetica", 14),
            bg=self.bg_color,
            fg="#777777"
        )
        self.history_loading.pack(expand=True)

        # Start notification checking thread if enabled
        if self.notifications_enabled:
            self.start_notification_thread()

    def create_detail_item(self, row, column, title):
        frame = tk.Frame(self.details_frame, bg=self.card_bg, padx=5, pady=10)
        frame.grid(row=row, column=column, sticky="nsew", padx=10, pady=5)

        title_label = tk.Label(
            frame,
            text=title,
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg="#777777"
        )
        title_label.pack(anchor="w")

        value_label = tk.Label(
            frame,
            text="",
            font=("Helvetica", 18, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        value_label.pack(anchor="w", pady=(5, 0))

        var_name = title.lower().replace(' ', '_') + "_value"
        setattr(self, var_name, value_label)

    def create_aqi_item(self, row, column, title):
        frame = tk.Frame(self.air_quality_frame, bg=self.card_bg, padx=5, pady=10)
        frame.grid(row=row, column=column, sticky="nsew", padx=10, pady=5)

        title_label = tk.Label(
            frame,
            text=title,
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg="#777777"
        )
        title_label.pack(anchor="w")

        value_label = tk.Label(
            frame,
            text="",
            font=("Helvetica", 14, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            wraplength=220,
            justify=tk.LEFT
        )
        value_label.pack(anchor="w", pady=(5, 0))

        var_name = "aqi_" + title.lower().replace(' ', '_') + "_value"
        setattr(self, var_name, value_label)

    def create_forecast_day(self, parent, day_data):
        # Extract date
        dt = datetime.fromtimestamp(day_data['dt'])
        date_str = dt.strftime("%a, %b %d")

        # Create frame for this day
        day_frame = tk.Frame(
            parent,
            bg=self.card_bg,
            highlightthickness=1,
            highlightbackground="#EEEEEE",
            padx=10,
            pady=10
        )
        day_frame.pack(fill=tk.X, pady=5)

        # Date label
        date_label = tk.Label(
            day_frame,
            text=date_str,
            font=("Helvetica", 14, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        date_label.grid(row=0, column=0, sticky="w", padx=5)

        # Weather icon
        icon_code = day_data['weather'][0]['icon'][:2]
        weather_icon = self.weather_icons.get(icon_code, "❓")
        icon_label = tk.Label(
            day_frame,
            text=weather_icon,
            font=("Arial Unicode MS", 24),
            bg=self.card_bg
        )
        icon_label.grid(row=0, column=1, rowspan=2, padx=5)

        # Temperature
        temp_unit = "°F" if self.temp_unit == "imperial" else "°C"
        temp_label = tk.Label(
            day_frame,
            text=f"{int(day_data['main']['temp'])}{temp_unit}",
            font=("Helvetica", 18, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        temp_label.grid(row=0, column=2, padx=5)

        # Description
        desc_label = tk.Label(
            day_frame,
            text=day_data['weather'][0]['description'].capitalize(),
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg="#555555"
        )
        desc_label.grid(row=1, column=0, sticky="w", padx=5)

        # Min/Max temp
        minmax_label = tk.Label(
            day_frame,
            text=f"Min: {int(day_data['main']['temp_min'])}{temp_unit} | Max: {int(day_data['main']['temp_max'])}{temp_unit}",
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg="#555555"
        )
        minmax_label.grid(row=1, column=2, padx=5)

        # Configure grid
        day_frame.columnconfigure(0, weight=3)
        day_frame.columnconfigure(1, weight=1)
        day_frame.columnconfigure(2, weight=3)
        import tkinter as tk
        from tkinter import messagebox, ttk, simpledialog
        import requests
        import json
        from datetime import datetime, timedelta
        import os
        import pickle


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Weather Forecast")
        self.root.geometry("600x750")
        self.root.resizable(False, False)

        # Set color scheme
        self.bg_color = "#E8F1F5"
        self.accent_color = "#005B96"
        self.text_color = "#333333"
        self.card_bg = "#FFFFFF"

        self.root.configure(bg=self.bg_color)

        # API key for OpenWeatherMap
        self.api_key = "9d28222a8f9d1633f4b8b81e61f290ae"

        # Temperature unit (metric by default)
        self.temp_unit = "metric"  # can be "metric" or "imperial"

        # Favorite cities list
        self.fav_cities = []
        self.load_favorites()

        # Current city data
        self.current_city = None
        self.current_weather_data = None

        # Create weather icon representations using text symbols
        self.weather_icons = {
            "01": "☀️",  # clear sky
            "02": "🌤️",  # few clouds
            "03": "☁️",  # scattered clouds
            "04": "☁️",  # broken clouds
            "09": "🌧️",  # shower rain
            "10": "🌦️",  # rain
            "11": "⛈️",  # thunderstorm
            "13": "❄️",  # snow
            "50": "🌫️"  # mist
        }

        # Header frame
        self.header_frame = tk.Frame(root, bg=self.accent_color, height=60)
        self.header_frame.pack(fill=tk.X)

        self.title_label = tk.Label(
            self.header_frame,
            text="Enhanced Weather Forecast",
            font=("Helvetica", 18, "bold"),
            bg=self.accent_color,
            fg="white",
            pady=10
        )
        self.title_label.pack()

        # Search frame
        self.search_frame = tk.Frame(root, bg=self.bg_color, pady=15)
        self.search_frame.pack(fill=tk.X, padx=20)

        self.search_entry = tk.Entry(
            self.search_frame,
            font=("Helvetica", 14),
            bg="white",
            fg=self.text_color,
            width=25,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#CCCCCC",
            highlightcolor=self.accent_color
        )
        self.search_entry.insert(0, "Enter city name...")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<Return>", lambda event: self.get_weather())
        self.search_entry.pack(side=tk.LEFT, ipady=8)

        self.search_button = tk.Button(
            self.search_frame,
            text="Search",
            font=("Helvetica", 12, "bold"),
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.get_weather
        )
        self.search_button.pack(side=tk.LEFT, padx=5)

        # Favorites button
        self.fav_button = tk.Button(
            self.search_frame,
            text="★",
            font=("Helvetica", 16, "bold"),
            bg="#FFD700",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=5,
            command=self.toggle_favorite
        )
        self.fav_button.pack(side=tk.LEFT, padx=5)

        # Unit toggle button
        self.unit_button = tk.Button(
            self.search_frame,
            text="°C",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            relief=tk.FLAT,
            padx=8,
            pady=8,
            command=self.toggle_unit
        )
        self.unit_button.pack(side=tk.LEFT, padx=5)

        # Favorites dropdown
        self.fav_var = tk.StringVar()
        self.fav_dropdown = ttk.Combobox(
            self.search_frame,
            textvariable=self.fav_var,
            font=("Helvetica", 12),
            width=15,
            state="readonly"
        )
        self.update_favorites_dropdown()
        self.fav_dropdown.bind("<<ComboboxSelected>>", self.select_favorite)
        self.fav_dropdown.pack(side=tk.LEFT, padx=5)

        # Tabs for current weather and forecast
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Content container with border for current weather
        self.content_container = tk.Frame(
            self.notebook,
            bg=self.bg_color,
            padx=10,
            pady=10
        )

        # Content container for forecast
        self.forecast_container = tk.Frame(
            self.notebook,
            bg=self.bg_color,
            padx=10,
            pady=10
        )

        # Content container for additional info
        self.extra_container = tk.Frame(
            self.notebook,
            bg=self.bg_color,
            padx=10,
            pady=10
        )

        # Add tabs to notebook
        self.notebook.add(self.content_container, text="Current")
        self.notebook.add(self.forecast_container, text="5-Day Forecast")
        self.notebook.add(self.extra_container, text="Additional Info")

        # Weather info card
        self.info_card = tk.Frame(
            self.content_container,
            bg=self.card_bg,
            padx=25,
            pady=25,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#DDDDDD"
        )
        self.info_card.pack(fill=tk.BOTH, expand=True)

        # City and date frame
        self.city_frame = tk.Frame(self.info_card, bg=self.card_bg)
        self.city_frame.pack(fill=tk.X)

        self.result_city = tk.Label(
            self.city_frame,
            text="",
            font=("Helvetica", 24, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            anchor="w"
        )
        self.result_city.pack(side=tk.LEFT)

        self.result_time = tk.Label(
            self.city_frame,
            text="",
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg="#777777",
            anchor="e"
        )
        self.result_time.pack(side=tk.RIGHT, pady=10)

        # Main weather info frame
        self.main_weather_frame = tk.Frame(self.info_card, bg=self.card_bg, pady=20)
        self.main_weather_frame.pack(fill=tk.X)

        self.weather_icon_label = tk.Label(
            self.main_weather_frame,
            text="",
            font=("Arial Unicode MS", 48),
            bg=self.card_bg
        )
        self.weather_icon_label.pack(side=tk.LEFT, padx=(0, 15))

        self.temp_desc_frame = tk.Frame(self.main_weather_frame, bg=self.card_bg)
        self.temp_desc_frame.pack(side=tk.LEFT)

        self.result_temp = tk.Label(
            self.temp_desc_frame,
            text="",
            font=("Helvetica", 42, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        self.result_temp.pack(anchor="w")

        self.result_desc = tk.Label(
            self.temp_desc_frame,
            text="",
            font=("Helvetica", 16),
            bg=self.card_bg,
            fg="#555555"
        )
        self.result_desc.pack(anchor="w")

        # Weather alerts frame
        self.alert_frame = tk.Frame(self.info_card, bg="#FFF3CD", padx=10, pady=10)

        self.alert_icon = tk.Label(
            self.alert_frame,
            text="⚠️",
            font=("Arial Unicode MS", 18),
            bg="#FFF3CD",
            fg="#856404"
        )
        self.alert_icon.pack(side=tk.LEFT, padx=(0, 10))

        self.alert_text = tk.Label(
            self.alert_frame,
            text="",
            font=("Helvetica", 12),
            bg="#FFF3CD",
            fg="#856404",
            wraplength=450,
            justify=tk.LEFT
        )
        self.alert_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Separator
        self.separator = ttk.Separator(self.info_card, orient='horizontal')
        self.separator.pack(fill=tk.X, pady=10)

        # Weather details grid
        self.details_frame = tk.Frame(self.info_card, bg=self.card_bg)
        self.details_frame.pack(fill=tk.X, pady=10)

        # Configure grid columns with equal width
        self.details_frame.columnconfigure(0, weight=1)
        self.details_frame.columnconfigure(1, weight=1)

        # Create detail items
        self.create_detail_item(0, 0, "Feels Like")
        self.create_detail_item(0, 1, "Humidity")
        self.create_detail_item(1, 0, "Wind Speed")
        self.create_detail_item(1, 1, "Pressure")
        self.create_detail_item(2, 0, "Sunrise")
        self.create_detail_item(2, 1, "Sunset")

        # Forecast Container Setup
        self.forecast_frame = tk.Frame(
            self.forecast_container,
            bg=self.card_bg,
            padx=15,
            pady=15,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#DDDDDD"
        )
        self.forecast_frame.pack(fill=tk.BOTH, expand=True)

        self.forecast_title = tk.Label(
            self.forecast_frame,
            text="5-Day Weather Forecast",
            font=("Helvetica", 16, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            pady=10
        )
        self.forecast_title.pack()

        # Forecast days will be added dynamically
        self.forecast_days_frame = tk.Frame(
            self.forecast_frame,
            bg=self.card_bg
        )
        self.forecast_days_frame.pack(fill=tk.BOTH, expand=True)

        # Extra info container setup
        self.extra_frame = tk.Frame(
            self.extra_container,
            bg=self.card_bg,
            padx=15,
            pady=15,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#DDDDDD"
        )
        self.extra_frame.pack(fill=tk.BOTH, expand=True)

        # Air quality section
        self.air_quality_title = tk.Label(
            self.extra_frame,
            text="Air Quality Information",
            font=("Helvetica", 16, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            pady=10
        )
        self.air_quality_title.pack(anchor="w")

        self.air_quality_frame = tk.Frame(
            self.extra_frame,
            bg=self.card_bg
        )
        self.air_quality_frame.pack(fill=tk.X, pady=10)

        # Configure air quality grid columns with equal width
        self.air_quality_frame.columnconfigure(0, weight=1)
        self.air_quality_frame.columnconfigure(1, weight=1)

        # Create air quality items
        self.create_aqi_item(0, 0, "AQI Level")
        self.create_aqi_item(0, 1, "Main Pollutant")
        self.create_aqi_item(1, 0, "Health Impact")
        self.create_aqi_item(1, 1, "Recommendation")

        # Status bar
        self.status_frame = tk.Frame(root, bg="#F5F5F5", height=30)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_bar = tk.Label(
            self.status_frame,
            text="Ready",
            font=("Helvetica", 10),
            bg="#F5F5F5",
            fg="#777777",
            anchor="w",
            padx=10,
            pady=5
        )
        self.status_bar.pack(side=tk.LEFT)

        # Initially hide weather card
        self.info_card.pack_forget()

        # Loading indicator
        self.loading_label = tk.Label(
            self.content_container,
            text="Enter a city to get weather information",
            font=("Helvetica", 14),
            bg=self.bg_color,
            fg="#777777"
        )
        self.loading_label.pack(expand=True)

        # Loading indicators for other tabs
        self.forecast_loading = tk.Label(
            self.forecast_container,
            text="Enter a city to get forecast information",
            font=("Helvetica", 14),
            bg=self.bg_color,
            fg="#777777"
        )
        self.forecast_loading.pack(expand=True)

        self.extra_loading = tk.Label(
            self.extra_container,
            text="Enter a city to get additional information",
            font=("Helvetica", 14),
            bg=self.bg_color,
            fg="#777777"
        )
        self.extra_loading.pack(expand=True)

    def create_detail_item(self, row, column, title):
        frame = tk.Frame(self.details_frame, bg=self.card_bg, padx=5, pady=10)
        frame.grid(row=row, column=column, sticky="nsew", padx=10, pady=5)

        title_label = tk.Label(
            frame,
            text=title,
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg="#777777"
        )
        title_label.pack(anchor="w")

        value_label = tk.Label(
            frame,
            text="",
            font=("Helvetica", 18, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        value_label.pack(anchor="w", pady=(5, 0))

        var_name = title.lower().replace(' ', '_') + "_value"
        setattr(self, var_name, value_label)

    def create_aqi_item(self, row, column, title):
        frame = tk.Frame(self.air_quality_frame, bg=self.card_bg, padx=5, pady=10)
        frame.grid(row=row, column=column, sticky="nsew", padx=10, pady=5)

        title_label = tk.Label(
            frame,
            text=title,
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg="#777777"
        )
        title_label.pack(anchor="w")

        value_label = tk.Label(
            frame,
            text="",
            font=("Helvetica", 14, "bold"),
            bg=self.card_bg,
            fg=self.text_color,
            wraplength=220,
            justify=tk.LEFT
        )
        value_label.pack(anchor="w", pady=(5, 0))

        var_name = "aqi_" + title.lower().replace(' ', '_') + "_value"
        setattr(self, var_name, value_label)

    def create_forecast_day(self, parent, day_data):
        # Extract date
        dt = datetime.fromtimestamp(day_data['dt'])
        date_str = dt.strftime("%a, %b %d")

        # Create frame for this day
        day_frame = tk.Frame(
            parent,
            bg=self.card_bg,
            highlightthickness=1,
            highlightbackground="#EEEEEE",
            padx=10,
            pady=10
        )
        day_frame.pack(fill=tk.X, pady=5)

        # Date label
        date_label = tk.Label(
            day_frame,
            text=date_str,
            font=("Helvetica", 14, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        date_label.grid(row=0, column=0, sticky="w", padx=5)

        # Weather icon
        icon_code = day_data['weather'][0]['icon'][:2]
        weather_icon = self.weather_icons.get(icon_code, "❓")
        icon_label = tk.Label(
            day_frame,
            text=weather_icon,
            font=("Arial Unicode MS", 24),
            bg=self.card_bg
        )
        icon_label.grid(row=0, column=1, rowspan=2, padx=5)

        # Temperature
        temp_unit = "°F" if self.temp_unit == "imperial" else "°C"
        temp_label = tk.Label(
            day_frame,
            text=f"{int(day_data['main']['temp'])}{temp_unit}",
            font=("Helvetica", 18, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        temp_label.grid(row=0, column=2, padx=5)

        # Description
        desc_label = tk.Label(
            day_frame,
            text=day_data['weather'][0]['description'].capitalize(),
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg="#555555"
        )
        desc_label.grid(row=1, column=0, sticky="w", padx=5)

        # Min/Max temp
        minmax_label = tk.Label(
            day_frame,
            text=f"Min: {int(day_data['main']['temp_min'])}{temp_unit} | Max: {int(day_data['main']['temp_max'])}{temp_unit}",
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg="#555555"
        )
        minmax_label.grid(row=1, column=2, padx=5)

        # Configure grid
        day_frame.columnconfigure(0, weight=3)
        day_frame.columnconfigure(1, weight=1)
        day_frame.columnconfigure(2, weight=3)

    def clear_placeholder(self, event):
        if self.search_entry.get() == "Enter city name...":
            self.search_entry.delete(0, tk.END)

    def toggle_unit(self):
        if self.temp_unit == "metric":
            self.temp_unit = "imperial"
            self.unit_button.config(text="°F")
        else:
            self.temp_unit = "metric"
            self.unit_button.config(text="°C")

        # Refresh weather data if we have a city loaded
        if self.current_city:
            self.get_weather_for_city(self.current_city)

    def load_favorites(self):
        try:
            if os.path.exists("weather_favorites.pkl"):
                with open("weather_favorites.pkl", "rb") as f:
                    self.fav_cities = pickle.load(f)
        except Exception as e:
            print(f"Error loading favorites: {e}")
            self.fav_cities = []

    def save_favorites(self):
        try:
            with open("weather_favorites.pkl", "wb") as f:
                pickle.dump(self.fav_cities, f)
        except Exception as e:
            print(f"Error saving favorites: {e}")

    def update_favorites_dropdown(self):
        if self.fav_cities:
            self.fav_dropdown['values'] = ["-- Favorites --"] + self.fav_cities
            self.fav_dropdown.current(0)
        else:
            self.fav_dropdown['values'] = ["-- No Favorites --"]
            self.fav_dropdown.current(0)

    def select_favorite(self, event):
        selected = self.fav_var.get()
        if selected not in ["-- Favorites --", "-- No Favorites --"]:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, selected)
            self.get_weather()

    def toggle_favorite(self):
        if not self.current_city:
            messagebox.showinfo("Info", "Search for a city first before adding to favorites")
            return

        if self.current_city in self.fav_cities:
            self.fav_cities.remove(self.current_city)
            messagebox.showinfo("Info", f"{self.current_city} removed from favorites")
        else:
            self.fav_cities.append(self.current_city)
            messagebox.showinfo("Info", f"{self.current_city} added to favorites")

        self.save_favorites()
        self.update_favorites_dropdown()

    def get_weather(self):
        city = self.search_entry.get().strip()
        if city == "Enter city name..." or not city:
            messagebox.showerror("Error", "Please enter a city name")
            return

        self.get_weather_for_city(city)

    def get_weather_for_city(self, city):
        self.status_bar.config(text="Searching...")

        # Hide info card and show loading indicator
        self.info_card.pack_forget()
        self.loading_label.config(text="Loading weather data...")
        self.loading_label.pack(expand=True)

        # Hide forecast frames
        for widget in self.forecast_days_frame.winfo_children():
            widget.destroy()
        self.forecast_frame.pack_forget()
        self.forecast_loading.pack(expand=True)

        # Hide extra info
        self.extra_frame.pack_forget()
        self.extra_loading.pack(expand=True)

        self.root.update()

        try:
            # Current weather API call
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units={self.temp_unit}"
            response = requests.get(url)
            data = json.loads(response.text)

            if data["cod"] != 200:
                messagebox.showerror("Error", f"City not found or {data['message']}")
                self.status_bar.config(text="Ready")
                self.loading_label.config(text="Enter a city to get weather information")
                self.forecast_loading.config(text="Enter a city to get forecast information")
                self.extra_loading.config(text="Enter a city to get additional information")
                return

            # Store current city and data
            self.current_city = f"{data['name']}, {data['sys']['country']}"
            self.current_weather_data = data

            # Update UI with weather data
            self.result_city.config(text=self.current_city)

            local_time = datetime.utcfromtimestamp(data['dt'] + data['timezone'])
            self.result_time.config(text=f"Last Updated: {local_time.strftime('%I:%M %p, %d %b %Y')}")

            temp_unit = "°F" if self.temp_unit == "imperial" else "°C"
            self.result_temp.config(text=f"{int(data['main']['temp'])}{temp_unit}")

            weather_desc = data['weather'][0]['description'].capitalize()
            self.result_desc.config(text=weather_desc)

            # Update the icon based on weather condition
            icon_code = data['weather'][0]['icon'][:2]  # First two characters of the icon code
            if icon_code in self.weather_icons:
                self.weather_icon_label.config(text=self.weather_icons[icon_code])

            # Update detail values
            self.feels_like_value.config(text=f"{int(data['main']['feels_like'])}{temp_unit}")
            self.humidity_value.config(text=f"{data['main']['humidity']}%")

            wind_unit = "mph" if self.temp_unit == "imperial" else "m/s"
            self.wind_speed_value.config(text=f"{data['wind']['speed']} {wind_unit}")

            self.pressure_value.config(text=f"{data['main']['pressure']} hPa")

            # Sunrise and sunset times
            sunrise_time = datetime.utcfromtimestamp(data['sys']['sunrise'] + data['timezone'])
            sunset_time = datetime.utcfromtimestamp(data['sys']['sunset'] + data['timezone'])

            self.sunrise_value.config(text=f"{sunrise_time.strftime('%I:%M %p')}")
            self.sunset_value.config(text=f"{sunset_time.strftime('%I:%M %p')}")

            # Check for alerts - OpenWeatherMap doesn't always include alerts in current weather
            if 'alerts' in data:
                self.alert_frame.pack(fill=tk.X, pady=10, before=self.separator)
                self.alert_text.config(text=data['alerts'][0]['description'])
            else:
                # Remove alert frame if it's currently displayed
                if self.alert_frame.winfo_ismapped():
                    self.alert_frame.pack_forget()

            # Hide loading label and show info card
            self.loading_label.pack_forget()
            self.info_card.pack(fill=tk.BOTH, expand=True)

            # Get 5-day forecast data
            self.get_forecast(city)

            # Get air quality data
            self.get_air_quality(data['coord']['lat'], data['coord']['lon'])

            self.status_bar.config(text=f"Weather data for {data['name']} retrieved successfully")

        except requests.ConnectionError:
            messagebox.showerror("Connection Error", "Please check your internet connection")
            self.status_bar.config(text="Connection Error")
            self.loading_label.config(text="Connection error. Please try again.")
            self.forecast_loading.config(text="Connection error. Please try again.")
            self.extra_loading.config(text="Connection error. Please try again.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_bar.config(text="Error occurred")
            self.loading_label.config(text="An error occurred. Please try again.")
            self.forecast_loading.config(text="An error occurred. Please try again.")
            self.extra_loading.config(text="An error occurred. Please try again.")

    def get_forecast(self, city):
        try:
            # 5-day forecast API call
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}&units={self.temp_unit}"
            response = requests.get(url)
            data = json.loads(response.text)

            if data["cod"] != "200":
                self.forecast_loading.config(text=f"Forecast data error: {data.get('message', 'Unknown error')}")
                return

            # Process forecast data - get one forecast per day (noon time)
            forecast_days = {}

            # Filter to get one entry per day (at around noon)
            for item in data['list']:
                dt = datetime.fromtimestamp(item['dt'])
                day_key = dt.strftime("%Y-%m-%d")

                # If we don't have this day yet, or if this time is closer to noon than existing one
                hour = dt.hour
                if day_key not in forecast_days or abs(hour - 12) < abs(
                        datetime.fromtimestamp(forecast_days[day_key]['dt']).hour - 12):
                    forecast_days[day_key] = item

            # Clear any existing forecast items
            for widget in self.forecast_days_frame.winfo_children():
                widget.destroy()

            # Create forecast day items (limit to 5 days)
            for day_key in list(forecast_days.keys())[:5]:
                self.create_forecast_day(self.forecast_days_frame, forecast_days[day_key])

            # Hide loading and show forecast frame
            self.forecast_loading.pack_forget()
            self.forecast_frame.pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            self.forecast_loading.config(text=f"Error getting forecast: {str(e)}")

    def get_air_quality(self, lat, lon):
        try:
            # Air quality API call
            url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={self.api_key}"
            response = requests.get(url)
            data = json.loads(response.text)

            if 'list' not in data or not data['list']:
                self.extra_loading.config(text="Air quality data not available for this location")
                return

            aqi_data = data['list'][0]
            aqi_level = aqi_data['main']['aqi']

            # AQI level interpretation
            aqi_levels = {
                1: "Good",
                2: "Fair",
                3: "Moderate",
                4: "Poor",
                5: "Very Poor"
            }

            aqi_colors = {
                1: "#4CAF50",  # Good - Green
                2: "#8BC34A",  # Fair - Light Green
                3: "#FFC107",  # Moderate - Yellow
                4: "#FF9800",  # Poor - Orange
                5: "#F44336"  # Very Poor - Red
            }

            aqi_health = {
                1: "Air quality is good. Ideal for outdoor activities.",
                2: "Air quality is acceptable. Some pollutants may affect very sensitive individuals.",
                3: "Members of sensitive groups may experience health effects. General public is less likely to be affected.",
                4: "Everyone may begin to experience health effects. Sensitive groups may experience more serious effects.",
                5: "Health alert: Everyone may experience more serious health effects. Avoid outdoor activities."
            }

            aqi_recommendations = {
                1: "Enjoy outdoor activities",
                2: "Sensitive individuals should consider limiting prolonged outdoor exertion",
                3: "Sensitive groups should limit outdoor exertion",
                4: "Everyone should reduce outdoor exertion",
                5: "Everyone should avoid outdoor activities"
            }

            # Get the main pollutant
            pollutants = aqi_data['components']
            max_pollutant = max(pollutants, key=pollutants.get)
            pollutant_names = {
                "co": "Carbon Monoxide (CO)",
                "no": "Nitrogen Monoxide (NO)",
                "no2": "Nitrogen Dioxide (NO₂)",
                "o3": "Ozone (O₃)",
                "so2": "Sulfur Dioxide (SO₂)",
                "pm2_5": "Fine Particles (PM2.5)",
                "pm10": "Coarse Particles (PM10)",
                "nh3": "Ammonia (NH₃)"
            }

            # Update AQI values
            self.aqi_aqi_level_value.config(
                text=f"{aqi_levels[aqi_level]}",
                fg=aqi_colors[aqi_level]
            )
            self.aqi_main_pollutant_value.config(text=pollutant_names.get(max_pollutant, max_pollutant))
            self.aqi_health_impact_value.config(text=aqi_health[aqi_level])
            self.aqi_recommendation_value.config(text=aqi_recommendations[aqi_level])

            # Hide loading and show extra frame
            self.extra_loading.pack_forget()
            self.extra_frame.pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            self.extra_loading.config(text=f"Error getting air quality data: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()