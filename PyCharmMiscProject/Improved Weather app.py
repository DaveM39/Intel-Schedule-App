import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
from datetime import datetime


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Forecast")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        # Set color scheme
        self.bg_color = "#E8F1F5"
        self.accent_color = "#005B96"
        self.text_color = "#333333"
        self.card_bg = "#FFFFFF"

        self.root.configure(bg=self.bg_color)

        # API key for OpenWeatherMap
        self.api_key = "9d28222a8f9d1633f4b8b81e61f290ae"

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
            text="Weather Forecast",
            font=("Helvetica", 18, "bold"),
            bg=self.accent_color,
            fg="white",
            pady=10
        )
        self.title_label.pack()

        # Search frame
        self.search_frame = tk.Frame(root, bg=self.bg_color, pady=20)
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
        self.search_button.pack(side=tk.LEFT, padx=10)

        # Content container with border
        self.content_container = tk.Frame(
            root,
            bg=self.bg_color,
            padx=20,
            pady=20
        )
        self.content_container.pack(fill=tk.BOTH, expand=True)

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

        # Fix: Use a properly formatted variable name
        var_name = title.lower().replace(' ', '_') + "_value"
        setattr(self, var_name, value_label)

    def clear_placeholder(self, event):
        if self.search_entry.get() == "Enter city name...":
            self.search_entry.delete(0, tk.END)

    def get_weather(self):
        city = self.search_entry.get().strip()
        if city == "Enter city name..." or not city:
            messagebox.showerror("Error", "Please enter a city name")
            return

        self.status_bar.config(text="Searching...")

        # Hide info card and show loading indicator
        self.info_card.pack_forget()
        self.loading_label.config(text="Loading weather data...")
        self.loading_label.pack(expand=True)

        self.root.update()

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            data = json.loads(response.text)

            if data["cod"] != 200:
                messagebox.showerror("Error", f"City not found or {data['message']}")
                self.status_bar.config(text="Ready")
                self.loading_label.config(text="Enter a city to get weather information")
                return

            # Update UI with weather data
            self.result_city.config(text=f"{data['name']}, {data['sys']['country']}")

            local_time = datetime.utcfromtimestamp(data['dt'] + data['timezone'])
            self.result_time.config(text=f"Last Updated: {local_time.strftime('%I:%M %p, %d %b %Y')}")

            self.result_temp.config(text=f"{int(data['main']['temp'])}°C")

            weather_desc = data['weather'][0]['description'].capitalize()
            self.result_desc.config(text=weather_desc)

            # Update the icon based on weather condition
            icon_code = data['weather'][0]['icon'][:2]  # First two characters of the icon code
            if icon_code in self.weather_icons:
                self.weather_icon_label.config(text=self.weather_icons[icon_code])

            # Update detail values
            self.feels_like_value.config(text=f"{int(data['main']['feels_like'])}°C")
            self.humidity_value.config(text=f"{data['main']['humidity']}%")
            self.wind_speed_value.config(text=f"{data['wind']['speed']} m/s")
            self.pressure_value.config(text=f"{data['main']['pressure']} hPa")

            # Hide loading label and show info card
            self.loading_label.pack_forget()
            self.info_card.pack(fill=tk.BOTH, expand=True)

            self.status_bar.config(text=f"Weather data for {data['name']} retrieved successfully")

        except requests.ConnectionError:
            messagebox.showerror("Connection Error", "Please check your internet connection")
            self.status_bar.config(text="Connection Error")
            self.loading_label.config(text="Connection error. Please try again.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_bar.config(text="Error occurred")
            self.loading_label.config(text="An error occurred. Please try again.")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()