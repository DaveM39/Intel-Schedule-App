import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def get_airline_data(airline_code):
    """Placeholder for fetching airline data (replace with actual API call)."""
    airline_data = {
        "AA": {"name": "American Airlines", "rating": 4.0, "hub": "Dallas/Fort Worth", "website": "aa.com", "fleet": 900},
        "DL": {"name": "Delta Air Lines", "rating": 4.2, "hub": "Atlanta", "website": "delta.com", "fleet": 800},
        "UA": {"name": "United Airlines", "rating": 3.8, "hub": "Chicago", "website": "united.com", "fleet": 850},
        "SW": {"name": "Southwest Airlines", "rating": 4.5, "hub": "Dallas Love Field", "website": "southwest.com", "fleet": 750},
        "BR": {"name": "EVA Air", "rating": 4.3, "hub": "Taipei", "website": "evaair.com", "fleet": 80},
        "LH": {"name": "Lufthansa", "rating": 4.1, "hub": "Frankfurt", "website": "lufthansa.com", "fleet": 280},
        "LY": {"name": "EL AL", "rating": 3.9, "hub": "Tel Aviv", "website": "elal.com", "fleet": 45},
        "KL": {"name": "KLM", "rating": 4.0, "hub": "Amsterdam", "website": "klm.com", "fleet": 120},
        "CX": {"name": "Cathay Pacific", "rating": 4.4, "hub": "Hong Kong", "website": "cathaypacific.com", "fleet": 180},
        "EK": {"name": "Emirates", "rating": 4.6, "hub": "Dubai", "website": "emirates.com", "fleet": 260},
        "QR": {"name": "Qatar Airways", "rating": 4.7, "hub": "Doha", "website": "qatarairways.com", "fleet": 200},
        "SQ": {"name": "Singapore Airlines", "rating": 4.8, "hub": "Singapore", "website": "singaporeair.com", "fleet": 140}
    }
    return airline_data.get(airline_code, {"name": "Airline not found", "rating": "N/A", "hub": "N/A", "website": "N/A", "fleet": "N/A"})

def compare_airlines():
    airline_codes = [entry.get().upper() for entry in airline_entries if entry.get()]
    if not airline_codes:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Please enter at least one airline code.")
        return

    airline_data_list = [get_airline_data(code) for code in airline_codes]

    result_text.delete(1.0, tk.END)
    ratings = []
    labels = []

    for i, data in enumerate(airline_data_list):
        result_text.insert(tk.END, f"Airline {i + 1} ({airline_codes[i]}):\n")
        result_text.insert(tk.END, f"  Name: {data['name']}\n")
        result_text.insert(tk.END, f"  Rating: {data['rating']}\n")
        result_text.insert(tk.END, f"  Hub: {data['hub']}\n")
        result_text.insert(tk.END, f"  Website: {data['website']}\n")
        result_text.insert(tk.END, f"  Fleet Size: {data['fleet']}\n\n")
        ratings.append(data['rating'])
        labels.append(airline_codes[i])

    # Bar chart
    fig = plt.Figure(figsize=(8, len(labels) * 0.7), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(labels, ratings)
    ax.set_ylabel('Rating')
    ax.set_title('Airline Ratings Comparison')
    fig.autofmt_xdate(rotation=45, ha='right')

    canvas = FigureCanvasTkAgg(fig, master=result_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side="bottom", fill="x", expand=True)

# GUI setup
window = tk.Tk()
window.title("Airline Comparison")

style = ttk.Style()
style.configure('TButton', padding=10, font=('Arial', 12))
style.configure('TLabel', padding=10, font=('Arial', 12))
style.configure('TEntry', padding=10, font=('Arial', 12))

# Frame for input
input_frame = ttk.Frame(window)
input_frame.pack(pady=10, fill="x")

airline_entries = []
for i in range(5):
    airline_label = ttk.Label(input_frame, text=f"Airline {i + 1} (Code):")
    airline_label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
    airline_entry = ttk.Entry(input_frame)
    airline_entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
    airline_entries.append(airline_entry)

compare_button = ttk.Button(input_frame, text="Compare", command=compare_airlines)
compare_button.grid(row=5, column=0, columnspan=2, pady=10)

# Result display frame
result_frame = ttk.Frame(window)
result_frame.pack(pady=10, fill="both", expand=True)

# Result display text area
result_text = tk.Text(result_frame, height=15, width=60)
result_text.pack(side="top", fill="x", expand=True)

window.columnconfigure(0, weight=1)
input_frame.columnconfigure(1, weight=1)

window.mainloop()