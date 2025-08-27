import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import textwrap

# (Keep the expanded tool_recommendations dictionary from the previous version)
tool_recommendations = {
    "Essentials - Driving & Fastening": [
        {"name": "Claw Hammer (approx. 16 oz)", "desc": "General purpose hammer for driving and pulling nails. Look for a comfortable grip."},
        {"name": "Screwdriver Set (Phillips & Flathead)", "desc": "A set with various sizes of both Phillips-head (+) and flat-head (-) tips is crucial. Magnetic tips can be helpful. A multi-bit screwdriver is a good space-saving alternative."},
        {"name": "Allen Wrench Set (Hex Keys)", "desc": "L-shaped keys for screws with hexagonal sockets, common in furniture assembly. Get both metric (mm) and standard (SAE/inch) sizes."},
        {"name": "Staple Gun (Manual)", "desc": "Useful for light upholstery, fastening fabric, or securing thin materials to wood."}
    ],
    "Essentials - Gripping & Adjusting": [
        {"name": "Pliers Set", "desc": "Should include: Slip-joint pliers (general use), Needle-nose pliers (small items/tight spaces), and Tongue-and-groove pliers (channel locks, good for plumbing/larger nuts)."},
        {"name": "Adjustable Wrench (Set of 2)", "desc": "One or two (e.g., 6-inch and 10-inch) can fit various sizes of nuts and bolts. Good for versatility."},
        {"name": "Locking Pliers (Vise-Grips)", "desc": "Clamp onto objects securely, freeing up your hands. Excellent for gripping stripped bolt heads or holding items for work."},
        {"name": "Wire Cutters / Diagonal Cutters", "desc": "Specifically designed for cutting copper wires and small fasteners cleanly."}
    ],
    "Essentials - Cutting & Measuring": [
        {"name": "Utility Knife", "desc": "A retractable blade knife for safely opening boxes, cutting cardboard, carpet, drywall scoring, etc. Keep spare blades."},
        {"name": "Tape Measure", "desc": "A 25-foot (~7.5m) retractable, locking tape measure is standard. Ensure it's easy to read."},
        {"name": "Level", "desc": "A small 'torpedo' level (~9in/23cm) for pictures/shelves. A longer level (2-4ft / 60-120cm) is better for larger projects like installing cabinets."},
        {"name": "Hacksaw", "desc": "Fine-toothed saw primarily for cutting metal (pipes, bolts, brackets) and plastic conduit."},
        {"name": "Combination Square", "desc": "Versatile tool for marking 90° and 45° angles, checking squareness, measuring depths, and as a straight edge."}
    ],
    "Safety & Utility": [
        {"name": "Flashlight / Headlamp", "desc": "Essential for dark spaces (under sinks, attics). An LED headlamp provides hands-free light."},
        {"name": "Safety Glasses / Goggles", "desc": "Crucial eye protection when hammering, cutting, drilling, using power tools, or working with chemicals."},
        {"name": "Work Gloves", "desc": "Protect hands from splinters, cuts, chemicals, and general dirt. Have a few types (general purpose, heavy-duty)."},
        {"name": "Dust Masks / Respirator", "desc": "Important for protecting lungs when sanding, sawing, or working in dusty environments. N95 masks are a common standard."},
        {"name": "Step Stool / Ladder", "desc": "Safely reach high places for tasks like changing lightbulbs, painting, or accessing storage."}
    ],
    "Plumbing & Electrical Basics": [
         {"name": "Plunger (Cup & Flange)", "desc": "Essential household item. Use a flange plunger for toilets and a cup plunger for sinks/drains."},
         {"name": "Pipe Wrench", "desc": "Heavy-duty wrench specifically designed for gripping round pipes. Useful for plumbing work."},
         {"name": "Caulking Gun", "desc": "Applies caulk or sealant from a tube to seal gaps around windows, doors, tubs, etc."},
         {"name": "Non-Contact Voltage Tester", "desc": "Safely checks for live electricity in outlets, switches, cords, and wires without direct contact. Essential electrical safety tool."},
         {"name": "Wire Stripper/Cutter Tool", "desc": "Combines wire cutting with specific notches for stripping insulation from various wire gauges."}
    ],
     "Good Additions (Hand Tools)": [
         {"name": "Socket Set (Ratchet & Sockets)", "desc": "Efficiently tighten/loosen nuts and bolts. Get a set with 1/4\" and 3/8\" drives, including Metric & SAE sockets."},
         {"name": "Combination Wrench Set", "desc": "Provides better grip than adjustable wrenches. Set should include common Metric & SAE sizes."},
         {"name": "Pry Bar / Crowbar", "desc": "For leveraging, prying apart boards, heavy-duty scraping, and removing embedded nails."},
         {"name": "Putty Knife (Flexible & Stiff)", "desc": "Flexible type for applying spackle/wood filler; stiff type for scraping paint or adhesive."},
         {"name": "Sandpaper Assortment", "desc": "Various grits (e.g., 80, 120, 220) for smoothing wood or preparing surfaces for finishing."},
         {"name": "Chalk Line", "desc": "For snapping long, straight lines on surfaces, useful for construction, flooring, or painting projects."}
    ],
    "Good Additions (Power Tools)": [
         {"name": "Cordless Drill/Driver", "desc": "Arguably the most useful power tool. Drills holes and drives screws. 18V or 20V models offer good power."},
         {"name": "Circular Saw", "desc": "For making fast, straight cuts in wood (dimensional lumber, plywood). Corded or cordless options available."},
         {"name": "Jigsaw", "desc": "Excellent for cutting curves, circles, and intricate shapes in wood, plastic, or thin metal."},
         {"name": "Orbital Sander", "desc": "For smooth finishing of wood surfaces quickly and easily before painting or staining."},
         {"name": "Oscillating Multi-Tool", "desc": "Extremely versatile for plunge cuts, sanding, scraping, grout removal, etc., especially in tight spots. Blades are interchangeable."},
         {"name": "Shop Vacuum (Wet/Dry Vac)", "desc": "Powerful vacuum for cleaning up workshop messes, sawdust, water spills, and general heavy-duty cleaning."}
    ],
     "Outdoor & Garden Basics": [
        {"name": "Shovel (Round or Square Point)", "desc": "Round point for digging; square point for scooping/moving loose materials like mulch or gravel."},
        {"name": "Garden Rake / Leaf Rake", "desc": "Metal garden rake for soil/gravel; flexible leaf rake for leaves and light debris."},
        {"name": "Hand Pruners / Shears", "desc": "For trimming small branches, deadheading flowers, and general garden plant maintenance."},
        {"name": "Garden Hose & Nozzle", "desc": "Essential for watering plants, cleaning outdoor surfaces, etc."},
        {"name": "Wheelbarrow or Garden Cart", "desc": "For moving soil, mulch, yard waste, tools, or heavy items around the yard."}
    ]
}

