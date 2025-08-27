import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import webbrowser


class CountryCitiesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("City Explorer")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Sample database of countries and cities with additional information
        self.countries_cities = {
            "USA": {
                "Washington D.C.": {"population": "670,000", "area": "177.0 km²",
                                    "description": "USA Capital, Federal district, historical landmarks"},
                "New York": {"population": "8.8 million", "area": "783.8 km²",
                             "description": "Largest city in the USA, global financial center"},
                "Los Angeles": {"population": "3.9 million", "area": "1,302 km²",
                                "description": "Entertainment capital, home to Hollywood"},
                "Chicago": {"population": "2.7 million", "area": "606.1 km²",
                            "description": "Known for architecture, blues music"},
                "Houston": {"population": "2.3 million", "area": "1,651 km²",
                            "description": "Space Center, energy industry hub"},
                "Phoenix": {"population": "1.6 million", "area": "1,344 km²",
                            "description": "Desert metropolis with year-round sunshine"},
                "Philadelphia": {"population": "1.6 million", "area": "369.6 km²",
                                 "description": "Historic city, home of Liberty Bell"}
            },
            "Canada": {
                "Toronto": {"population": "2.9 million", "area": "630.2 km²",
                            "description": "Canada's largest city, CN Tower"},
                "Montreal": {"population": "1.8 million", "area": "431.5 km²",
                             "description": "French-speaking cultural hub"},
                "Vancouver": {"population": "675,000", "area": "115.2 km²",
                              "description": "Surrounded by mountains and water"},
                "Calgary": {"population": "1.3 million", "area": "825.3 km²",
                            "description": "Gateway to the Rocky Mountains"},
                "Ottawa": {"population": "994,000", "area": "2,790 km²", "description": "Canada's capital city"},
                "Edmonton": {"population": "981,000", "area": "684.4 km²",
                             "description": "Festival City, home to West Edmonton Mall"}
            },
            "UK": {
                "London": {"population": "9.0 million", "area": "1,572 km²",
                           "description": "Capital city, Westminster, Big Ben"},
                "Manchester": {"population": "547,000", "area": "115.6 km²",
                               "description": "Industrial city, famous for football"},
                "Birmingham": {"population": "1.1 million", "area": "267.8 km²",
                               "description": "UK's second-largest city"},
                "Glasgow": {"population": "633,000", "area": "175.5 km²", "description": "Scotland's largest city"},
                "Liverpool": {"population": "498,000", "area": "111.8 km²", "description": "Birthplace of The Beatles"},
                "Edinburgh": {"population": "524,000", "area": "264 km²",
                              "description": "Scotland's capital, Edinburgh Castle"}
            },
            "France": {
                "Paris": {"population": "2.1 million", "area": "105.4 km²",
                          "description": "City of Light, Eiffel Tower"},
                "Marseille": {"population": "870,000", "area": "240.6 km²", "description": "Major Mediterranean port"},
                "Lyon": {"population": "516,000", "area": "47.9 km²", "description": "Culinary capital of France"},
                "Toulouse": {"population": "479,000", "area": "118.3 km²",
                             "description": "Pink City, aerospace center"},
                "Nice": {"population": "342,000", "area": "71.9 km²",
                         "description": "Azure coast, tourism destination"},
                "Nantes": {"population": "309,000", "area": "65.2 km²",
                           "description": "Historic port city on the Loire"}
            },
            "Japan": {
                "Tokyo": {"population": "13.9 million", "area": "2,194 km²",
                          "description": "World's largest urban economy"},
                "Osaka": {"population": "2.7 million", "area": "225.2 km²",
                          "description": "Japan's kitchen, vibrant food culture"},
                "Kyoto": {"population": "1.5 million", "area": "827.8 km²",
                          "description": "Historic temples, traditional culture"},
                "Yokohama": {"population": "3.7 million", "area": "437.6 km²", "description": "Major port city"},
                "Sapporo": {"population": "1.9 million", "area": "1,121 km²",
                            "description": "Known for snow festival, beer"},
                "Nagoya": {"population": "2.3 million", "area": "326.4 km²",
                           "description": "Manufacturing hub, automotive industry"}
            },
            "Australia": {
                "Sydney": {"population": "5.3 million", "area": "12,368 km²",
                           "description": "Harbor city, Opera House"},
                "Melbourne": {"population": "5.0 million", "area": "9,992 km²",
                              "description": "Cultural capital, sporting events"},
                "Brisbane": {"population": "2.4 million", "area": "15,826 km²",
                             "description": "River city, subtropical climate"},
                "Perth": {"population": "2.1 million", "area": "6,418 km²",
                          "description": "Isolated city, beautiful beaches"},
                "Adelaide": {"population": "1.3 million", "area": "3,258 km²",
                             "description": "City of churches, wine regions"},
                "Gold Coast": {"population": "710,000", "area": "1,334 km²",
                               "description": "Tourism destination, surf beaches"}
            },
            "Israel": {
                "Jerusalem": {"population": "936,000", "area": "125.1 km²",
                              "description": "Holy city, religious importance"},
                "Tel Aviv": {"population": "460,000", "area": "52 km²",
                             "description": "Mediterranean coastline, Tourism destination, tech hub"},
                "Haifa": {"population": "285,000", "area": "63.7 km²", "description": "Port city, Mount Carmel"},
                "Rishon LeZion": {"population": "251,000", "area": "58.7 km²",
                                  "description": "Fourth-largest city in Israel"},
                "Petah Tikva": {"population": "248,000", "area": "35.9 km²",
                                "description": "Founded in 1878, industrial center"},
                "Beersheba": {"population": "209,000", "area": "117.5 km²",
                              "description": "Capital of the Negev desert"},
                "Ashdod": {"population": "225,000", "area": "47.2 km²",
                           "description": "Major port city, diverse population"},
                "Ashkelon": {"population": "145,000", "area": "47.8 km²",
                             "description": "Coastal city, ancient history"},
                "Eilat": {"population": "55,000", "area" : "84.79 km²",
                          "description": "Resort city, Red sea beaches, Israel's southernmost city" }
            },
            "Taiwan": {
                "Taipei": {"population": "2.6 million", "area": "271.8 km²",
                           "description": "Capital city, Taipei 101 skyscraper"},
                "Kaohsiung": {"population": "2.7 million", "area": "2,952 km²",
                              "description": "Harbor city, industrial center"},
                "Taichung": {"population": "2.8 million", "area": "2,215 km²",
                             "description": "Cultural city, mild climate"},
                "Tainan": {"population": "1.9 million", "area": "2,192 km²",
                           "description": "Ancient capital, historic sites"},
                "Hsinchu": {"population": "443,000", "area": "104.1 km²", "description": "Silicon Valley of Taiwan"},
                "Keelung": {"population": "371,000", "area": "132.8 km²", "description": "Northern port city"}
            },
            "Czech Republic": {
                "Prague": {"population": "1.3 million", "area": "496 km²",
                           "description": "Capital city, historic architecture"},
                "Brno": {"population": "380,000", "area": "230.2 km²",
                         "description": "Second-largest city, university center"},
                "Ostrava": {"population": "290,000", "area": "214.2 km²",
                            "description": "Industrial city, coal mining history"},
                "Pilsen": {"population": "174,000", "area": "137.7 km²", "description": "Birthplace of Pilsner beer"},
                "Liberec": {"population": "104,000", "area": "106.1 km²",
                            "description": "Northern city, winter sports"},
                "Olomouc": {"population": "100,000", "area": "103.4 km²", "description": "Historic university city"},
                "Karlovy Vary": {"population": "48,000", "area": "59.1 km²",
                                 "description": "Spa town, famous hot springs"}
            }
        }

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Create a style
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 11))
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # App title
        title_label = ttk.Label(main_frame, text="City Explorer", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Left panel - controls
        left_panel = ttk.Frame(main_frame, padding="10")
        left_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        ttk.Label(left_panel, text="Select Country:", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))

        # Country selection dropdown
        self.country_var = tk.StringVar()
        country_dropdown = ttk.Combobox(left_panel, textvariable=self.country_var,
                                        values=sorted(list(self.countries_cities.keys())),
                                        state="readonly", width=30)
        country_dropdown.pack(fill=tk.X, pady=5)
        country_dropdown.bind("<<ComboboxSelected>>", self.display_cities)

        # Or enter a custom country
        ttk.Label(left_panel, text="OR Enter Country:", style="Header.TLabel").pack(anchor=tk.W, pady=(15, 5))
        self.custom_country = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.custom_country, width=30).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Find", command=self.find_custom).pack(anchor=tk.W, pady=5)

        # Sorting options
        ttk.Label(left_panel, text="Sort Cities By:", style="Header.TLabel").pack(anchor=tk.W, pady=(15, 5))
        self.sort_var = tk.StringVar(value="name")
        sort_options = [
            ("Name (A-Z)", "name"),
            ("Name (Z-A)", "name_desc"),
            ("Population (High-Low)", "population_desc"),
            ("Population (Low-High)", "population"),
            ("Area (Large-Small)", "area_desc"),
            ("Area (Small-Large)", "area")
        ]

        for text, value in sort_options:
            ttk.Radiobutton(left_panel, text=text, value=value, variable=self.sort_var,
                            command=self.resort_cities).pack(anchor=tk.W, pady=2)

        # Add city section
        ttk.Label(left_panel, text="Add New City:", style="Header.TLabel").pack(anchor=tk.W, pady=(15, 5))

        add_frame = ttk.Frame(left_panel)
        add_frame.pack(fill=tk.X, pady=5)

        ttk.Label(add_frame, text="City Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.new_city = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_city).grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(add_frame, text="Population:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.new_population = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_population).grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(add_frame, text="Area (km²):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.new_area = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_area).grid(row=2, column=1, sticky=tk.W, pady=2)

        ttk.Label(add_frame, text="Description:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.new_description = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_description).grid(row=3, column=1, sticky=tk.W, pady=2)

        ttk.Button(left_panel, text="Add City", command=self.add_city).pack(anchor=tk.W, pady=5)

        # Right panel - city list and details
        right_panel = ttk.Frame(main_frame, padding="10")
        right_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # City list
        ttk.Label(right_panel, text="Cities:", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        city_frame = ttk.Frame(right_panel)
        city_frame.pack(fill=tk.BOTH, expand=True)

        self.city_listbox = tk.Listbox(city_frame, font=("Arial", 11), height=10)
        self.city_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(city_frame, orient="vertical", command=self.city_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.city_listbox.config(yscrollcommand=scrollbar.set)

        self.city_listbox.bind('<<ListboxSelect>>', self.display_city_details)

        # City details
        ttk.Label(right_panel, text="City Details:", style="Header.TLabel").pack(anchor=tk.W, pady=(15, 5))

        self.details_text = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD, width=40, height=10,
                                                      font=("Arial", 11))
        self.details_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.details_text.config(state=tk.DISABLED)

        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(1, weight=1)

    def display_cities(self, event=None):
        country = self.country_var.get()
        self.custom_country.set("")
        self.show_cities(country)

    def find_custom(self):
        country = self.custom_country.get().strip()
        if not country:
            messagebox.showwarning("Input Error", "Please enter a country name.")
            return

        self.country_var.set("")
        self.show_cities(country)

    def show_cities(self, country):
        self.city_listbox.delete(0, tk.END)

        if country in self.countries_cities:
            cities = self.get_sorted_cities(country)
            for city in cities:
                self.city_listbox.insert(tk.END, city)
        else:
            self.city_listbox.insert(tk.END, f"No data for {country}")
            # Create entry for new country
            self.countries_cities[country] = {}

        # Clear details
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state=tk.DISABLED)

    def get_sorted_cities(self, country):
        if country not in self.countries_cities:
            return []

        cities = list(self.countries_cities[country].keys())
        sort_method = self.sort_var.get()

        if sort_method == "name":
            return sorted(cities)
        elif sort_method == "name_desc":
            return sorted(cities, reverse=True)
        elif sort_method.startswith("population"):
            # Extract numeric value from population string
            def get_population(city):
                pop_str = self.countries_cities[country][city]["population"]
                return float(pop_str.split()[0].replace(',', ''))

            return sorted(cities, key=get_population, reverse=sort_method.endswith("_desc"))
        elif sort_method.startswith("area"):
            # Extract numeric value from area string
            def get_area(city):
                area_str = self.countries_cities[country][city]["area"]
                return float(area_str.split()[0].replace(',', ''))

            return sorted(cities, key=get_area, reverse=sort_method.endswith("_desc"))

        return cities

    def resort_cities(self):
        # Re-sort the currently displayed cities
        if self.country_var.get():
            self.show_cities(self.country_var.get())
        elif self.custom_country.get().strip():
            self.show_cities(self.custom_country.get().strip())

    def display_city_details(self, event):
        selection = self.city_listbox.curselection()
        if not selection:
            return

        city = self.city_listbox.get(selection[0])
        country = self.country_var.get() or self.custom_country.get().strip()

        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)

        if city.startswith("No data for"):
            self.details_text.insert(tk.END,
                                     f"No information available for this country.\n\nYou can add cities using the form on the left.")
        elif country in self.countries_cities and city in self.countries_cities[country]:
            city_info = self.countries_cities[country][city]

            self.details_text.insert(tk.END, f"City: {city}\n", "title")
            self.details_text.insert(tk.END, f"Country: {country}\n\n")

            self.details_text.insert(tk.END, f"Population: {city_info.get('population', 'N/A')}\n")
            self.details_text.insert(tk.END, f"Area: {city_info.get('area', 'N/A')}\n\n")

            self.details_text.insert(tk.END,
                                     f"Description:\n{city_info.get('description', 'No description available.')}\n")

            # Add fake map link
            self.details_text.insert(tk.END, "\n\nView on Map", "link")

            # Configure tags
            self.details_text.tag_config("title", font=("Arial", 12, "bold"))
            self.details_text.tag_config("link", foreground="blue", underline=1)
            self.details_text.tag_bind("link", "<Button-1>", lambda e: messagebox.showinfo("Map View",
                                                                                           f"This would open a map of {city}, {country}"))
        else:
            self.details_text.insert(tk.END, "No detailed information available for this city.")

        self.details_text.config(state=tk.DISABLED)

    def add_city(self):
        city = self.new_city.get().strip()
        country = self.country_var.get() or self.custom_country.get().strip()
        population = self.new_population.get().strip()
        area = self.new_area.get().strip()
        description = self.new_description.get().strip()

        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        if not country:
            messagebox.showwarning("Input Error", "Please select or enter a country first.")
            return

        if country not in self.countries_cities:
            self.countries_cities[country] = {}

        # Add default values if not provided
        if not population:
            population = "Unknown"
        if not area:
            area = "Unknown"
        if not description:
            description = "No description available."

        # Add km² to area if it's just a number
        if area.isdigit():
            area += " km²"

        if city not in self.countries_cities[country]:
            self.countries_cities[country][city] = {
                "population": population,
                "area": area,
                "description": description
            }

            # Clear input fields
            self.new_city.set("")
            self.new_population.set("")
            self.new_area.set("")
            self.new_description.set("")

            # Refresh display
            self.show_cities(country)
            messagebox.showinfo("Success", f"{city} added to {country}")
        else:
            messagebox.showinfo("Info", f"{city} already exists in {country}")


def main():
    root = tk.Tk()
    app = CountryCitiesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()