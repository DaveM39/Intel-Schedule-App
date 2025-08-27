import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
from datetime import datetime


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Weather App")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # API key for OpenWeatherMap (You'll need to replace this with your own)
        self.api_key = "9d28222a8f9d1633f4b8b81e61f290ae"

        # Create frames
        self.search_frame = tk.Frame(root, bg="#f0f0f0")
        self.search_frame.pack(pady=20)

        self.result_frame = tk.Frame(root, bg="#f0f0f0")
        self.result_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Search widgets
        self.city_label = tk.Label(
            self.search_frame,
            text="Enter City Name:",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        self.city_label.grid(row=0, column=0, padx=5)

        self.city_entry = tk.Entry(
            self.search_frame,
            font=("Arial", 12),
            width=15
        )
        self.city_entry.grid(row=0, column=1, padx=5)

        self.search_button = tk.Button(
            self.search_frame,
            text="Search",
            font=("Arial", 10),
            bg="#4a7abc",
            fg="white",
            command=self.get_weather
        )
        self.search_button.grid(row=0, column=2, padx=5)

        # Results widgets
        self.result_city = tk.Label(
            self.result_frame,
            text="",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        )
        self.result_city.pack(pady=(20, 5))

        self.result_time = tk.Label(
            self.result_frame,
            text="",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#555555"
        )
        self.result_time.pack(pady=(0, 10))

        self.result_temp = tk.Label(
            self.result_frame,
            text="",
            font=("Arial", 35),
            bg="#f0f0f0"
        )
        self.result_temp.pack(pady=5)

        self.result_desc = tk.Label(
            self.result_frame,
            text="",
            font=("Arial", 14),
            bg="#f0f0f0"
        )
        self.result_desc.pack(pady=5)

        self.details_frame = tk.Frame(self.result_frame, bg="#f0f0f0")
        self.details_frame.pack(pady=15, fill=tk.X)

        # First row of details
        self.feels_like_label = tk.Label(
            self.details_frame,
            text="Feels Like",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.feels_like_label.grid(row=0, column=0, padx=20, pady=5)

        self.humidity_label = tk.Label(
            self.details_frame,
            text="Humidity",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.humidity_label.grid(row=0, column=1, padx=20, pady=5)

        self.feels_like_value = tk.Label(
            self.details_frame,
            text="",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        self.feels_like_value.grid(row=1, column=0, padx=20, pady=5)

        self.humidity_value = tk.Label(
            self.details_frame,
            text="",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        self.humidity_value.grid(row=1, column=1, padx=20, pady=5)

        # Second row of details
        self.wind_label = tk.Label(
            self.details_frame,
            text="Wind Speed",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.wind_label.grid(row=2, column=0, padx=20, pady=5)

        self.pressure_label = tk.Label(
            self.details_frame,
            text="Pressure",
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.pressure_label.grid(row=2, column=1, padx=20, pady=5)

        self.wind_value = tk.Label(
            self.details_frame,
            text="",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        self.wind_value.grid(row=3, column=0, padx=20, pady=5)

        self.pressure_value = tk.Label(
            self.details_frame,
            text="",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        self.pressure_value.grid(row=3, column=1, padx=20, pady=5)

        # Status bar
        self.status_bar = tk.Label(
            root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind Enter key to search function
        self.city_entry.bind("<Return>", lambda event: self.get_weather())

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showerror("Error", "Please enter a city name")
            return

        self.status_bar.config(text="Searching...")
        self.root.update()

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            data = json.loads(response.text)

            if data["cod"] != 200:
                messagebox.showerror("Error", f"City not found or {data['message']}")
                self.status_bar.config(text="Ready")
                return

            # Update UI with weather data
            self.result_city.config(text=f"{data['name']}, {data['sys']['country']}")

            local_time = datetime.utcfromtimestamp(data['dt'] + data['timezone'])
            self.result_time.config(text=f"Last Updated: {local_time.strftime('%I:%M %p, %d %b %Y')}")

            self.result_temp.config(text=f"{int(data['main']['temp'])}°C")

            weather_desc = data['weather'][0]['description'].capitalize()
            self.result_desc.config(text=weather_desc)

            self.feels_like_value.config(text=f"{int(data['main']['feels_like'])}°C")
            self.humidity_value.config(text=f"{data['main']['humidity']}%")
            self.wind_value.config(text=f"{data['wind']['speed']} m/s")
            self.pressure_value.config(text=f"{data['main']['pressure']} hPa")

            self.status_bar.config(text="Data retrieved successfully")

        except requests.ConnectionError:
            messagebox.showerror("Connection Error", "Please check your internet connection")
            self.status_bar.config(text="Connection Error")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_bar.config(text="Error occurred")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()