# --- GUI Application Class ---

class ToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Tool Recommendations")
        self.root.geometry("900x650") # Slightly larger again

        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        # Try to pick a theme
        if 'clam' in available_themes: self.style.theme_use('clam')
        elif 'aqua' in available_themes: self.style.theme_use('aqua')
        elif 'vista' in available_themes: self.style.theme_use('vista')
        elif 'alt' in available_themes: self.style.theme_use('alt')

        # --- Main Layout ---
        # Content frame holds the two main sections
        content_frame = ttk.Frame(root, padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid columns to allow resizing
        content_frame.columnconfigure(1, weight=3) # Details area takes more space
        content_frame.columnconfigure(0, weight=1) # Category area
        content_frame.rowconfigure(0, weight=1)    # Allow vertical resizing

        # --- Left Section: Categories ---
        # Use LabelFrame for visual grouping
        left_labelframe = ttk.LabelFrame(content_frame, text="Tool Categories", padding="10")
        left_labelframe.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_labelframe.rowconfigure(0, weight=1) # Allow treeview to expand vertically
        left_labelframe.columnconfigure(0, weight=1) # Allow treeview to expand horizontally

        # Treeview for category list
        self.category_tree = ttk.Treeview(
            left_labelframe,
            selectmode='browse', # Only one item selectable
            show='tree' # Hide the default '#' column header
        )
        # Add a vertical scrollbar
        tree_scrollbar = ttk.Scrollbar(left_labelframe, orient="vertical", command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.category_tree.grid(row=0, column=0, sticky='nsew')
        tree_scrollbar.grid(row=0, column=1, sticky='ns')

        # Populate the Treeview
        self.categories = list(tool_recommendations.keys())
        for category in self.categories:
            # Insert item with category name as text and also store it as item id (iid)
            self.category_tree.insert('', tk.END, text=category, iid=category)

        # Bind selection event
        self.category_tree.bind("<<TreeviewSelect>>", self.on_category_select)

        # "View All" Button
        self.view_all_button = ttk.Button(
            left_labelframe,
            text="View All Tools",
            command=self.show_all_tools # Link button to the function
        )
        self.view_all_button.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(10, 0))


        # --- Right Section: Details ---
        # Use LabelFrame for visual grouping
        right_labelframe = ttk.LabelFrame(content_frame, text="Tool Details", padding="10")
        right_labelframe.grid(row=0, column=1, sticky="nsew")
        right_labelframe.rowconfigure(0, weight=1) # Allow text area to expand
        right_labelframe.columnconfigure(0, weight=1)

        # ScrolledText Area for details
        self.details_text = scrolledtext.ScrolledText(
            right_labelframe,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED # Start read-only
        )
        self.details_text.grid(row=0, column=0, sticky='nsew')

        # Configure text tags (adjusting spacing slightly)
        self.details_text.tag_configure("tool_name", font=("Arial", 11, "bold"), spacing1=6, spacing3=2)
        self.details_text.tag_configure("tool_desc", lmargin1=15, lmargin2=15, spacing1=1, spacing3=8)
        self.details_text.tag_configure("category_header", font=("Arial", 12, "bold", "underline"), spacing1=10, spacing3=10, justify='center')
        self.details_text.tag_configure("all_category_header", font=("Arial", 11, "bold"), spacing1=8, spacing3=4)

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Select a category.")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="2 5")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Show initial message
        self.show_initial_message()

    # --- Methods ---

    def show_initial_message(self):
        """Displays a welcome message."""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert(tk.END, "\n\nWelcome!\n\nPlease select a category from the list on the left\nor click 'View All Tools'.", ('category_header',))
        self.details_text.config(state=tk.DISABLED)
        self.status_var.set("Ready. Select a category or click 'View All'.")

    def show_all_tools(self):
        """Called by the 'View All' button."""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert(tk.END, f"All Recommended Tools\n\n", ('category_header',))

        for cat, tools in tool_recommendations.items():
            self.details_text.insert(tk.END, f"--- {cat} ---\n", ('all_category_header',))
            if not tools:
                self.details_text.insert(tk.END, "  (No tools listed)\n\n", ('tool_desc',))
                continue
            for tool in tools:
                self.details_text.insert(tk.END, f"{tool['name']}\n", ('tool_name',))
                self.details_text.insert(tk.END, f"{textwrap.fill(tool['desc'], width=80)}\n\n", ('tool_desc',))
            self.details_text.insert(tk.END, "\n")

        self.details_text.config(state=tk.DISABLED)
        # Deselect any category in the treeview if 'View All' is clicked
        selection = self.category_tree.selection()
        if selection:
            self.category_tree.selection_remove(selection)
        self.status_var.set("Displaying all tools.")


    def display_tools_for_category(self, category_name):
        """Displays tools for a specific category."""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete('1.0', tk.END)

        if category_name in tool_recommendations:
            tools = tool_recommendations[category_name]
            self.details_text.insert(tk.END, f"Category: {category_name}\n\n", ('category_header',))
            if not tools:
                self.details_text.insert(tk.END, "No tools listed in this category.", ('tool_desc',))
            else:
                for tool in tools:
                    self.details_text.insert(tk.END, f"{tool['name']}\n", ('tool_name',))
                    self.details_text.insert(tk.END, f"{textwrap.fill(tool['desc'], width=80)}\n\n", ('tool_desc',))
            self.status_var.set(f"Selected category: {category_name}")
        else:
             self.details_text.insert(tk.END, f"Information for '{category_name}' not found.", ('tool_desc',))
             self.status_var.set(f"Error: Category '{category_name}' not found.")

        self.details_text.config(state=tk.DISABLED)

    def on_category_select(self, event):
        """Callback function when a category is selected in the Treeview."""
        selected_item = self.category_tree.focus() # Get the item that has focus (selected)
        if not selected_item:
            return

        # In Treeview, the 'iid' (item id) is what we stored the category name in
        selected_category_name = selected_item
        self.display_tools_for_category(selected_category_name)


# --- Start the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ToolApp(root)
    root.mainloop()