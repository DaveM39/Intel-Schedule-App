import tkinter as tk
from tkinter import ttk
import requests
import json  # For potential JSON response handling

def get_airline_data(airline_code):
    """Placeholder for fetching airline data (replace with actual API call)."""
    # In a real app, replace this with an API call to an airline data source.
    # Example using a placeholder dict (replace with real data):
    airline_data = {
        "AA": {"name": "American Airlines", "rating": 4.0, "hub": "Dallas/Fort Worth"},
        "DL": {"name": "Delta Air Lines", "rating": 4.2, "hub": "Atlanta"},
        "UA": {"name": "United Airlines", "rating": 3.8, "hub": "Chicago"},
        "SW": {"name": "Southwest Airlines", "rating": 4.5, "hub": "Dallas Love Field"},
        "BR": {"name": "EVA Air", "rating": 4.3, "hub": "Taipei"},  # Added EVA Air
        "LH": {"name": "Lufthansa", "rating": 4.1, "hub": "Frankfurt"},  # Added Lufthansa
        "LY": {"name": "EL AL", "rating": 3.9, "hub": "Tel Aviv"},  # Added EL AL
        "KL": {"name": "KLM", "rating": 4.0, "hub": "Amsterdam"},  # Added KLM
        "CX": {"name": "Cathay Pacific", "rating": 4.4, "hub": "Hong Kong"}  # Added Cathay Pacific
    }
    return airline_data.get(airline_code, {"name": "Airline not found", "rating": "N/A", "hub": "N/A"})

def compare_airlines():
    """Compares airlines and displays the results."""
    airline_code1 = airline1_entry.get().upper()
    airline_code2 = airline2_entry.get().upper()

    data1 = get_airline_data(airline_code1)
    data2 = get_airline_data(airline_code2)

    result_text.delete(1.0, tk.END)  # Clear previous results

    result_text.insert(tk.END, f"Airline 1 ({airline_code1}):\n")
    result_text.insert(tk.END, f"  Name: {data1['name']}\n")
    result_text.insert(tk.END, f"  Rating: {data1['rating']}\n")
    result_text.insert(tk.END, f"  Hub: {data1['hub']}\n\n")

    result_text.insert(tk.END, f"Airline 2 ({airline_code2}):\n")
    result_text.insert(tk.END, f"  Name: {data2['name']}\n")
    result_text.insert(tk.END, f"  Rating: {data2['rating']}\n")
    result_text.insert(tk.END, f"  Hub: {data2['hub']}\n")

# GUI setup
window = tk.Tk()
window.title("Airline Comparison")

# Airline 1 input
airline1_label = tk.Label(window, text="Airline 1 (Code):")
airline1_label.grid(row=0, column=0, padx=5, pady=5)
airline1_entry = tk.Entry(window)
airline1_entry.grid(row=0, column=1, padx=5, pady=5)

# Airline 2 input
airline2_label = tk.Label(window, text="Airline 2 (Code):")
airline2_label.grid(row=1, column=0, padx=5, pady=5)
airline2_entry = tk.Entry(window)
airline2_entry.grid(row=1, column=1, padx=5, pady=5)

# Compare button
compare_button = tk.Button(window, text="Compare", command=compare_airlines)
compare_button.grid(row=2, column=0, columnspan=2, pady=10)

# Result display
result_text = tk.Text(window, height=10, width=40)
result_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

window.mainloop()