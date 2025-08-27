import tkinter as tk
from tkinter import font
import requests
from PIL import Image, ImageTk
from io import BytesIO
import os

# --- Configuration ---
API_KEY = "9d28222a8f9d1633f4b8b81e61f290ae"
SAVE_FILE = 'last_city.txt'


# --- Functions ---

def get_weather():
    """Fetches weather data from the API and updates the GUI."""
    city = city_entry.get()
    if not city:
        return

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        weather_data = response.json()

        # Update GUI with new data
        update_display(weather_data)
        save_last_city(city)

    except requests.exceptions.HTTPError:
        display_error("City not found.")
    except requests.exceptions.RequestException:
        display_error("Network error. Check connection.")


def update_display(data):
    """Updates all the labels with the fetched weather data."""
    # Location and Description
    location = f"{data['name']}, {data['sys']['country']}"
    description = data['weather'][0]['description'].title()
    location_label.config(text=location)
    desc_label.config(text=description)

    # Temperature
    temp = f"{data['main']['temp']:.1f}°C"  # Formatted to one decimal place
    temp_label.config(text=temp)

    # Details (Humidity and Wind)
    humidity = f"Humidity: {data['main']['humidity']}%"
    wind = f"Wind: {data['wind']['speed']:.1f} m/s"
    details_label.config(text=f"{humidity}\n{wind}")

    # Weather Icon
    icon_code = data['weather'][0]['icon']
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

    # Download the icon image
    image_response = requests.get(icon_url)
    img_data = image_response.content

    # Open the image with Pillow and create a Tkinter-compatible PhotoImage
    pil_image = Image.open(BytesIO(img_data))
    photo_image = ImageTk.PhotoImage(pil_image)

    # Update the icon label
    icon_label.config(image=photo_image)
    # IMPORTANT: Keep a reference to the image to prevent it from being garbage collected
    icon_label.image = photo_image


def display_error(message):
    """Displays an error message in the GUI."""
    location_label.config(text=message)
    desc_label.config(text="")
    temp_label.config(text="")
    details_label.config(text="")
    icon_label.config(image='')  # Clear the icon


def save_last_city(city):
    """Saves the last successfully searched city to a file."""
    with open(SAVE_FILE, 'w') as f:
        f.write(city)


def load_last_city():
    """Loads the last city from the file and fetches its weather."""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            city = f.read().strip()
            if city:
                city_entry.insert(0, city)
                get_weather()


# --- GUI Setup ---
# Main window
root = tk.Tk()
root.title("Cooler Weather App")
root.geometry("450x450")
root.resizable(False, False)  # Make window not resizable

# Fonts
default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="Helvetica", size=11)
title_font = font.Font(family="Helvetica", size=18, weight="bold")
temp_font = font.Font(family="Helvetica", size=48, weight="bold")
desc_font = font.Font(family="Helvetica", size=14)

# --- Frames for layout ---
# Top frame for input field and button
top_frame = tk.Frame(root, pady=10)
top_frame.pack(fill="x", padx=10)

# Main weather info frame (icon, temp, etc.)
weather_frame = tk.Frame(root)
weather_frame.pack(pady=20)

# Details frame (humidity, wind)
details_frame = tk.Frame(root)
details_frame.pack(pady=10)

# --- Widgets ---
# Top Frame Widgets
city_entry = tk.Entry(top_frame, width=30, font=default_font)
city_entry.pack(side="left", ipady=4, expand=True, fill="x")  # ipady for internal padding

get_weather_button = tk.Button(top_frame, text="Get Weather", command=get_weather, font=default_font)
get_weather_button.pack(side="left", padx=5)

# Weather Frame Widgets
location_label = tk.Label(weather_frame, font=title_font)
location_label.pack()

icon_label = tk.Label(weather_frame)
icon_label.pack(pady=5)

temp_label = tk.Label(weather_frame, font=temp_font)
temp_label.pack()

desc_label = tk.Label(weather_frame, font=desc_font)
desc_label.pack()

# Details Frame Widgets
details_label = tk.Label(details_frame, font=default_font, justify="left")
details_label.pack()

# --- Initial Load ---
# Load the last city when the app starts
root.after(100, load_last_city)  # Use .after to run after the main loop has started

# Start the main event loop
root.mainloop()