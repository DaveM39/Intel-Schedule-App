import os
from io import BytesIO
import requests
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from tkinter import font

# --- הגדרות ---
API_KEY = "9d28222a8f9d1633f4b8b81e61f290ae"
SAVE_FILE = 'last_city.txt'

# --- תרגומים נפוצים של תיאורי מזג אוויר ---
WEATHER_TRANSLATIONS = {
    "clear sky": "שמיים בהירים",
    "few clouds": "מעונן חלקית",
    "scattered clouds": "עננות פזורה",
    "broken clouds": "עננות חלקית",
    "overcast clouds": "מעונן",
    "shower rain": "גשם קל",
    "rain": "גשם",
    "light rain": "גשם קל",
    "moderate rain": "גשם בינוני",
    "heavy intensity rain": "גשם כבד",
    "thunderstorm": "סופת רעמים",
    "snow": "שלג",
    "mist": "ערפל",
    "smoke": "עשן",
    "haze": "אובך",
    "dust": "אבק",
    "fog": "ערפל",
}


# --- פונקציות ---

def get_weather(event=None):
    """מביאה את נתוני מזג האוויר מה-API ומעדכנת את הממשק."""
    city = city_entry.get()
    if not city:
        return

    show_loading_state()

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={API_KEY}&units=metric&lang=he"

    try:
        response = requests.get(complete_url, timeout=5)
        response.raise_for_status()
        weather_data = response.json()
        update_display(weather_data)
        save_last_city(city)
    except requests.exceptions.HTTPError:
        display_error("העיר לא נמצאה")
    except requests.exceptions.RequestException:
        display_error("שגיאת רשת")
    finally:
        get_weather_button.config(state="enabled")


def show_loading_state():
    """מציגה הודעת טעינה ונועלת את כפתור החיפוש."""
    location_label.config(text="...טוען")
    temp_label.config(text="")
    desc_label.config(text="")
    details_label.config(text="")
    icon_label.config(image='')
    get_weather_button.config(state="disabled")


def update_display(data):
    """מעדכנת את כל התוויות עם המידע שהתקבל."""
    location = f"{data['name']}, {data['sys']['country']}"

    # תרגום תיאור מזג האוויר
    english_desc = data['weather'][0]['description']
    hebrew_desc = WEATHER_TRANSLATIONS.get(english_desc.lower(), english_desc.title())

    temp = f"{data['main']['temp']:.1f}°C"
    humidity = f"לחות: {data['main']['humidity']}%"
    wind = f"רוח: {data['wind']['speed']:.1f} מ'/ש'"

    location_label.config(text=location)
    desc_label.config(text=hebrew_desc)
    temp_label.config(text=temp)
    details_label.config(text=f"{humidity}\n{wind}")

    icon_code = data['weather'][0]['icon']
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@4x.png"

    try:
        image_response = requests.get(icon_url, timeout=5)
        image_response.raise_for_status()
        img_data = image_response.content
        pil_image = Image.open(BytesIO(img_data))
        photo_image = ImageTk.PhotoImage(pil_image)
        icon_label.config(image=photo_image)
        icon_label.image = photo_image
    except requests.exceptions.RequestException:
        icon_label.config(image='')


def display_error(message):
    """מציגה הודעת שגיאה בממשק."""
    location_label.config(text=message)
    temp_label.config(text="")
    desc_label.config(text="")
    details_label.config(text="")
    icon_label.config(image='')


def save_last_city(city):
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        f.write(city)


def load_last_city():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            city = f.read().strip()
            if city:
                city_entry.insert(0, city)
                get_weather()


# --- הגדרת הממשק הגרפי (GUI) ---
# שימוש בערכת העיצוב "vapor" של ttkbootstrap
root = ttk.Window(themename="vapor")
root.title("אפליקציית מזג אוויר")
root.geometry("500x550")
root.resizable(False, False)

# הגדרת פונטים
title_font = font.Font(family="Arial", size=24, weight="bold")
temp_font = font.Font(family="Arial", size=56, weight="bold")
desc_font = font.Font(family="Arial", size=16)
details_font = font.Font(family="Arial", size=12)

# מסגרת ראשית עם ריווח פנימי
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill=BOTH)

# --- אזור עליון: קלט וכפתור ---
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill=X, pady=(0, 20))

# שינוי סדר וכיוון עבור RTL
get_weather_button = ttk.Button(input_frame, text="חפש", command=get_weather, bootstyle="success")
get_weather_button.pack(side=LEFT, padx=(10, 0), ipady=5)

city_entry = ttk.Entry(input_frame, font=desc_font, justify=RIGHT)
city_entry.insert(0, "הקלד עיר...")  # Placeholder
city_entry.pack(side=LEFT, expand=True, fill=X, ipady=5)
# אירועים למחיקת ה-placeholder בלחיצה וכריכת מקש Enter
city_entry.bind("<FocusIn>", lambda e: city_entry.delete('0', 'end'))
city_entry.bind("<Return>", get_weather)

# --- אזור אמצעי: מידע ראשי ---
weather_info_frame = ttk.Frame(main_frame)
weather_info_frame.pack(expand=True)

location_label = ttk.Label(weather_info_frame, font=title_font)
location_label.pack(pady=(0, 10))

# מסגרת פנימית לאייקון ולטמפרטורה
icon_temp_frame = ttk.Frame(weather_info_frame)
icon_temp_frame.pack()

temp_label = ttk.Label(icon_temp_frame, font=temp_font)
temp_label.pack(side=RIGHT, padx=(20, 0))

icon_label = ttk.Label(icon_temp_frame)
icon_label.pack(side=RIGHT)

# --- אזור תחתון: תיאור ופרטים נוספים ---
desc_label = ttk.Label(main_frame, font=desc_font)
desc_label.pack(pady=(15, 5))

details_label = ttk.Label(main_frame, font=details_font, justify=RIGHT)
details_label.pack(pady=5)

# --- טעינה ראשונית ---
root.after(200, load_last_city)

root.mainloop()