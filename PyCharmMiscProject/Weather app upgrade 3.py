# Weather App – Full Upgrade with Geolocation, Maps, History, Notifications, and Themes

import tkinter as tk
from tkinter import ttk, messagebox
import requests, json, os, pickle, threading, time, math, webbrowser
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageTk

# Optional desktop notification (plyer is cross‑platform)
try:
    from plyer import notification
    NOTIFIER_AVAILABLE = True
except ImportError:
    NOTIFIER_AVAILABLE = False

API_KEY = "9d28222a8f9d1633f4b8b81e61f290ae"  # <‑‑ replace with your own if you hit limits


def deg2num(lat, lon, zoom):
    """Convert lat/lon to XYZ tile numbers (Slippy Map)."""
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


class WeatherApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Enhanced Weather Forecast")
        self.root.geometry("650x780")
        self.root.resizable(False, False)

        # ------------- APP STATE -----------------
        self.temp_unit = "metric"           # "metric" or "imperial"
        self.current_theme = "light"        # default theme
        self.fav_cities = []
        self.current_city = None
        self.current_lat = None
        self.current_lon = None
        self.notifications_enabled = False
        self._stop_notification_event = threading.Event()
        self.last_alert = None              # to avoid spam‑alerting

        # ------------- THEMES --------------------
        self.color_schemes = {
            "light":  {"bg": "#E8F1F5", "accent": "#005B96", "text": "#333", "card": "#FFFFFF"},
            "dark":   {"bg": "#1E1E1E", "accent": "#2080F0", "text": "#FFF", "card": "#2D2D2D"},
            "nature": {"bg": "#E8F5E9", "accent": "#388E3C", "text": "#212121", "card": "#FFFFFF"},
            "sunset": {"bg": "#FBE9E7", "accent": "#D84315", "text": "#212121", "card": "#FFFFFF"},
        }
        self.apply_theme(self.current_theme, first_time=True)

        # ------------- MENU BAR ------------------
        menubar = tk.Menu(root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Themes", menu=view_menu)
        for t in self.color_schemes:
            view_menu.add_command(label=t.capitalize(), command=lambda theme=t: self.apply_theme(theme))

        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        self.notifications_var = tk.BooleanVar(value=False)
        settings_menu.add_checkbutton(label="Enable Severe‑Weather Notifications", variable=self.notifications_var,
                                      command=self.toggle_notifications)

        # ------------- HEADER --------------------
        header = tk.Frame(root, bg=self.accent_color, height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="Enhanced Weather Forecast", fg="white", bg=self.accent_color,
                 font=("Helvetica", 18, "bold")).pack(side=tk.LEFT, padx=20)
        tk.Button(header, text="📍 My Location", bg=self.accent_color, fg="white", relief=tk.FLAT,
                  command=self.get_current_location).pack(side=tk.RIGHT, padx=20)

        # ------------- SEARCH BAR ---------------
        search_frame = tk.Frame(root, bg=self.bg_color, pady=15)
        search_frame.pack(fill=tk.X, padx=20)
        self.search_entry = tk.Entry(search_frame, font=("Helvetica", 14), width=24)
        self.search_entry.insert(0, "Enter city name…")
        self.search_entry.bind("<FocusIn>", lambda e: self._clear_placeholder())
        self.search_entry.bind("<Return>", lambda e: self.get_weather())
        self.search_entry.pack(side=tk.LEFT, ipady=4)
        tk.Button(search_frame, text="Search", bg=self.accent_color, fg="white", command=self.get_weather).pack(side=tk.LEFT, padx=6)
        self.unit_btn = tk.Button(search_frame, text="°C", bg="#4CAF50", fg="white", command=self.toggle_unit)
        self.unit_btn.pack(side=tk.LEFT, padx=6)

        # ------------- NOTEBOOK ------------------
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)
        self.tab_current = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_forecast = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_history = tk.Frame(self.notebook, bg=self.bg_color)
        self.tab_map = tk.Frame(self.notebook, bg=self.bg_color)
        for tab, name in [(self.tab_current, "Current"), (self.tab_forecast, "5‑Day Forecast"),
                          (self.tab_history, "History"), (self.tab_map, "Weather Map")]:
            self.notebook.add(tab, text=name)

        # ---- Current weather card ----
        self.card = tk.Frame(self.tab_current, bg=self.card_bg, bd=1, relief=tk.FLAT)
        self.card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.lbl_city = tk.Label(self.card, text="", font=("Helvetica", 24, "bold"), bg=self.card_bg, anchor="w")
        self.lbl_city.pack(anchor="w", pady=(10, 0))
        self.lbl_time = tk.Label(self.card, text="", bg=self.card_bg, fg="#777")
        self.lbl_time.pack(anchor="w")
        self.lbl_icon = tk.Label(self.card, text="", font=("Arial Unicode MS", 56), bg=self.card_bg)
        self.lbl_icon.pack(pady=(10, 0))
        self.lbl_temp = tk.Label(self.card, text="", font=("Helvetica", 40, "bold"), bg=self.card_bg)
        self.lbl_temp.pack()
        self.lbl_desc = tk.Label(self.card, text="", font=("Helvetica", 16), bg=self.card_bg, fg="#555")
        self.lbl_desc.pack()

        # ---- Forecast frame ----
        self.frame_forecast = tk.Frame(self.tab_forecast, bg=self.bg_color)
        self.frame_forecast.pack(fill=tk.BOTH, expand=True)

        # ---- History frame ----
        self.btn_fetch_hist = tk.Button(self.tab_history, text="Fetch last 5 days", bg=self.accent_color, fg="white",
                                        command=self.fetch_history)
        self.btn_fetch_hist.pack(pady=10)
        self.frame_history = tk.Frame(self.tab_history, bg=self.bg_color)
        self.frame_history.pack(fill=tk.BOTH, expand=True)

        # ---- Map frame ----
        map_top = tk.Frame(self.tab_map, bg=self.bg_color)
        map_top.pack(fill=tk.X, pady=6)
        self.map_layer_var = tk.StringVar(value="Temperature")
        layers = ["Temperature", "Clouds", "Precipitation", "Wind", "Pressure"]
        ttk.Combobox(map_top, textvariable=self.map_layer_var, values=layers, width=14, state="readonly").pack(side=tk.LEFT, padx=10)
        tk.Button(map_top, text="Load Map", bg=self.accent_color, fg="white", command=self.load_weather_map).pack(side=tk.LEFT)
        tk.Button(map_top, text="Open in Browser", command=self.open_weather_map).pack(side=tk.LEFT, padx=6)
        self.lbl_map = tk.Label(self.tab_map, text="Map will appear here", bg=self.bg_color)
        self.lbl_map.pack(expand=True)

        # ---- Status bar ----
        status_frame = tk.Frame(root, bg="#F5F5F5")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_lbl = tk.Label(status_frame, text="Ready", bg="#F5F5F5", anchor="w")
        self.status_lbl.pack(side=tk.LEFT, padx=10)
        self.notif_lbl = tk.Label(status_frame, text="🔕", bg="#F5F5F5")
        self.notif_lbl.pack(side=tk.RIGHT, padx=10)

    # ------------------------------------------------------ THEME HANDLING
    def apply_theme(self, theme: str, first_time=False):
        if theme not in self.color_schemes:
            return
        self.current_theme = theme
        scheme = self.color_schemes[theme]
        self.bg_color, self.accent_color, self.text_color, self.card_bg = (
            scheme["bg"], scheme["accent"], scheme["text"], scheme["card"])
        if not first_time:
            # Simple approach: restart UI colors recursively
            self._recolor_widgets(self.root)

    def _recolor_widgets(self, widget):
        # Recursively recolor text/background where sensible
        try:
            if isinstance(widget, (tk.Frame, tk.Label, tk.Button)):
                widget.configure(bg=self.bg_color if not isinstance(widget, tk.Frame) or widget in (self.card,) else self.card_bg,
                                  fg=self.text_color if isinstance(widget, (tk.Label, tk.Button)) else None)
                if widget in (self.card,):
                    widget.configure(bg=self.card_bg)
        except tk.TclError:
            pass
        for w in widget.winfo_children():
            self._recolor_widgets(w)

    # ------------------------------------------------------ SEARCH & FETCH
    def _clear_placeholder(self):
        if self.search_entry.get() == "Enter city name…":
            self.search_entry.delete(0, tk.END)

    def toggle_unit(self):
        self.temp_unit = "imperial" if self.temp_unit == "metric" else "metric"
        self.unit_btn.config(text="°F" if self.temp_unit == "imperial" else "°C")
        if self.current_city:
            self.get_weather_for_city(self.current_city)

    def get_current_location(self):
        self.status_lbl.config(text="Detecting location…")
        self.root.update_idletasks()
        try:
            res = requests.get("http://ip-api.com/json", timeout=5)
            loc = res.json()
            if loc.get("status") == "success":
                city = loc["city"]
                self.current_lat = loc["lat"]
                self.current_lon = loc["lon"]
                self.search_entry.delete(0, tk.END)
                self.search_entry.insert(0, city)
                self.get_weather_for_city(city)
            else:
                messagebox.showerror("Error", "Could not determine location")
        except Exception as e:
            messagebox.showerror("Error", f"Location error: {e}")
        finally:
            self.status_lbl.config(text="Ready")

    def get_weather(self):
        city = self.search_entry.get().strip()
        if not city or city == "Enter city name…":
            messagebox.showinfo("Input", "Please enter city name")
            return
        self.get_weather_for_city(city)

    def get_weather_for_city(self, city):
        self.status_lbl.config(text="Fetching weather…")
        self.root.update_idletasks()
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={self.temp_unit}"
            data = requests.get(url, timeout=8).json()
            if data.get("cod") != 200:
                raise ValueError(data.get("message", "City not found"))
            self.current_city = f"{data['name']}, {data['sys']['country']}"
            self.current_lat, self.current_lon = data['coord']['lat'], data['coord']['lon']
            self.update_current_ui(data)
            self.populate_forecast()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.status_lbl.config(text="Ready")

    def update_current_ui(self, data):
        self.lbl_city.config(text=self.current_city)
        local_time = datetime.utcfromtimestamp(data['dt'] + data['timezone'])
        self.lbl_time.config(text=local_time.strftime('%d %b %Y  %H:%M'))
        unit = "°F" if self.temp_unit == "imperial" else "°C"
        self.lbl_temp.config(text=f"{int(data['main']['temp'])}{unit}")
        desc = data['weather'][0]['description'].capitalize()
        self.lbl_desc.config(text=desc)
        icon_code = data['weather'][0]['icon'][:2]
        icons = {
            "01": "☀️", "02": "🌤️", "03": "☁️", "04": "☁️", "09": "🌧️",
            "10": "🌦️", "11": "⛈️", "13": "❄️", "50": "🌫️"
        }
        self.lbl_icon.config(text=icons.get(icon_code, "❓"))

    # --------------------------------------------------- FORECAST
    def populate_forecast(self):
        for w in self.frame_forecast.winfo_children():
            w.destroy()
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.current_lat}&lon={self.current_lon}&appid={API_KEY}&units={self.temp_unit}"
        data = requests.get(url).json()
        if data.get("cod") != "200":
            tk.Label(self.frame_forecast, text="Forecast unavailable", bg=self.bg_color).pack()
            return
        # pick noon forecasts per day
        seen = {}
        for item in data['list']:
            dt = datetime.fromtimestamp(item['dt'])
            day = dt.strftime('%Y-%m-%d')
            if dt.hour == 12 and day not in seen:
                seen[day] = item
        for day, item in list(seen.items())[:5]:
            self._add_forecast_day(item)

    def _add_forecast_day(self, item):
        frame = tk.Frame(self.frame_forecast, bg=self.card_bg, bd=1, relief=tk.GROOVE, padx=10, pady=6)
        frame.pack(fill=tk.X, padx=8, pady=4)
        dt = datetime.fromtimestamp(item['dt'])
        tk.Label(frame, text=dt.strftime('%a %d %b'), bg=self.card_bg, font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w")
        icon_code = item['weather'][0]['icon'][:2]
        icons = {
            "01": "☀️", "02": "🌤️", "03": "☁️", "04": "☁️", "09": "🌧️",
            "10": "🌦️", "11": "⛈️", "13": "❄️", "50": "🌫️"
        }
        tk.Label(frame, text=icons.get(icon_code, "❓"), bg=self.card_bg, font=("Arial Unicode MS", 24)).grid(row=0, column=1)
        unit = "°F" if self.temp_unit == "imperial" else "°C"
        tk.Label(frame, text=f"{int(item['main']['temp'])}{unit}", bg=self.card_bg, font=("Helvetica", 16, "bold")).grid(row=0, column=2)
        tk.Label(frame, text=item['weather'][0]['description'].capitalize(), bg=self.card_bg).grid(row=1, column=0, columnspan=3, sticky="w")

    # --------------------------------------------------- HISTORY
    def fetch_history(self):
        if not (self.current_lat and self.current_lon):
            messagebox.showinfo("History", "Load current weather first so I know where you are")
            return
        for w in self.frame_history.winfo_children():
            w.destroy()
        for i in range(1, 6):  # past 5 days
            dt = int((datetime.utcnow() - timedelta(days=i)).replace(hour=12, minute=0, second=0, microsecond=0).timestamp())
            url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={self.current_lat}&lon={self.current_lon}&dt={dt}&appid={API_KEY}&units={self.temp_unit}"
            data = requests.get(url).json()
            if "current" not in data:
                continue
            self._add_history_day(data['current'])
        if not self.frame_history.winfo_children():
            tk.Label(self.frame_history, text="History unavailable (API limit?)", bg=self.bg_color).pack()

    def _add_history_day(self, current):
        frame = tk.Frame(self.frame_history, bg=self.card_bg, bd=1, relief=tk.SOLID, padx=8, pady=4)
        frame.pack(fill=tk.X, padx=8, pady=4)
        dt = datetime.fromtimestamp(current['dt'])
        unit = "°F" if self.temp_unit == "imperial" else "°C"
        tk.Label(frame, text=dt.strftime('%a %d %b'), font=("Helvetica", 12, "bold"), bg=self.card_bg).grid(row=0, column=0, sticky="w")
        tk.Label(frame, text=f"Temp: {int(current['temp'])}{unit}", bg=self.card_bg).grid(row=1, column=0, sticky="w")
        tk.Label(frame, text=f"Weather: {current['weather'][0]['description'].capitalize()}", bg=self.card_bg).grid(row=1, column=1, sticky="w")

    # --------------------------------------------------- MAPS
    map_layer_codes = {
        "Temperature": "temp_new", "Clouds": "clouds_new", "Precipitation": "precipitation_new",
        "Wind": "wind_new", "Pressure": "pressure_new"
    }

    def load_weather_map(self):
        if not (self.current_lat and self.current_lon):
            messagebox.showinfo("Map", "Load current weather first")
            return
        self.lbl_map.config(text="Loading map…")
        layer_code = self.map_layer_codes[self.map_layer_var.get()]
        zoom = 5
        x, y = deg2num(self.current_lat, self.current_lon, zoom)
        url = f"https://tile.openweathermap.org/map/{layer_code}/{zoom}/{x}/{y}.png?appid={API_KEY}"
        try:
            img_data = requests.get(url, timeout=10).content
            img = Image.open(BytesIO(img_data)).resize((512, 512), Image.LANCZOS)
            self.tk_map = ImageTk.PhotoImage(img)
            self.lbl_map.config(image=self.tk_map, text="")
        except Exception as e:
            self.lbl_map.config(text=f"Error loading map: {e}")

    def open_weather_map(self):
        if not (self.current_lat and self.current_lon):
            messagebox.showinfo("Map", "Load current weather first")
            return
        layer_code = self.map_layer_codes[self.map_layer_var.get()]
        url = f"https://openweathermap.org/weathermap?basemap=map&cities=true&layer={layer_code}&lat={self.current_lat}&lon={self.current_lon}&zoom=5"
        webbrowser.open(url)

    # --------------------------------------------------- NOTIFICATIONS
    def toggle_notifications(self):
        self.notifications_enabled = self.notifications_var.get()
        if self.notifications_enabled:
            self.notif_lbl.config(text="🔔")
            self._stop_notification_event.clear()
            threading.Thread(target=self._notification_loop, daemon=True).start()
        else:
            self.notif_lbl.config(text="🔕")
            self._stop_notification_event.set()

    def _notification_loop(self):
        while not self._stop_notification_event.is_set():
            try:
                if self.current_lat and self.current_lon:
                    url = (f"https://api.openweathermap.org/data/2.5/weather?lat={self.current_lat}&lon={self.current_lon}&appid="
                           f"{API_KEY}&units={self.temp_unit}")
                    data = requests.get(url, timeout=10).json()
                    cond_id = data['weather'][0]['id']
                    severe = cond_id < 800 or cond_id >= 900  # thunderstorms, etc.
                    if severe:
                        desc = data['weather'][0]['description'].capitalize()
                        if desc != self.last_alert:
                            self.last_alert = desc
                            self.send_notification("Severe Weather Alert", desc)
                time.sleep(600)  # check every 10 minutes
            except Exception:
                time.sleep(600)

    def send_notification(self, title, message):
        if NOTIFIER_AVAILABLE:
            notification.notify(title=title, message=message, timeout=10)
        else:
            # fallback – a simple messagebox (blocking) – can be removed if undesired
            messagebox.showwarning(title, message)


if __name__ == "__main__":
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()
