# simulator.py (Modified Further)
import sys
import tkinter.font as tkfont
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import datetime
import pickle
import os
import random
import math
import numpy as np

# Prefecture Data
PREFECTURE_NAMES = [
    "Hokkaido", "Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima", "Ibaraki", "Tochigi", "Gunma",
    "Saitama", "Chiba", "Tokyo", "Kanagawa", "Niigata", "Toyama", "Ishikawa", "Fukui", "Yamanashi", "Nagano",
    "Gifu", "Shizuoka", "Aichi", "Mie", "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama", "Tottori",
    "Shimane", "Okayama", "Hiroshima", "Yamaguchi", "Tokushima", "Kagawa", "Ehime", "Kochi", "Fukuoka",
    "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima", "Okinawa"
]

# Placeholder GDP data (e.g., in Billions USD) - From previous step
PREFECTURE_GDP_PLACEHOLDERS = {
    "Tokyo": 1000, "Osaka": 400, "Aichi": 380, "Kanagawa": 350, "Saitama": 230, "Chiba": 210, "Hyogo": 200,
    "Fukuoka": 190, "Hokkaido": 180, "Shizuoka": 170, "Ibaraki": 130, "Hiroshima": 120, "Kyoto": 110,
    "Niigata": 100, "Miyagi": 95, "Gunma": 90, "Tochigi": 88, "Okayama": 85, "Gifu": 80, "Nagano": 78,
    "Mie": 75, "Fukushima": 70, "Shiga": 68, "Yamaguchi": 65, "Kumamoto": 60, "Ehime": 58, "Kagoshima": 55,
    "Toyama": 53, "Ishikawa": 52, "Wakayama": 50, "Oita": 48, "Yamagata": 46, "Nagasaki": 45, "Yamanashi": 44,
    "Aomori": 43, "Iwate": 42, "Akita": 40, "Miyazaki": 38, "Fukui": 37, "Kagawa": 36, "Tokushima": 35,
    "Saga": 34, "Nara": 33, "Okinawa": 32, "Kochi": 30, "Shimane": 28, "Tottori": 25
}

# ** NEW: Placeholder Population Growth Rates (% per year) **
# Based on general trends (Tokyo/Okinawa positive, many rural negative) - Needs real data
PREFECTURE_GROWTH_RATES = {
    "Tokyo": 0.4, "Kanagawa": 0.1, "Saitama": 0.05, "Chiba": 0.0, "Aichi": 0.0, "Osaka": -0.1, "Fukuoka": 0.05,
    "Okinawa": 0.3, "Shiga": 0.0,
    # Most others slightly negative or more significantly negative
    "Hokkaido": -0.5, "Aomori": -1.0, "Iwate": -0.9, "Miyagi": -0.3, "Akita": -1.5, "Yamagata": -1.1, "Fukushima": -0.8,
    "Ibaraki": -0.4, "Tochigi": -0.5, "Gunma": -0.6, "Niigata": -0.9, "Toyama": -0.7, "Ishikawa": -0.6, "Fukui": -0.7,
    "Yamanashi": -0.6, "Nagano": -0.7, "Gifu": -0.5, "Shizuoka": -0.4, "Mie": -0.6, "Kyoto": -0.3, "Hyogo": -0.3,
    "Nara": -0.7, "Wakayama": -1.0, "Tottori": -0.9, "Shimane": -1.1, "Okayama": -0.3, "Hiroshima": -0.2, "Yamaguchi": -0.8,
    "Tokushima": -1.0, "Kagawa": -0.6, "Ehime": -0.9, "Kochi": -1.1, "Saga": -0.7, "Nagasaki": -1.0, "Kumamoto": -0.5,
    "Oita": -0.8, "Miyazaki": -0.9, "Kagoshima": -0.8
}

# ** NEW: Population data parsed from Wikipedia search results (Oct 1, 2022 figures) **
PREFECTURE_POPULATIONS = {
    'Tokyo': 14038167, 'Kanagawa': 9232489, 'Osaka': 8782484, 'Aichi': 7495171,
    'Saitama': 7337089, 'Chiba': 6265975, 'Hyogo': 5402493, 'Hokkaido': 5140354,
    'Fukuoka': 5116046, 'Shizuoka': 3582297, 'Ibaraki': 2839555, 'Hiroshima': 2759500,
    'Kyoto': 2549749, 'Miyagi': 2279977, 'Niigata': 2152693, 'Nagano': 2019993,
    'Gifu': 1945763, 'Gunma': 1913254, 'Tochigi': 1908821, 'Okayama': 1862317,
    'Fukushima': 1790181, 'Mie': 1742174, 'Kumamoto': 1718327, 'Kagoshima': 1562662,
    'Okinawa': 1468318, 'Shiga': 1408931, 'Yamaguchi': 1313403, 'Ehime': 1306486,
    'Nara': 1305812, 'Nagasaki': 1283128, 'Aomori': 1204392, 'Iwate': 1180595,
    'Ishikawa': 1117637, 'Oita': 1106831, 'Miyazaki': 1052338, 'Yamagata': 1041025,
    'Toyama': 1016534, 'Kagawa': 934060, 'Akita': 929901, 'Wakayama': 903265,
    'Yamanashi': 801874, 'Saga': 800787, 'Fukui': 752855, 'Tokushima': 703852,
    'Kochi': 675705, 'Shimane': 657909, 'Tottori': 543620
}


DEFAULT_PM_NAME = "Shigeru Ishiba"
DEFAULT_PARTY_NAME = "Liberal Democratic Party"

class Prefecture:
    # ** MODIFIED: Added population_growth_rate **
    def __init__(self, name, population=None, gdp=None, growth_rate=None):
        self.name = name
        # Use float for population internally to handle fractional growth
        self.population = float(population) if population is not None else float(random.randint(500000, 10000000))
        self.gdp = float(gdp) if gdp is not None else random.uniform(20.0, 100.0) # Billions USD
        self.economy = random.uniform(0.5, 1.5)
        self.approval = random.uniform(40.0, 60.0)
        self.unemployment = random.uniform(3.0, 10.0)
        # ** NEW: Population Growth Rate (% per year) **
        self.population_growth_rate = float(growth_rate) if growth_rate is not None else random.uniform(-1.0, 0.5) # Annual rate

    # ** NEW: Method for daily population update **
    def update_daily_population(self):
        """Updates population based on the annual growth rate, applied daily."""
        # Convert annual rate to daily rate (approximation)
        daily_rate_multiplier = (1.0 + self.population_growth_rate / 100.0)**(1.0/365.0)
        self.population *= daily_rate_multiplier
        # Keep population as float internally, can round for display if needed

    def normalize_values(self):
        """Ensure all values are within valid ranges"""
        self.approval = min(100.0, max(0.0, self.approval))
        self.unemployment = min(30.0, max(1.0, self.unemployment))
        self.economy = min(3.0, max(0.1, self.economy))
        self.gdp = max(1.0, self.gdp)
        self.population = max(1000.0, self.population) # Ensure pop doesn't go below a minimum threshold
        # Optional: Clamp growth rate?
        # self.population_growth_rate = min(5.0, max(-5.0, self.population_growth_rate))

    def get_gdp_per_capita(self):
        if self.population > 0:
            return (self.gdp * 1_000_000_000) / self.population
        return 0

    # ** NEW: Convenience method to get integer population for display/some calcs **
    def get_population_int(self):
        return int(round(self.population))


class PrimeMinister:
    def __init__(self, name, party_name):
        self.name = name
        self.party_name = party_name
        self.global_approval = 50.0
        self.base_popularity = random.uniform(50.0, 70.0)
        self.economy_skill = random.uniform(0.5, 1.5)
        self.unemployment_skill = random.uniform(0.5, 1.5)
        self.welfare_skill = random.uniform(0.5, 1.5)
        # ** NEW: Skill related to demographics/growth policies? **
        self.demographics_skill = random.uniform(0.5, 1.5)

    def calculate_global_approval(self, prefectures):
        total_approval = 0
        total_population = 0
        for prefecture in prefectures:
            pop_int = prefecture.get_population_int() # Use integer pop for weighting
            total_approval += prefecture.approval * pop_int
            total_population += pop_int
        if total_population > 0:
            self.global_approval = min(100.0, max(0.0, (total_approval / total_population)))
        else:
            self.global_approval = 0.0 # Handle case of zero population
        return self.global_approval

class RivalParty:
    def __init__(self, name):
        self.name = name
        self.base_popularity = random.uniform(40.0, 60.0)
        # ** NEW: Attributes for attack strength? **
        self.attack_skill = random.uniform(0.8, 1.2)
        self.preferred_attack = random.choice(["economy", "scandal", "welfare", "competence"])

    # ** NEW: Method to generate an attack message/effect **
    def generate_attack(self):
        """Generates a random attack message and potential approval impact."""
        attack_type = self.preferred_attack
        # Base impact range before skill modification
        base_impact = random.uniform(0.5, 2.5)
        # Modify impact by party's skill
        impact = base_impact * self.attack_skill

        messages = {
            "economy": [
                f"{self.name} criticizes the government's failed economic policies!",
                f"'{self.party_name}'s economic plan is hurting families,' claims {self.name}.",
                f"{self.name} points to rising inflation under the current administration."
            ],
            "scandal": [
                f"{self.name} hints at potential corruption within the cabinet.",
                f"Questions raised by {self.name} about the PM's transparency.",
                f"{self.name} calls for an investigation into government spending."
            ],
            "welfare": [
                f"{self.name} argues that welfare programs are being neglected.",
                f"'{self.party_name} doesn't care about the elderly,' says {self.name}.",
                f"{self.name} promises better social support if elected."
            ],
            "competence": [
                f"{self.name} slams the government's handling of recent events.",
                f"'{self.party_name} is out of touch with the people,' states {self.name}.",
                f"{self.name} questions the PM's leadership abilities."
            ]
        }
        message = random.choice(messages.get(attack_type, messages["competence"]))
        return message, impact # Returns the message and the calculated approval hit


class CountryStatistics:
    def __init__(self):
        self.economy = {
            'gdp_ppp': 6.31, 'gdp_nominal': 4.204, 'gdp_per_capita': 36990.33,
            'inflation': 3.2, 'growth_rate': 0.9,
        }
        self.demographics = {
            'population': 125921755, 'density': 333.2, 'migration_rate': 0.08,
            'birth_rate': 5.7,
            'immigration': {
                'total_foreigners': 3768977,
                'source_countries': [("China", 873286), ("Vietnam", 634361), ("South Korea", 409238), ("Nepal", 124356), ("Brazil", 206886)],
                'immigration_rate': 10.5
            }
        }

class PrefectureTab:
    # (No changes needed in PrefectureTab class structure itself for these new features)
    # ... (Keep PrefectureTab class as defined in the previous step) ...
    """A container for prefecture data tab in the notebook"""
    def __init__(self, parent, prefecture_data):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.prefecture_data = prefecture_data # Now expects data including GDP and GDP per capita
        self.setup_ui()

    def setup_ui(self):
        # Setup sorter and filters at the top
        sort_frame = tk.Frame(self.frame, bg="#f0f0f8")
        sort_frame.pack(fill=tk.X, pady=5)

        tk.Label(sort_frame, text="Sort by:", bg="#f0f0f8").pack(side=tk.LEFT, padx=5)
        # ** MODIFIED: Added Growth Rate **
        sort_options = ["Prefecture Name", "Population", "Economy", "Approval Rating", "Unemployment Rate",
                        "GDP (B USD)", "GDP per Capita (USD)", "Pop. Growth (%)"] # Added Growth Rate
        self.sort_var = tk.StringVar(value=sort_options[0])
        sort_menu = ttk.Combobox(sort_frame, textvariable=self.sort_var, values=sort_options, width=20)
        sort_menu.pack(side=tk.LEFT, padx=5)

        self.sort_asc_var = tk.BooleanVar(value=True)
        asc_radio = tk.Radiobutton(sort_frame, text="Ascending", variable=self.sort_asc_var, value=True, bg="#f0f0f8")
        desc_radio = tk.Radiobutton(sort_frame, text="Descending", variable=self.sort_asc_var, value=False, bg="#f0f0f8")
        asc_radio.pack(side=tk.LEFT, padx=5)
        desc_radio.pack(side=tk.LEFT, padx=5)

        search_frame = tk.Frame(sort_frame, bg="#f0f0f8")
        search_frame.pack(side=tk.RIGHT, padx=10)

        tk.Label(search_frame, text="Search:", bg="#f0f0f8").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=15)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Setup treeview with scrollbars
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        v_scrollbar = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # ** MODIFIED: Updated columns list **
        columns = ("name", "population", "economy", "approval", "unemployment", "gdp", "gdp_per_capita", "growth_rate") # Added growth_rate
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                          yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Configure scrollbars
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)

        # ** MODIFIED: Define column headings (Added Growth Rate) **
        self.tree.heading("name", text="Prefecture", command=lambda: self.sort_treeview("name", False))
        self.tree.heading("population", text="Population", command=lambda: self.sort_treeview("population", True))
        self.tree.heading("economy", text="Economy Score", command=lambda: self.sort_treeview("economy", True))
        self.tree.heading("approval", text="Approval %", command=lambda: self.sort_treeview("approval", True))
        self.tree.heading("unemployment", text="Unemployment %", command=lambda: self.sort_treeview("unemployment", True))
        self.tree.heading("gdp", text="GDP (B USD)", command=lambda: self.sort_treeview("gdp", True))
        self.tree.heading("gdp_per_capita", text="GDP p/c (USD)", command=lambda: self.sort_treeview("gdp_per_capita", True))
        self.tree.heading("growth_rate", text="Pop Growth %", command=lambda: self.sort_treeview("growth_rate", True)) # Added Growth Rate

        # ** MODIFIED: Set column widths (Adjusted for new column) **
        self.tree.column("name", width=110, anchor=tk.W)
        self.tree.column("population", width=110, anchor=tk.E)
        self.tree.column("economy", width=90, anchor=tk.E)
        self.tree.column("approval", width=80, anchor=tk.E)
        self.tree.column("unemployment", width=110, anchor=tk.E)
        self.tree.column("gdp", width=90, anchor=tk.E)
        self.tree.column("gdp_per_capita", width=100, anchor=tk.E)
        self.tree.column("growth_rate", width=90, anchor=tk.E) # Added Growth Rate


        # Pack the treeview
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind events
        sort_menu.bind("<<ComboboxSelected>>", lambda e: self.populate_tree())
        asc_radio.config(command=self.populate_tree)
        desc_radio.config(command=self.populate_tree)
        self.search_entry.bind("<KeyRelease>", lambda e: self.populate_tree())

        # Initial population
        self.populate_tree()

    def sort_treeview(self, column, is_numeric):
        """Sort treeview when header is clicked"""
        column_name_map = {
            "name": "Prefecture Name", "population": "Population", "economy": "Economy Score",
            "approval": "Approval Rating", "unemployment": "Unemployment Rate",
            "gdp": "GDP (B USD)", "gdp_per_capita": "GDP per Capita (USD)",
            "growth_rate": "Pop. Growth (%)" # Added Growth Rate
        }
        sort_display_name = column_name_map.get(column, "Prefecture Name")

        if self.sort_var.get() == sort_display_name:
            self.sort_asc_var.set(not self.sort_asc_var.get())
        else:
            self.sort_var.set(sort_display_name)
            self.sort_asc_var.set(True)

        self.populate_tree()

    def populate_tree(self):
        """Populate the treeview with sorted and filtered data"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        sort_column = self.sort_var.get()
        # ** MODIFIED: Updated column mapping **
        column_mapping = {
            "Prefecture Name": 0, "Population": 1, "Economy Score": 2, "Approval Rating": 3,
            "Unemployment Rate": 4, "GDP (B USD)": 5, "GDP per Capita (USD)": 6,
            "Pop. Growth (%)": 7 # Added Growth Rate
        }
        sort_idx = column_mapping.get(sort_column, 0)

        search_text = self.search_entry.get().lower()
        filtered_data = [data for data in self.prefecture_data if search_text in data[0].lower()]

        try:
            # Sort using the correct index
            sorted_data = sorted(filtered_data,
                               key=lambda x: x[sort_idx] if x[sort_idx] is not None else ('' if not isinstance(x[sort_idx], (int, float)) else 0),
                               reverse=not self.sort_asc_var.get())
        except (TypeError, IndexError): # Added IndexError safety
             sorted_data = sorted(filtered_data, key=lambda x: x[0], reverse=not self.sort_asc_var.get())

        # Insert data
        for i, data in enumerate(sorted_data):
            # ** MODIFIED: Unpack new data structure **
            name, population, economy, approval, unemployment, gdp, gdp_per_capita, growth_rate = data
            formatted_pop = f"{population:,}" # Use integer population for display
            formatted_gdp_pc = f"${gdp_per_capita:,.0f}"
            formatted_growth = f"{growth_rate:+.2f}%" # Format growth rate

            # ** MODIFIED: Insert new columns **
            self.tree.insert("", i, values=(name, formatted_pop, f"{economy:.2f}",
                                          f"{approval:.1f}%", f"{unemployment:.1f}%",
                                          f"{gdp:.1f}", formatted_gdp_pc,
                                          formatted_growth)) # Added growth rate value

    def update_data(self, new_data):
        """Update with new prefecture data"""
        self.prefecture_data = new_data
        self.populate_tree()

class RegionAnalysisTab:
    # (No major changes needed here unless adding Growth Rate as an analysis option)
    # ... (Keep RegionAnalysisTab class largely as is) ...
    """A container for region analysis tab in the notebook"""
    def __init__(self, parent, prefecture_data):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.prefecture_data = prefecture_data # Expects data with GDP/GDP p.c. and maybe growth
        self.setup_ui()

    def setup_ui(self):
        # Define regions (same as before)
        self.regions = {
            "Hokkaido": ["Hokkaido"],
            "Tohoku": ["Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima"],
            "Kanto": ["Ibaraki", "Tochigi", "Gunma", "Saitama", "Chiba", "Tokyo", "Kanagawa"],
            "Chubu": ["Niigata", "Toyama", "Ishikawa", "Fukui", "Yamanashi", "Nagano", "Gifu", "Shizuoka", "Aichi"],
            "Kansai": ["Mie", "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama"],
            "Chugoku": ["Tottori", "Shimane", "Okayama", "Hiroshima", "Yamaguchi"],
            "Shikoku": ["Tokushima", "Kagawa", "Ehime", "Kochi"],
            "Kyushu & Okinawa": ["Fukuoka", "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima", "Okinawa"]
        }

        # Create figure
        self.fig = plt.Figure(figsize=(9, 5), dpi=100)

        # Create a frame for the chart
        chart_frame = tk.Frame(self.frame)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Display options
        options_frame = tk.Frame(self.frame, bg="#f0f0f8")
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(options_frame, text="Display:", bg="#f0f0f8").pack(side=tk.LEFT, padx=5)
        self.display_var = tk.StringVar(value="Population")
        # ** MODIFIED: Optionally add Growth Rate **
        display_options = ["Population", "Approval", "Economy", "Unemployment", "GDP", "GDP per Capita", "Pop. Growth"] # Added Growth
        display_menu = ttk.Combobox(options_frame, textvariable=self.display_var,
                                  values=display_options, width=15)
        display_menu.pack(side=tk.LEFT, padx=5)
        display_menu.bind("<<ComboboxSelected>>", lambda e: self.update_chart())

        # Create initial chart
        self.create_charts(chart_frame)
        self.update_chart()

    def create_charts(self, parent_frame):
        """Create the chart canvas"""
        self.canvas = FigureCanvasTkAgg(self.fig, parent_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_chart(self):
        """Update the chart with selected display option"""
        self.fig.clear()
        display_type = self.display_var.get()

        ax1 = self.fig.add_subplot(121)  # Pie chart
        ax2 = self.fig.add_subplot(122)  # Bar chart

        region_data = {}
        # ** MODIFIED: Map display type to data index including Growth **
        data_idx = {"Population": 1, "Economy": 2, "Approval": 3, "Unemployment": 4,
                    "GDP": 5, "GDP per Capita": 6, "Pop. Growth": 7} # Added Growth
        idx = data_idx.get(display_type)
        if idx is None: # Fallback if display type not found
            print(f"Warning: Display type '{display_type}' not mapped.")
            idx = 1 # Default to population

        for region_name, prefectures in self.regions.items():
            # Use integer population for weighting averages
            region_prefs = [p for p in self.prefecture_data if p[0] in prefectures]

            if region_prefs:
                # Ensure data exists at the required index
                valid_prefs = [p for p in region_prefs if len(p) > idx and p[idx] is not None]
                if not valid_prefs:
                    region_data[region_name] = 0 # Or handle as missing data
                    continue

                if display_type in ["Population", "GDP"]: # Sum these values
                    region_data[region_name] = sum(p[idx] for p in valid_prefs)
                else: # Calculate population-weighted average for other metrics
                    # Use get_population_int() which is index 1
                    total_pop = sum(p[1] for p in valid_prefs if len(p) > 1 and p[1] is not None)
                    if total_pop > 0:
                         # Weighted sum: population (index 1) * metric (index idx)
                         weighted_sum = sum(p[1] * p[idx] for p in valid_prefs if len(p) > 1 and p[1] is not None)
                         weighted_avg = weighted_sum / total_pop
                    else: # Fallback to simple average if no population data
                         weighted_avg = sum(p[idx] for p in valid_prefs) / len(valid_prefs) if valid_prefs else 0
                    region_data[region_name] = weighted_avg


        # Sort and prepare data for charts
        sorted_items = sorted(region_data.items(), key=lambda x: x[1], reverse=True)
        labels, values = zip(*sorted_items) if sorted_items else ([], [])

        # Create pie chart
        if values:
            explode = [0.05] * len(labels)
            autopct_format = '%1.1f%%'
            title_suffix = " Distribution"

            if display_type == "Population": formatted_labels = [f"{l}\n({v:,.0f})" for l, v in zip(labels, values)]
            elif display_type == "GDP": formatted_labels = [f"{l}\n(${v:.1f}B)" for l, v in zip(labels, values)]; title_suffix += " (B USD)"
            elif display_type == "GDP per Capita": formatted_labels = [f"{l}\n(${v:,.0f})" for l, v in zip(labels, values)]; title_suffix += " (USD)"
            elif display_type == "Pop. Growth": formatted_labels = [f"{l}\n({v:+.2f}%)" for l, v in zip(labels, values)]; title_suffix += " (Avg %)"
            else:
                unit = "%" if display_type in ["Approval", "Unemployment"] else ""
                formatted_labels = [f"{l}\n({v:.1f}{unit})" for l, v in zip(labels, values)]
                if unit != "%": title_suffix += " (Avg Score)"
                else: title_suffix += " (Avg %)"

            title = f"Region {display_type}{title_suffix}"
            ax1.pie(values, labels=None, autopct=autopct_format, startangle=90, shadow=False, explode=explode)
            ax1.axis('equal')
            ax1.set_title(title)
            ax1.legend(labels, loc="center left", bbox_to_anchor=(1.1, 0.5), fontsize='small')
        else: ax1.set_title(f"No data for {display_type}")

        # Create bar chart
        if values:
            colors = plt.cm.viridis(np.linspace(0, 0.9, len(labels)))
            ax2.bar(labels, values, color=colors)
            ylabel = display_type

            if display_type == "Population": ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/1000000:.1f}M'))
            elif display_type == "GDP": ylabel += ' (Billions USD)'; ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:.0f}B'))
            elif display_type == "GDP per Capita": ylabel += ' (USD)'; ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
            elif display_type == "Pop. Growth": ylabel = 'Avg Pop. Growth (%)'; ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:+.2f}%'))
            else:
                unit = "%" if display_type in ["Approval", "Unemployment"] else ""
                ylabel = f'Avg {display_type} {unit}'

            ax2.set_ylabel(ylabel)
            ax2.set_title(f'{display_type} by Region')
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        else: ax2.set_title(f"No data for {display_type}")

        self.fig.tight_layout(rect=[0, 0, 0.85, 1])
        self.canvas.draw()

    def update_data(self, new_data):
        """Update with new prefecture data"""
        self.prefecture_data = new_data
        self.update_chart()


class PrefectureMapTab:
    # (No major changes needed here unless adding Growth Rate as a map option)
    # ... (Keep PrefectureMapTab class largely as is) ...
    """A container for prefecture map visualization"""
    def __init__(self, parent, prefecture_data):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.prefecture_data = prefecture_data # Expects data with GDP/GDP p.c. and maybe growth
        self.setup_ui()

    def setup_ui(self):
        # Control frame at top
        control_frame = tk.Frame(self.frame, bg="#f0f0f8")
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(control_frame, text="Color by:", bg="#f0f0f8").pack(side=tk.LEFT, padx=5)
        self.color_var = tk.StringVar(value="Approval")
        # ** MODIFIED: Optionally add Growth Rate **
        color_options = ["Approval", "Population", "Economy", "Unemployment", "GDP", "GDP per Capita", "Pop. Growth"] # Added Growth
        color_menu = ttk.Combobox(control_frame, textvariable=self.color_var,
                                values=color_options, width=15)
        color_menu.pack(side=tk.LEFT, padx=5)
        color_menu.bind("<<ComboboxSelected>>", lambda e: self.draw_map())

        # Create canvas for map
        self.canvas = tk.Canvas(self.frame, bg="white", width=600, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Information label
        self.info_label = tk.Label(self.frame, text="Hover over a region to see details",
                                 bg="#f0f0f8", font=("Arial", 10))
        self.info_label.pack(pady=5)

        # Draw the initial map
        self.draw_map()

    def draw_map(self):
        """Draw a simplified map of Japan with prefecture data"""
        self.canvas.delete("all")

        # Layout and region definitions (same as before)
        region_layouts = {
            "Hokkaido": {"x": 450, "y": 50, "width": 120, "height": 100}, "Tohoku": {"x": 450, "y": 170, "width": 80, "height": 150},
            "Kanto": {"x": 450, "y": 330, "width": 90, "height": 90}, "Chubu": {"x": 360, "y": 330, "width": 80, "height": 80},
            "Kansai": {"x": 300, "y": 350, "width": 70, "height": 70}, "Chugoku": {"x": 220, "y": 330, "width": 80, "height": 50},
            "Shikoku": {"x": 240, "y": 400, "width": 70, "height": 40}, "Kyushu": {"x": 150, "y": 350, "width": 70, "height": 100},
            "Okinawa": {"x": 80, "y": 450, "width": 30, "height": 30}
        }
        regions = {
            "Hokkaido": ["Hokkaido"], "Tohoku": ["Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima"],
            "Kanto": ["Ibaraki", "Tochigi", "Gunma", "Saitama", "Chiba", "Tokyo", "Kanagawa"], "Chubu": ["Niigata", "Toyama", "Ishikawa", "Fukui", "Yamanashi", "Nagano", "Gifu", "Shizuoka", "Aichi"],
            "Kansai": ["Mie", "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama"], "Chugoku": ["Tottori", "Shimane", "Okayama", "Hiroshima", "Yamaguchi"],
            "Shikoku": ["Tokushima", "Kagawa", "Ehime", "Kochi"], "Kyushu": ["Fukuoka", "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima"], "Okinawa": ["Okinawa"]
        }

        # Find min/max values for normalization across all prefectures
        display_type = self.color_var.get()
        # ** MODIFIED: Map display type to data index including Growth **
        data_idx = {"Population": 1, "Economy": 2, "Approval": 3, "Unemployment": 4,
                    "GDP": 5, "GDP per Capita": 6, "Pop. Growth": 7}
        idx = data_idx.get(display_type, 3) # Default to Approval

        # Get all valid values for the selected metric
        all_values = [p[idx] for p in self.prefecture_data if len(p) > idx and p[idx] is not None]
        min_val, max_val = (min(all_values), max(all_values)) if all_values else (0, 1)
        range_val = max_val - min_val if max_val > min_val else 1.0 # Avoid division by zero


        for region_name, layout in region_layouts.items():
            x, y, width, height = layout["x"], layout["y"], layout["width"], layout["height"]
            prefecture_names = regions.get(region_name, [])
            prefecture_data_list = [p for p in self.prefecture_data if p[0] in prefecture_names]

            # Calculate the average or total value for the selected metric for this region
            total_value = 0
            normalized_value = 0.5 # Default grey

            if prefecture_data_list:
                valid_prefs = [p for p in prefecture_data_list if len(p) > idx and p[idx] is not None]
                if valid_prefs:
                    values_in_region = [p[idx] for p in valid_prefs]
                    if display_type in ["Population", "GDP"]:
                        total_value = sum(values_in_region)
                        current_val = total_value # Normalize based on the sum
                    else: # Weighted average for others
                        total_pop = sum(p[1] for p in valid_prefs if len(p) > 1 and p[1] is not None)
                        if total_pop > 0:
                            weighted_sum = sum(p[1] * p[idx] for p in valid_prefs if len(p) > 1 and p[1] is not None)
                            total_value = weighted_sum / total_pop
                        else: # Simple average fallback
                            total_value = sum(values_in_region) / len(values_in_region) if values_in_region else 0
                        current_val = total_value # Normalize based on the average

                    # Normalize the calculated value using overall min/max
                    normalized_value = (current_val - min_val) / range_val if range_val > 0 else 0.5
                    normalized_value = min(1.0, max(0.0, normalized_value)) # Clamp 0-1

                    # Invert for unemployment (lower is better -> greener)
                    if display_type == "Unemployment":
                        normalized_value = 1.0 - normalized_value

            # Convert normalized value to color (green for high/good, red for low/bad)
            r = int(255 * (1 - normalized_value))
            g = int(255 * normalized_value)
            b = 100
            color = f"#{r:02x}{g:02x}{b:02x}"

            region_id = self.canvas.create_rectangle(x, y, x+width, y+height, fill=color, outline="black", width=2)
            self.canvas.create_text(x + width/2, y + height/2, text=region_name, font=("Arial", 10, "bold"))

            # Bind hover event
            self.canvas.tag_bind(region_id, "<Enter>",
                              lambda e, rn=region_name, plist=prefecture_data_list,
                              dt=display_type, tv=total_value, norm_v=normalized_value:
                              self.show_region_info(rn, plist, dt, tv, norm_v))
            self.canvas.tag_bind(region_id, "<Leave>", self.clear_info)

        # Add legend
        self.draw_legend(display_type, min_val, max_val)


    def draw_legend(self, display_type, min_val, max_val):
        """Draw a color legend for the map"""
        legend_x, legend_y = 50, 50
        legend_width, legend_height = 20, 200

        self.canvas.create_rectangle(legend_x, legend_y, legend_x + legend_width, legend_y + legend_height, fill="white", outline="black")

        steps = 20
        for i in range(steps):
            y_step = i * (legend_height / steps)
            norm_val = 1.0 - (i / float(steps))  # Normalized value (1 at top, 0 at bottom)

            # Color logic matches map drawing (Red=Low, Green=High, except Unemployment)
            r = int(255 * (1 - norm_val))
            g = int(255 * norm_val)
            b = 100
            color = f"#{r:02x}{g:02x}{b:02x}"

            self.canvas.create_rectangle(legend_x, legend_y + y_step, legend_x + legend_width, legend_y + y_step + (legend_height / steps), fill=color, outline="")

        # Determine labels based on whether high value is good (green) or bad (red)
        high_is_good = display_type != "Unemployment"

        # Format labels based on type
        def format_value(val, dtype):
            if dtype == "Population": return f"{val:,.0f}"
            if dtype == "GDP": return f"${val:.1f}B"
            if dtype == "GDP per Capita": return f"${val:,.0f}"
            if dtype in ["Approval", "Unemployment", "Pop. Growth"]: return f"{val:+.1f}%" # Show sign for growth
            if dtype == "Economy": return f"{val:.2f}"
            return f"{val:.1f}"

        top_val = max_val
        bottom_val = min_val
        top_label_text = f"High ({format_value(top_val, display_type)})"
        bottom_label_text = f"Low ({format_value(bottom_val, display_type)})"

        # Swap labels if high value is represented by red
        if not high_is_good:
            top_label_text, bottom_label_text = bottom_label_text, top_label_text

        self.canvas.create_text(legend_x + legend_width + 10, legend_y, text=top_label_text, anchor="w")
        self.canvas.create_text(legend_x + legend_width + 10, legend_y + legend_height, text=bottom_label_text, anchor="w")
        self.canvas.create_text(legend_x + legend_width/2, legend_y - 10, text=f"{display_type}", anchor="s")

    def show_region_info(self, region_name, prefecture_list, display_type, total_value, normalized_value):
        """Display information about the region on hover"""
        if not prefecture_list:
            text = f"{region_name}: No data available"
        else:
            # Format the displayed value based on whether it's a sum or average
            value_label = ""
            if display_type == "Population": value_label = f"{total_value:,.0f}"
            elif display_type == "GDP": value_label = f"${total_value:.1f}B"
            elif display_type == "GDP per Capita": value_label = f"${total_value:,.0f} (Avg)"
            elif display_type in ["Approval", "Unemployment", "Pop. Growth"]: value_label = f"{total_value:+.1f}% (Avg)"
            elif display_type == "Economy": value_label = f"{total_value:.2f} (Avg)"
            else: value_label = f"{total_value:.2f} (Avg)"

            prefectures = ", ".join([p[0] for p in prefecture_list])
            text = f"{region_name} - Avg {display_type}: {value_label}\nPrefectures: {prefectures}"
            if display_type in ["Population", "GDP"]: # Clarify if it's total
                 text = f"{region_name} - Total {display_type}: {value_label}\nPrefectures: {prefectures}"


        self.info_label.config(text=text)


    def clear_info(self, event):
        """Clear the information display"""
        self.info_label.config(text="Hover over a region to see details")

    def update_data(self, new_data):
        """Update with new prefecture data"""
        self.prefecture_data = new_data
        self.draw_map()


class Simulation:
    def __init__(self, fresh=True, pm_name=None, party_name=None):
        self.stats = CountryStatistics()
        self.prefectures = []
        
        # Check if all prefectures have population data
        for name in PREFECTURE_NAMES:
            if name not in PREFECTURE_POPULATIONS:
                print(f"Warning: Missing population data for {name}, using default.")
                PREFECTURE_POPULATIONS[name] = 500000  # Default fallback
        
        # Initialize prefectures with real population data
        for name in PREFECTURE_NAMES:
            pop = PREFECTURE_POPULATIONS.get(name, 500000.0)  # Use real population data
            gdp = PREFECTURE_GDP_PLACEHOLDERS.get(name, random.uniform(20.0, 100.0))
            growth = PREFECTURE_GROWTH_RATES.get(name, random.uniform(-1.0, 0.5))
            self.prefectures.append(Prefecture(name, population=pop, gdp=gdp, growth_rate=growth))
        
        self.pm_name = pm_name if pm_name else DEFAULT_PM_NAME
        self.party_name = party_name if party_name else DEFAULT_PARTY_NAME
        self.pm = PrimeMinister(self.pm_name, self.party_name)
        self.day = 1
        self.month = 1
        self.year = 2025
        self.running = True
        self.game_over_reason = None
        
        # ** NEW: Election state management **
        self.election_in_progress = None # Can be None, 'triggered', 'attack_phase', 'voting_day'
        self.election_attack_messages = [] # Store messages for the popup
        
        # Initial calculation
        self.pm.calculate_global_approval(self.prefectures)
        self.approval_history = [self.pm.global_approval]
        self.approval_dates = [datetime.date(self.year, self.month, self.day)]
        
        self.rivals = [
            RivalParty("Constitutional Democratic Party"),
            RivalParty("Democratic Party for the People"),
            RivalParty("Nihon Ishin no Kai"),
        ]
        
        self.events = []

    def make_policy(self, policy_type):
        """Make a policy and influence stats"""
        if not self.running or self.election_in_progress: # Prevent actions during election
            return None, "Game Over" if not self.running else "Election in Progress"

        policy_effect = 0; policy_name = ""; catastrophic = False; positive = False # Define positive here

        def high_risk_outcome(pos_range, neg_range):
            success = random.random() < 0.5
            value = random.uniform(*pos_range) if success else -random.uniform(*neg_range)
            return value, success # Return value and success boolean

        # --- Policy Effects ---
        # (Simplified effects - adjust ranges and add more nuanced impacts)
        if policy_type == "economy":
            policy_effect, positive = high_risk_outcome((6, 14), (7, 15))
            policy_name = random.choice(["Economic Stimulus", "Industrial Plan", "Trade Initiative", "Investment Promotion"])
            for p in self.prefectures:
                gdp_change = (0.02 + 0.03 * self.pm.economy_skill) if positive else (-0.01 - 0.03 / self.pm.economy_skill)
                p.gdp *= (1 + gdp_change)
                p.approval += policy_effect * random.uniform(0.8, 1.2) # Apply approval effect
                p.economy += (0.1 * self.pm.economy_skill) if positive else (-0.1 / self.pm.economy_skill)
                # Economy policy might slightly affect growth rate
                p.population_growth_rate += (0.05 * self.pm.economy_skill) if positive else (-0.05 / self.pm.economy_skill)
                p.normalize_values()
            self.stats.economy['gdp_nominal'] = sum(p.gdp for p in self.prefectures)
            self.stats.economy['growth_rate'] += (0.1 if positive else -0.1)

        elif policy_type == "unemployment":
            policy_effect, positive = high_risk_outcome((5, 10), (6, 12))
            policy_name = random.choice(["Job Creation", "Workforce Training", "Small Business Support", "Employment Subsidy"])
            for p in self.prefectures:
                p.unemployment -= (1.0 + 1.0 * self.pm.unemployment_skill) if positive else (-0.5 - 1.0 / self.pm.unemployment_skill)
                p.approval += policy_effect * random.uniform(0.7, 1.3)
                # Maybe slightly boost growth if unemployment drops significantly?
                if positive and p.unemployment < 4.0:
                     p.population_growth_rate += 0.02 * self.pm.unemployment_skill
                p.normalize_values()

        elif policy_type == "welfare":
            policy_effect, positive = high_risk_outcome((6, 12), (7, 14))
            policy_name = random.choice(["Healthcare Reform", "Pension Overhaul", "Social Security Boost", "Family Support"])
            for p in self.prefectures:
                p.approval += policy_effect * random.uniform(0.9, 1.1)
                # ** MODIFIED: Welfare policy directly impacts growth rate **
                growth_impact = (0.1 + 0.1 * self.pm.welfare_skill) if positive else (-0.1 - 0.1 / self.pm.welfare_skill)
                p.population_growth_rate += growth_impact
                p.normalize_values()
            self.stats.demographics['birth_rate'] += 0.1 if positive else -0.05 # Simplified national effect

        # ** NEW POLICY EXAMPLE: Childcare Subsidies **
        elif policy_type == "childcare_subsidies":
            policy_effect, positive = high_risk_outcome((5, 10), (4, 8)) # Usually positive effect expected
            policy_name = "Childcare Subsidy Program"
            for p in self.prefectures:
                p.approval += policy_effect * random.uniform(0.8, 1.2)
                # Directly boost growth rate, more strongly if positive
                growth_impact = (0.15 + 0.1 * self.pm.demographics_skill) if positive else (-0.05 / self.pm.demographics_skill)
                p.population_growth_rate += growth_impact
                p.normalize_values()
            self.stats.demographics['birth_rate'] += 0.15 if positive else -0.02 # Small national effect


        # --- Other policies (Austerity, Corruption, Gambles) ---
        # (Keep existing logic, potentially add minor growth rate impacts)
        elif policy_type == "austerity":
            policy_effect, positive = high_risk_outcome((2, 6), (8, 16)) # More likely negative
            policy_name = random.choice(["Austerity Budget", "Public Sector Cuts", "Welfare Reduction"])
            for p in self.prefectures:
                p.approval += policy_effect * random.uniform(0.8, 1.2)
                p.economy -= 0.1 / self.pm.economy_skill # Austerity usually hurts economy score
                p.unemployment += 0.5 / self.pm.unemployment_skill # And increases unemployment
                # Austerity likely reduces population growth
                p.population_growth_rate -= (0.1 + 0.1 / self.pm.demographics_skill)
                p.normalize_values()

        elif policy_type == "corrupt_deal": # Risk of scandal
            policy_effect, positive = high_risk_outcome((1, 5), (10, 20)) # High risk of large negative if discovered
            policy_name = random.choice(["Secret Deal", "Crony Contract", "Illegal Funding"])
            if positive: # Got away with it (small temporary boost)
                 policy_name += " (Successful)"
                 for p in self.prefectures:
                     p.approval += policy_effect
                     p.normalize_values()
            else: # Scandal!
                policy_name += " Scandal Exposed!"
                catastrophic = True # Treat exposure as catastrophic
                for p in self.prefectures:
                    p.approval += policy_effect # Apply large negative effect
                    p.normalize_values()
                self.events.append(f"SCANDAL! {policy_name}")


        elif policy_type == "nuclear_energy_gamble":
            policy_effect, positive = high_risk_outcome((12, 20), (15, 30))
            if positive:
                policy_name = "Nuclear Expansion Success"
                for p in self.prefectures:
                    p.gdp *= (1 + random.uniform(0.03, 0.06))
                    p.approval += policy_effect * random.uniform(0.8, 1.2)
                    p.economy += 0.2 * self.pm.economy_skill
                    p.normalize_values()
            else:
                policy_name = "Nuclear Accident Disaster"
                catastrophic = True
                for p in self.prefectures:
                    p.approval += policy_effect * random.uniform(0.9, 1.1)
                    p.population_growth_rate -= random.uniform(0.1, 0.5) # People might leave affected areas
                    p.normalize_values()
                self.events.append(f"CATASTROPHE: {policy_name}")


        elif policy_type == "tech_gamble":
            policy_effect, positive = high_risk_outcome((15, 25), (12, 20))
            if positive:
                policy_name = "AI Tech Revolution"
                for p in self.prefectures:
                    p.gdp *= (1 + random.uniform(0.05, 0.10))
                    p.approval += policy_effect * random.uniform(0.8, 1.2)
                    p.economy += 0.3 * self.pm.economy_skill
                    p.unemployment -= 0.5 * self.pm.unemployment_skill
                    # Tech boom might attract people
                    p.population_growth_rate += random.uniform(0.05, 0.15) * self.pm.demographics_skill
                    p.normalize_values()
            else:
                policy_name = "Tech Bubble Burst"
                for p in self.prefectures:
                    p.gdp *= (1 - random.uniform(0.02, 0.05))
                    p.approval += policy_effect * random.uniform(0.9, 1.1)
                    p.economy -= 0.2 / self.pm.economy_skill
                    # Bubble burst might slow growth
                    p.population_growth_rate -= random.uniform(0.05, 0.1) / self.pm.demographics_skill
                    p.normalize_values()


        # Recalculate global approval after policy effects
        self.pm.calculate_global_approval(self.prefectures)

        # Add event message (avoiding duplicate scandal/catastrophe messages)
        if not catastrophic and "Scandal" not in policy_name:
             outcome = "Success" if positive else "Failure"
             self.events.append(f"Policy: {policy_name} ({outcome})")

        if len(self.events) > 10: self.events.pop(0)

        # Check for election trigger
        self.check_for_election()

        return policy_effect, policy_name

    def random_event(self):
        """Random events affecting approval"""
        if not self.running or self.election_in_progress: return None, None

        if random.random() > 0.2: return None, None # 20% chance

        event_type = random.choice(["scandal", "natural_disaster", "economic_boom", "foreign_success"])
        event_name = ""; effect = 0

        if event_type == "scandal":
            event_name = random.choice(["Minister Resigns", "Corruption Allegations", "Funds Misuse Exposed", "Gaffe Backlash"])
            effect = -random.uniform(3.0, 8.0)
        elif event_type == "natural_disaster":
            event_name = random.choice(["Typhoon Strike", "Kansai Earthquake", "Northern Flooding", "Volcano Warning"])
            effect = -random.uniform(2.0, 5.0)
            # Disasters can impact growth negatively
            for p in self.prefectures:
                 p.population_growth_rate -= random.uniform(0.01, 0.1) # Random small negative impact
                 p.normalize_values()
        elif event_type == "economic_boom":
            event_name = random.choice(["Stock Market Rally", "Major Investment Deal", "Tourism Boom", "Tech Sector Growth"])
            effect = random.uniform(3.0, 7.0)
            # Booms might slightly increase growth
            for p in self.prefectures:
                 p.population_growth_rate += random.uniform(0.01, 0.05)
                 p.normalize_values()
        elif event_type == "foreign_success":
            event_name = random.choice(["Trade Deal Signed", "Diplomatic Victory", "Peace Initiative Success", "New Alliance Formed"])
            effect = random.uniform(2.0, 6.0)

        # Apply approval effect locally
        for p in self.prefectures:
            p.approval += effect * random.uniform(0.7, 1.3)
            p.normalize_values()

        self.pm.calculate_global_approval(self.prefectures)
        self.events.append(f"Event: {event_name}")
        if len(self.events) > 10: self.events.pop(0)

        self.check_for_election()
        return event_type, event_name

    # ** MODIFIED: Advance day handles population growth and election state **
    def advance_day(self):
        """Advance the simulation by one day, handling growth and elections."""
        if not self.running: return None, None

        # --- Handle Election State Machine ---
        if self.election_in_progress == 'triggered':
            self.election_in_progress = 'attack_phase'
            self.handle_election_attacks() # Run attacks, update approval
            # Record approval *after* attacks
            self.approval_history.append(self.pm.global_approval)
            self.approval_dates.append(datetime.date(self.year, self.month, self.day))
            # Return immediately, day advances effectively to attack day results
            return "election_attack", "Rival parties launch attacks!"

        elif self.election_in_progress == 'attack_phase':
            self.election_in_progress = 'voting_day'
            # No approval change today, just transition state
            # Day advances to voting day
            # Record approval (should be same as end of attack day)
            self.approval_history.append(self.pm.global_approval)
            self.approval_dates.append(datetime.date(self.year, self.month, self.day))
            return "election_voting", "Election voting begins!"

        elif self.election_in_progress == 'voting_day':
            self.handle_election_voting() # This will set running=False if lost
            self.election_in_progress = None # Election cycle ends
            # Record final approval after vote outcome (might be unchanged if won)
            self.approval_history.append(self.pm.global_approval)
            self.approval_dates.append(datetime.date(self.year, self.month, self.day))
            # If still running, proceed with normal day advancement below
            if not self.running:
                 return "election_result", "Election results are in!" # Game Over handled by check later
            # If survived, continue to normal day processing for the day *after* voting


        # --- Normal Day Advancement ---
        # Update Date
        self.day += 1
        days_in_month = 30 # Simplified month length (can be improved)
        if self.month == 2: days_in_month = 28
        if self.day > days_in_month:
            self.day = 1; self.month += 1
            if self.month > 12: self.month = 1; self.year += 1

        # Apply daily population growth
        for p in self.prefectures:
            p.update_daily_population()

        # Apply slight daily drift/changes to other stats (optional)
        for p in self.prefectures:
            p.approval += random.uniform(-0.1, 0.1) # Random drift
            p.economy += random.uniform(-0.005, 0.005)
            p.unemployment += random.uniform(-0.01, 0.01)
            p.normalize_values()

        # Recalculate global approval after drift
        self.pm.calculate_global_approval(self.prefectures)

        # Check for random events (which includes election check)
        event_type, event_name = self.random_event()

        # Record history (only if not handled by election logic above)
        if self.election_in_progress is None:
            try:
                 current_date = datetime.date(self.year, self.month, self.day)
            except ValueError: # Handle invalid dates like Feb 30
                 # Attempt to fix the date, e.g., go to last valid day of previous month? Or first of current?
                 try:
                     current_date = datetime.date(self.year, self.month, self.day - 1) # Try previous day
                 except ValueError:
                     current_date = datetime.date(self.year, self.month, 1) # Fallback

            self.approval_history.append(self.pm.global_approval)
            self.approval_dates.append(current_date)


        # Final check (mainly for game over state after events/voting)
        if not self.running: return None, None # Ensure game over state stops further processing

        return event_type, event_name


    # ** NEW: Election attack phase logic **
    def handle_election_attacks(self):
        """Simulates rival attacks during the election campaign."""
        if not self.running: return

        total_approval_hit = 0
        self.election_attack_messages = ["Election Attack Phase! Rivals respond:"] # Reset messages

        for rival in self.rivals:
            message, impact = rival.generate_attack()
            self.election_attack_messages.append(f"- {message} (Impact: ~{impact:.1f}%)")
            total_approval_hit += impact

        # Apply the hit - reduce global approval and slightly randomized local approval
        print(f"Total calculated attack impact: {total_approval_hit:.2f}%") # Debug
        # Make the hit slightly variable
        actual_hit = total_approval_hit * random.uniform(0.8, 1.2)
        print(f"Actual approval hit applied: {actual_hit:.2f}%") # Debug

        # Apply hit locally with variation
        for p in self.prefectures:
             local_hit_factor = random.uniform(0.7, 1.3)
             p.approval -= actual_hit * local_hit_factor
             p.normalize_values()

        # Recalculate precise global approval after local hits
        self.pm.calculate_global_approval(self.prefectures)

        self.events.append("Election: Rivals launch attacks!")
        # The messages stored in self.election_attack_messages will be shown by the App


    # ** NEW: Election voting logic (separated from check) **
    def handle_election_voting(self):
        """Counts votes and determines election outcome."""
        if not self.running: return

        votes_to_keep = 0
        votes_to_oust = 0
        total_prefectures = len(self.prefectures)

        for prefecture in self.prefectures:
            if prefecture.approval >= 50.0:
                votes_to_keep += 1
            else:
                votes_to_oust += 1

        print(f"Election Voting Results: Keep: {votes_to_keep}, Oust: {votes_to_oust}") # Debug

        # PM loses if more than half vote to oust
        if votes_to_oust > total_prefectures / 2:
            self.running = False # Set game state to over
            self.game_over_reason = (f"Lost Election!\n"
                                     f"Final Vote: Keep {votes_to_keep}, Oust {votes_to_oust}. "
                                     f"({votes_to_oust}/{total_prefectures} prefectures voted against you).")
            self.events.append("Election Result: Lost!")
            print("Election Lost!") # Debug
        else:
             # PM survives the election
             self.events.append("Election Result: Survived!")
             # Store message to be shown by App
             self.election_survival_message = (f"Election Survived!\n"
                                               f"Votes to Keep: {votes_to_keep}\n"
                                               f"Votes to Oust: {votes_to_oust}\n"
                                               f"Your position is secure... for now.")
             # Optional: Small approval boost for surviving?
             boost = random.uniform(1.0, 4.0)
             for p in self.prefectures:
                 p.approval += boost
                 p.normalize_values()
             self.pm.calculate_global_approval(self.prefectures)
             self.events.append(f"Approval boosted slightly after surviving election (+{boost:.1f}% approx).")


    # ** MODIFIED: Election check only triggers the process **
    def check_for_election(self):
        """Checks if global approval triggers an election."""
        if not self.running or self.election_in_progress: return # Don't trigger if game over or election already happening

        election_threshold = 30.0 # ** CHANGED THRESHOLD **
        if self.pm.global_approval < election_threshold:
            self.election_in_progress = 'triggered'
            print(f"Approval dropped to {self.pm.global_approval:.2f}%, election process triggered!") # Debug
            self.events.append(f"Approval below {election_threshold}%! Election Triggered!")
            # Message will be shown by App based on state change


    def skip_year(self):
        """Skip ahead by one year, simulating daily changes."""
        if not self.running or self.election_in_progress:
             print("Cannot skip year while game is over or election is in progress.")
             return self.running

        original_date_str = f"{self.day}/{self.month}/{self.year}"
        num_days_to_skip = 365 # Approximate a year

        for i in range(num_days_to_skip):
            # --- Simulate one day ---
            if self.election_in_progress == 'triggered':
                self.election_in_progress = 'attack_phase'
                self.handle_election_attacks()
            elif self.election_in_progress == 'attack_phase':
                self.election_in_progress = 'voting_day'
            elif self.election_in_progress == 'voting_day':
                self.handle_election_voting()
                self.election_in_progress = None
                if not self.running: # Check if game ended after voting
                     final_date = (datetime.date(self.year, self.month, self.day) + datetime.timedelta(days=i+1))
                     self.year, self.month, self.day = final_date.year, final_date.month, final_date.day
                     print(f"Game ended during year skip (election) on {self.day}/{self.month}/{self.year}")
                     self.approval_history.append(self.pm.global_approval); self.approval_dates.append(final_date)
                     return False # Stop skipping

            # Apply daily growth if no election is happening or after it resolves
            if self.election_in_progress is None:
                for p in self.prefectures: p.update_daily_population()

            # Apply drift/changes
            for p in self.prefectures:
                p.approval += random.uniform(-0.15, 0.15) # Slightly larger drift for skips
                p.normalize_values()
            self.pm.calculate_global_approval(self.prefectures)

            # Higher chance of random event during skip
            if random.random() < 0.05: # 5% chance per skipped day
                self.random_event()
                if not self.running: # Check if event caused game over
                    final_date = (datetime.date(self.year, self.month, self.day) + datetime.timedelta(days=i+1))
                    self.year, self.month, self.day = final_date.year, final_date.month, final_date.day
                    print(f"Game ended during year skip (event) on {self.day}/{self.month}/{self.year}")
                    self.approval_history.append(self.pm.global_approval); self.approval_dates.append(final_date)
                    return False # Stop skipping

            # Record approval periodically during skip for graph
            if (i + 1) % 30 == 0: # Record roughly monthly
                interim_date = (datetime.date(self.year, self.month, self.day) + datetime.timedelta(days=i+1))
                self.approval_history.append(self.pm.global_approval)
                # Ensure date is valid before appending
                try: valid_date = datetime.date(interim_date.year, interim_date.month, interim_date.day)
                except ValueError: continue # Skip if date becomes invalid during skip
                self.approval_dates.append(valid_date)

        # Update final date after skip completes successfully
        final_date = (datetime.date(self.year, self.month, self.day) + datetime.timedelta(days=num_days_to_skip))
        self.year, self.month, self.day = final_date.year, final_date.month, final_date.day

        # Add final data point
        self.approval_history.append(self.pm.global_approval)
        self.approval_dates.append(final_date)

        # Final check for election trigger after skip (if still running)
        if self.running: self.check_for_election()

        print(f"Skipped from {original_date_str} to {self.day}/{self.month}/{self.year}")
        return self.running

    # ** MODIFIED: Return prefecture data including growth rate **
    def get_prefecture_data(self):
        """Return data about all prefectures for display"""
        return [(p.name, p.get_population_int(), p.economy, p.approval, p.unemployment,
                 p.gdp, p.get_gdp_per_capita(), p.population_growth_rate)
                for p in self.prefectures]

    def get_recent_events(self):
        return self.events

    def calculate_final_score(self):
        if not self.approval_history: return 0.0
        return sum(self.approval_history) / len(self.approval_history)


class JapanPMSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nihon Seiji 伝説 (Japan Politics Legend)")
        self.root.geometry("900x750")
        self.root.configure(bg="#f0f0f8")

        # Font setup (remains the same)
        default_font = tk.font.nametofont("TkDefaultFont"); default_font.configure(family="Arial Unicode MS", size=10)
        text_font = tk.font.nametofont("TkTextFont"); text_font.configure(family="Arial Unicode MS", size=10)
        fixed_font = tk.font.nametofont("TkFixedFont"); fixed_font.configure(family="Arial Unicode MS", size=10)
        self.root.option_add("*Font", default_font)

        self.simulation = None
        self.prefecture_window_open = False # Flag to track if prefecture window is open

        self.show_welcome_screen()

    def show_welcome_screen(self):
        # If coming from a game over state, show the reason and score first
        if hasattr(self, 'simulation') and self.simulation and not self.simulation.running:
             # Check if game over screen was already shown
             if not hasattr(self, 'game_over_shown') or not self.game_over_shown:
                 self.show_game_over_screen()
                 return # Stop here, game over screen handles next steps
             # else: game over already acknowledged, proceed to clear screen

        # Reset game over flag if moving to welcome screen
        self.game_over_shown = False

        for widget in self.root.winfo_children():
            widget.destroy()

        # ... (Welcome screen UI setup remains the same) ...
        welcome_frame = tk.Frame(self.root, bg="#f0f0f8", padx=20, pady=20); welcome_frame.pack(expand=True)
        title_label = tk.Label(welcome_frame, text="日本首相シミュレーター", font=("Arial Unicode MS", 32, "bold"), bg="#f0f0f8"); title_label.pack(pady=10)
        subtitle_label = tk.Label(welcome_frame, text="Japan Prime Minister Simulator", font=("Arial Unicode MS", 18), bg="#f0f0f8"); subtitle_label.pack(pady=10)
        info_frame = tk.Frame(welcome_frame, bg="#f0f0f8", pady=20); info_frame.pack()
        tk.Label(info_frame, text="Your Name:", font=("Arial Unicode MS", 12), bg="#f0f0f8").grid(row=0, column=0, sticky="e", pady=5)
        self.name_entry = tk.Entry(info_frame, font=("Arial Unicode MS", 12), width=25); self.name_entry.grid(row=0, column=1, sticky="w", pady=5); self.name_entry.insert(0, DEFAULT_PM_NAME)
        tk.Label(info_frame, text="Party Name:", font=("Arial Unicode MS", 12), bg="#f0f0f8").grid(row=1, column=0, sticky="e", pady=5)
        self.party_entry = tk.Entry(info_frame, font=("Arial Unicode MS", 12), width=25); self.party_entry.grid(row=1, column=1, sticky="w", pady=5); self.party_entry.insert(0, DEFAULT_PARTY_NAME)
        button_frame = tk.Frame(welcome_frame, bg="#f0f0f8", pady=20); button_frame.pack()
        new_game_btn = tk.Button(button_frame, text="Start New Game", font=("Arial", 12), command=self.start_new_game, bg="#4CAF50", fg="white", padx=20, pady=10); new_game_btn.grid(row=0, column=0, padx=10)
        load_game_btn = tk.Button(button_frame, text="Load Game", font=("Arial", 12), command=self.load_game, bg="#2196F3", fg="white", padx=20, pady=10); load_game_btn.grid(row=0, column=1, padx=10)
        quit_btn = tk.Button(button_frame, text="Quit", font=("Arial", 12), command=self.quit_game, bg="#f44336", fg="white", padx=20, pady=10); quit_btn.grid(row=0, column=2, padx=10)


    def show_country_stats(self):
        if not self.simulation:
            messagebox.showerror("Error", "No simulation running.")
            return

        stats = self.simulation.stats
        prefectures = self.simulation.prefectures

        # Calculate dynamic totals/averages using integer population
        total_pop = sum(p.get_population_int() for p in prefectures)
        total_gdp_nominal = sum(p.gdp for p in prefectures)

        stats.demographics['population'] = total_pop
        stats.economy['gdp_nominal'] = total_gdp_nominal
        stats.economy['gdp_per_capita'] = (total_gdp_nominal * 1_000_000_000) / total_pop if total_pop > 0 else 0
        # Calculate average growth rate (weighted by population)
        if total_pop > 0:
             weighted_growth_sum = sum(p.get_population_int() * p.population_growth_rate for p in prefectures)
             avg_growth_rate = weighted_growth_sum / total_pop
        else: avg_growth_rate = 0


        # --- Calculate Rankings ---
        pop_sorted = sorted(prefectures, key=lambda p: p.get_population_int(), reverse=True)
        top_5_pop = [(p.name, p.get_population_int()) for p in pop_sorted[:5]]
        gdp_sorted = sorted(prefectures, key=lambda p: p.gdp, reverse=True)
        top_5_gdp = [(p.name, p.gdp) for p in gdp_sorted[:5]]
        gdp_pc_sorted = sorted(prefectures, key=lambda p: p.get_gdp_per_capita(), reverse=True)
        top_5_gdp_pc = [(p.name, p.get_gdp_per_capita()) for p in gdp_pc_sorted[:5]]
        growth_sorted = sorted(prefectures, key=lambda p: p.population_growth_rate, reverse=True) # Highest growth first
        top_5_growth = [(p.name, p.population_growth_rate) for p in growth_sorted[:5]]
        bottom_5_growth = [(p.name, p.population_growth_rate) for p in growth_sorted[-5:]] # Lowest growth


        # --- Format Message ---
        msg = (
            f"--- Economy (National Estimates) ---\n"
            f"GDP (Nominal): ${stats.economy['gdp_nominal']:.1f} Billion USD (Calculated Total)\n"
            f"GDP per Capita: ${stats.economy['gdp_per_capita']:,.0f} USD (Calculated Average)\n"
            f"Inflation: {stats.economy['inflation']:.1f}% (Estimate)\n"
            f"Growth Rate: {stats.economy['growth_rate']:.1f}% (Estimate)\n"
            f"\n--- Top 5 Prefectures by GDP (B USD) ---\n" + "\n".join([f"  {i+1}. {name}: {gdp:.1f}" for i, (name, gdp) in enumerate(top_5_gdp)]) +
            f"\n--- Top 5 Prefectures by GDP per Capita (USD) ---\n" + "\n".join([f"  {i+1}. {name}: ${gdp_pc:,.0f}" for i, (name, gdp_pc) in enumerate(top_5_gdp_pc)]) +
            f"\n\n--- Demographics (National Estimates) ---\n"
            f"Population: {stats.demographics['population']:,}\n"
            f"Avg Pop. Growth Rate: {avg_growth_rate:+.2f}% (Calculated Weighted Avg)\n" # Added avg growth
            f"Density: {stats.demographics['density']:.1f} per km² (Estimate)\n"
            f"Birth Rate: {stats.demographics['birth_rate']:.1f} per 1000 (Estimate)\n"
            f"\n--- Top 5 Prefectures by Population ---\n" + "\n".join([f"  {i+1}. {name}: {pop:,}" for i, (name, pop) in enumerate(top_5_pop)]) +
            f"\n--- Top 5 Prefectures by Pop. Growth Rate (%) ---\n" + "\n".join([f"  {i+1}. {name}: {gr:+.2f}%" for i, (name, gr) in enumerate(top_5_growth)]) +
            f"\n--- Bottom 5 Prefectures by Pop. Growth Rate (%) ---\n" + "\n".join([f"  {i+len(prefectures)-4}. {name}: {gr:+.2f}%" for i, (name, gr) in enumerate(reversed(bottom_5_growth))]) + # Show lowest growth
            f"\n\n--- Immigration (Estimates) ---\n" # Immigration section remains same
            f"Total Foreigners: {stats.demographics['immigration']['total_foreigners']:,}\n"
            f"Immigration Rate: {stats.demographics['immigration']['immigration_rate']:.1f}% growth\n"
            f"Top Source Countries:\n" + "\n".join([f"  {name}: {num:,}" for name, num in stats.demographics['immigration']['source_countries']])
        )
        messagebox.showinfo("Country Statistics", msg)


    def skip_year(self):
        if not self.simulation or not self.simulation.running: return
        if self.simulation.election_in_progress:
             messagebox.showwarning("Action Blocked", "Cannot skip year during an election.")
             return

        if messagebox.askyesno("Skip One Year",
                              "Are you sure you want to skip ahead one full year?\n\n"
                              "This will simulate daily changes and events, and could trigger an election or end the game."):
            still_running = self.simulation.skip_year()
            if still_running:
                messagebox.showinfo("Time Advanced",
                                f"One year has passed. The date is now {self.simulation.day}/{self.simulation.month}/{self.simulation.year}.")
                self.update_display() # Update display after successful skip
                self.check_election_messages() # Check if election was triggered during skip
            else:
                # Game ended during the skip, show game over screen
                self.show_game_over_screen()


    def start_new_game(self):
        pm_name = self.name_entry.get().strip() or DEFAULT_PM_NAME
        party_name = self.party_entry.get().strip() or DEFAULT_PARTY_NAME
        self.simulation = Simulation(fresh=True, pm_name=pm_name, party_name=party_name)
        self.game_over_shown = False # Reset flag for new game
        self.setup_game_screen()

    def load_game(self):
        try:
            slot = simpledialog.askinteger("Load Game", "Enter save slot (1-3):", minvalue=1, maxvalue=3)
            if slot is None: return
            save_file = f"pm_simulator_save_{slot}.pkl"
            if not os.path.exists(save_file):
                messagebox.showerror("Error", f"Save file for slot {slot} not found"); return
            try:
                with open(save_file, "rb") as f: self.simulation = pickle.load(f)
                self.game_over_shown = False # Reset flag on load

                if not self.simulation.running:
                     messagebox.showinfo("Load Complete", f"Game loaded from slot {slot}.\nThis game had already ended.")
                     self.show_game_over_screen()
                else:
                    # ** Check if loaded into an election state **
                    if self.simulation.election_in_progress:
                         messagebox.showinfo("Load Complete", f"Game loaded from slot {slot}.\nAn election is currently in progress!")
                    else:
                         messagebox.showinfo("Load Complete", f"Game loaded from slot {slot}")
                    self.setup_game_screen() # Setup screen even if election is on
                    self.update_display() # Ensure UI reflects loaded state (incl. election)

            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load or interpret save file: {str(e)}"); self.simulation = None; self.show_welcome_screen()
        except Exception as e: messagebox.showerror("Error", f"Failed to load game: {str(e)}")


    def setup_game_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.root.resizable(True, True); self.root.minsize(800, 600)
        main_frame = tk.Frame(self.root, bg="#f0f0f8"); main_frame.pack(fill=tk.BOTH, expand=True)

        # Top info panel (remains same)
        self.info_frame = tk.Frame(main_frame, bg="#e1e1f0", padx=10, pady=10); self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        self.title_label = tk.Label(self.info_frame, text=f"Prime Minister {self.simulation.pm.name} ({self.simulation.pm.party_name})", font=("Arial", 16, "bold"), bg="#e1e1f0"); self.title_label.grid(row=0, column=0, columnspan=2, sticky="w")
        self.date_label = tk.Label(self.info_frame, text=f"Date: {self.simulation.day}/{self.simulation.month}/{self.simulation.year}", font=("Arial", 12), bg="#e1e1f0"); self.date_label.grid(row=1, column=0, sticky="w")
        self.approval_label = tk.Label(self.info_frame, text=f"Approval: {self.simulation.pm.global_approval:.2f}%", font=("Arial", 12), bg="#e1e1f0"); self.approval_label.grid(row=1, column=1, sticky="e")
        # ** NEW: Election Status Label **
        self.election_status_label = tk.Label(self.info_frame, text="", font=("Arial", 12, "bold"), fg="red", bg="#e1e1f0");
        self.election_status_label.grid(row=2, column=0, columnspan=2, sticky="w")


        # Middle section (graph/events - remains same structure)
        middle_frame = tk.Frame(main_frame, bg="#f0f0f8"); middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.graph_frame = tk.Frame(middle_frame, bg="white", bd=2, relief=tk.GROOVE); self.graph_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        event_frame = tk.Frame(middle_frame, bg="white", bd=2, relief=tk.GROOVE, width=300); event_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        middle_frame.grid_columnconfigure(0, weight=7); middle_frame.grid_columnconfigure(1, weight=3); middle_frame.grid_rowconfigure(0, weight=1)
        tk.Label(event_frame, text="Recent Events / Log", font=("Arial", 14, "bold"), bg="white").pack(anchor="w", padx=10, pady=5)
        self.event_listbox = tk.Listbox(event_frame, font=("Arial", 11), height=10, width=35, bd=0, highlightthickness=0); self.event_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Policy buttons section
        policy_frame = tk.Frame(main_frame, bg="#f0f0f8", pady=5); policy_frame.pack(fill=tk.X, padx=10, pady=5)
        btn_frame = tk.Frame(policy_frame, bg="#f0f0f8"); btn_frame.pack()
        btn_width = 15; btn_height = 1; btn_font = ("Arial", 10)

        # ** ADDED new policy button example **
        policy_buttons_config = [
            ("Economy", "economy", "#4CAF50", "white", 0, 0), ("Jobs", "unemployment", "#2196F3", "white", 0, 1),
            ("Welfare", "welfare", "#FF9800", "white", 0, 2), ("Childcare", "childcare_subsidies", "#E91E63", "white", 0, 3), # New Policy
            ("Austerity", "austerity", "#b71c1c", "white", 1, 0), ("Corruption", "corrupt_deal", "#616161", "white", 1, 1),
            ("Nuclear Gamble", "nuclear_energy_gamble", "#fbc02d", "black", 1, 2), ("Tech Gamble", "tech_gamble", "#1976d2", "white", 1, 3),
        ]
        self.policy_buttons = {}
        for text, ptype, bg, fg, r, c in policy_buttons_config:
             btn = tk.Button(btn_frame, text=text, command=lambda pt=ptype: self.policy_action(pt), width=btn_width, height=btn_height, bg=bg, fg=fg, font=btn_font)
             btn.grid(row=r, column=c, padx=3, pady=3)
             self.policy_buttons[ptype] = btn

        # Control buttons (Next Day, Skip Year)
        control_frame = tk.Frame(policy_frame, bg="#f0f0f8"); control_frame.pack(pady=5)
        self.next_day_btn = tk.Button(control_frame, text="Next Day ➡️", command=self.next_day, width=btn_width*2, height=btn_height, bg="#9C27B0", fg="white", font=btn_font); self.next_day_btn.grid(row=0, column=0, padx=3, pady=3)
        self.skip_year_btn = tk.Button(control_frame, text="Skip Year ⏩", command=self.skip_year, width=btn_width*2, height=btn_height, bg="#673AB7", fg="white", font=btn_font); self.skip_year_btn.grid(row=0, column=1, padx=3, pady=3)

        # Bottom Menu (Save, Stats, End Game)
        self.menu_frame = tk.Frame(main_frame, bg="#f0f0f8"); self.menu_frame.pack(fill=tk.X, padx=10, pady=5)
        self.save_btn = tk.Button(self.menu_frame, text="Save Game", command=self.save_game, bg="#673AB7", fg="white", font=("Arial", 10)); self.save_btn.pack(side=tk.LEFT, padx=5)
        self.stats_btn = tk.Button(self.menu_frame, text="Country Stats", command=self.show_country_stats, bg="#607D8B", fg="white", font=("Arial", 10)); self.stats_btn.pack(side=tk.LEFT, padx=5)
        self.end_game_btn = tk.Button(self.menu_frame, text="End Game", command=self.confirm_end_game, bg="#f44336", fg="white", font=("Arial", 10)); self.end_game_btn.pack(side=tk.RIGHT, padx=5)

        self.add_prefecture_button() # Adds prefecture button to menu
        self.create_approval_graph() # Initial graph draw
        self.update_display() # Update all UI elements to reflect initial state


    def create_approval_graph(self):
        # (Graph creation logic remains largely the same as previous step)
        # Ensure it handles potentially empty history gracefully
        # ... (Keep graph code from previous step, including threshold line) ...
        for widget in self.graph_frame.winfo_children(): widget.destroy()
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        approval_data = self.simulation.approval_history if self.simulation else []
        approval_dates = self.simulation.approval_dates if self.simulation else []

        if len(approval_data) > 1:
            min_len = min(len(approval_dates), len(approval_data))
            dates, data = approval_dates[:min_len], approval_data[:min_len]
            if dates and data: # Ensure not empty after slicing
                ax.plot(dates, data, marker='o', markersize=3, linestyle='-', color='#2196F3', linewidth=1.5)
                date_range = max(dates) - min(dates)
                if date_range.days > 730: loc, fmt = mdates.YearLocator(), mdates.DateFormatter('%Y')
                elif date_range.days > 180: loc, fmt = mdates.MonthLocator(interval=3), mdates.DateFormatter('%b %Y')
                elif date_range.days > 30: loc, fmt = mdates.MonthLocator(), mdates.DateFormatter('%b %d')
                else: loc, fmt = mdates.DayLocator(interval=max(1, date_range.days // 5)), mdates.DateFormatter('%b %d')
                ax.xaxis.set_major_locator(loc); ax.xaxis.set_major_formatter(fmt)
                plt.xticks(rotation=30, ha='right')
            else: ax.plot([], []) # Empty plot if data mismatch
        elif approval_data: # Single point
            ax.plot([0], [approval_data[0]], marker='o', linestyle='-', color='#2196F3')
            ax.set_xlim(-0.1, 0.1); ax.set_xticks([0]); ax.set_xticklabels(['Start'])
        else: ax.plot([], []) # No data

        ax.set_title("Approval Rating Over Time", fontsize=12); ax.set_ylabel("Approval (%)")
        ax.grid(True, linestyle='--', alpha=0.7); ax.set_ylim(0, 100)
        # ** MODIFIED: Election threshold line updated **
        ax.axhline(y=30, color='red', linestyle=':', alpha=0.8, linewidth=1.5) # Changed to 30%
        ax.annotate('Election Threshold (30%)', xy=(0.05, 30), xycoords=('axes fraction', 'data'), xytext=(5, 5), textcoords='offset points', fontsize=8, color='red', ha='left')

        plt.tight_layout(pad=1.2)
        canvas = FigureCanvasTkAgg(fig, self.graph_frame); canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True); canvas.draw()


    def update_event_list(self):
        self.event_listbox.delete(0, tk.END)
        if not self.simulation: return
        events = self.simulation.get_recent_events()
        for event in reversed(events): # Show newest first
            self.event_listbox.insert(tk.END, event)


    # ** MODIFIED: update_display handles election state UI **
    def update_display(self):
        if not self.simulation: return

        # Check game state FIRST
        if not self.simulation.running:
            if not self.game_over_shown: self.show_game_over_screen()
            return

        # Update standard labels
        self.date_label.config(text=f"Date: {self.simulation.day}/{self.simulation.month}/{self.simulation.year}")
        self.approval_label.config(text=f"Approval: {self.simulation.pm.global_approval:.2f}%")

        # Update election status label and button states
        election_status_text = ""
        action_button_state = tk.NORMAL
        if self.simulation.election_in_progress == 'triggered':
            election_status_text = "ELECTION TRIGGERED! Attacks tomorrow!"
            action_button_state = tk.DISABLED # Disable actions once triggered
        elif self.simulation.election_in_progress == 'attack_phase':
            election_status_text = "ELECTION: Attack Phase! Voting tomorrow!"
            action_button_state = tk.DISABLED
        elif self.simulation.election_in_progress == 'voting_day':
            election_status_text = "ELECTION: Voting Day! Results soon..."
            action_button_state = tk.DISABLED

        self.election_status_label.config(text=election_status_text)

        # Enable/disable buttons based on election state
        for btn in self.policy_buttons.values():
            if btn: btn.config(state=action_button_state)
        if hasattr(self, 'next_day_btn'): self.next_day_btn.config(state=tk.NORMAL) # Next day always active to advance election
        if hasattr(self, 'skip_year_btn'): self.skip_year_btn.config(state=action_button_state)
        if hasattr(self, 'save_btn'): self.save_btn.config(state=action_button_state) # Prevent saving during election?


        # Update graph and event list (always update)
        self.create_approval_graph()
        self.update_event_list()

        # Update prefecture window if open
        if self.prefecture_window_open:
            self.refresh_prefecture_window_data()


    # ** NEW: Check for and display election-related messages **
    def check_election_messages(self):
        if not self.simulation: return

        # Check for attack messages to display
        if hasattr(self.simulation, 'election_attack_messages') and self.simulation.election_attack_messages:
            attack_summary = "\n".join(self.simulation.election_attack_messages)
            messagebox.showwarning("Election Attacks!", attack_summary)
            self.simulation.election_attack_messages = [] # Clear messages after showing

        # Check for survival message
        if hasattr(self.simulation, 'election_survival_message') and self.simulation.election_survival_message:
            messagebox.showinfo("Election Result", self.simulation.election_survival_message)
            self.simulation.election_survival_message = None # Clear message


    def policy_action(self, policy_type):
        if not self.simulation or not self.simulation.running: return
        if self.simulation.election_in_progress:
            messagebox.showwarning("Action Blocked", "Cannot implement policies during an election.")
            return

        effect, policy_name = self.simulation.make_policy(policy_type)

        # Check if policy itself caused game over (e.g., catastrophic failure, scandal)
        if not self.simulation.running:
             self.show_game_over_screen()
             return

        # Check if policy triggered an election
        if self.simulation.election_in_progress == 'triggered':
             messagebox.showinfo("Election Triggered!", f"Your approval dropped below 30% after implementing {policy_name}, triggering an election!")
             self.update_display() # Update UI to show election status
             # Don't advance day here, let user click Next Day to start attack phase
             return

        # If game still running and no election triggered by policy, proceed to next day
        self.next_day()


    def next_day(self):
        if not self.simulation or not self.simulation.running: return

        event_type, event_name = self.simulation.advance_day()

        # Check game state AFTER advancing day
        if not self.simulation.running:
            self.show_game_over_screen()
            return

        # Handle messages from election state transitions or random events
        if event_type == "election_attack":
             self.check_election_messages() # Show attack popup
        elif event_type == "election_result":
             self.check_election_messages() # Show survival popup
        elif event_type and event_name: # Handle normal random events
            emoji = ""; title = "Event Occurred"
            if event_type == "scandal": emoji = "🔥 "; title="Scandal!"
            elif event_type == "natural_disaster": emoji = "⚠️ "; title="Disaster!"
            elif event_type == "economic_boom": emoji = "📈 "
            elif event_type == "foreign_success": emoji = "🌏 "
            messagebox.showinfo(title, f"{emoji}{event_name}")

        # Check if an election was triggered by the events of the day
        elif self.simulation.election_in_progress == 'triggered':
             messagebox.showinfo("Election Triggered!", "Your approval dropped below 30% due to recent events, triggering an election!")

        # Always update display at the end
        self.update_display()


    def confirm_end_game(self):
        if self.simulation and self.simulation.election_in_progress:
             if not messagebox.askyesno("End Game During Election?",
                                     "An election is in progress! Are you sure you want to concede and end the game now?\n"
                                     "This will count as an election loss."):
                 return # User cancelled
             # If they proceed, end the game with election loss reason
             self.end_game("Conceded during election.")
        elif messagebox.askyesno("End Game", "Are you sure you want to end the current game?\nYour final score will be calculated."):
            self.end_game("Ended game voluntarily.")


    def end_game(self, reason="Game Over"):
        if not self.simulation: return
        self.simulation.running = False
        self.simulation.game_over_reason = reason
        self.show_game_over_screen()


    def show_game_over_screen(self):
        if not self.simulation: self.show_welcome_screen(); return
        if self.game_over_shown: return # Prevent multiple popups/UI updates

        # Disable game controls
        try:
            for btn in self.policy_buttons.values(): btn.config(state=tk.DISABLED)
            self.next_day_btn.config(state=tk.DISABLED)
            self.skip_year_btn.config(state=tk.DISABLED)
            self.end_game_btn.config(text="Return to Menu", command=self.show_welcome_screen)
            self.save_btn.config(state=tk.DISABLED) # Disable saving on game over
            self.stats_btn.config(state=tk.DISABLED) # Disable stats? Maybe allow viewing?
            # Ensure election status label is cleared or shows "Game Over"
            self.election_status_label.config(text="GAME OVER")
        except AttributeError: pass # Widgets might not exist

        final_score = self.simulation.calculate_final_score()
        reason = self.simulation.game_over_reason or "Game Ended"

        # Display final message (only once)
        messagebox.showinfo("Game Over", f"{reason}\n\nFinal Score (Avg. Daily Approval): {final_score:.2f}%")
        self.game_over_shown = True # Set flag to indicate message shown

        # Keep game screen visible, user clicks the modified "Return to Menu" button


    def show_prefecture_data(self):
        if self.prefecture_window_open: return # Prevent opening multiple windows

        self.prefecture_window = tk.Toplevel(self.root)
        self.prefecture_window.title("Japan Prefecture Data")
        self.prefecture_window.geometry("1000x650") # Wider for growth rate
        self.prefecture_window.configure(bg="#f0f0f8")
        self.prefecture_window_open = True

        # Set closing protocol
        self.prefecture_window.protocol("WM_DELETE_WINDOW", self.on_prefecture_window_close)


        title_label = tk.Label(self.prefecture_window, text="Japan Prefecture Data", font=("Arial Unicode MS", 18, "bold"), bg="#f0f0f8"); title_label.pack(pady=10)
        notebook = ttk.Notebook(self.prefecture_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        current_prefecture_data = []
        if self.simulation: current_prefecture_data = self.simulation.get_prefecture_data()
        else: temp_sim = Simulation(fresh=True); current_prefecture_data = temp_sim.get_prefecture_data()

        # Store references to tab objects
        self.pref_data_tab = PrefectureTab(notebook, current_prefecture_data)
        self.pref_analysis_tab = RegionAnalysisTab(notebook, current_prefecture_data)
        self.pref_map_tab = PrefectureMapTab(notebook, current_prefecture_data)

        notebook.add(self.pref_data_tab.frame, text="Prefecture Data")
        notebook.add(self.pref_analysis_tab.frame, text="Regional Analysis")
        notebook.add(self.pref_map_tab.frame, text="Prefecture Map")

        stats_frame = tk.Frame(self.prefecture_window, bg="#e1e1f0", padx=10, pady=5); stats_frame.pack(fill=tk.X, padx=10, pady=5)
        self.pref_stats_label = tk.Label(stats_frame, text="", bg="#e1e1f0", font=("Arial", 10)); self.pref_stats_label.pack(pady=5)
        self.update_prefecture_stats_display(current_prefecture_data) # Initial stats display


        button_frame = tk.Frame(self.prefecture_window, bg="#f0f0f8"); button_frame.pack(pady=10)
        update_btn = tk.Button(button_frame, text="Refresh Data", command=self.refresh_prefecture_window_data, bg="#4CAF50", fg="white"); update_btn.pack(side=tk.LEFT, padx=10)
        if not self.simulation or not self.simulation.running: update_btn.config(state=tk.DISABLED)
        close_btn = tk.Button(button_frame, text="Close", command=self.on_prefecture_window_close, bg="#f44336", fg="white"); close_btn.pack(side=tk.LEFT, padx=10)

        self.prefecture_window.resizable(True, True); self.prefecture_window.minsize(950, 600)

    # ** NEW: Method to specifically update data in the open prefecture window **
    def refresh_prefecture_window_data(self):
         if not self.prefecture_window_open or not self.simulation or not self.simulation.running:
             # Maybe disable the button instead of showing a message here
             # messagebox.showinfo("Update Info", "Prefecture window not open or no active game.")
             return

         new_data = self.simulation.get_prefecture_data()
         # Update tabs using stored references
         if hasattr(self, 'pref_data_tab'): self.pref_data_tab.update_data(new_data)
         if hasattr(self, 'pref_analysis_tab'): self.pref_analysis_tab.update_data(new_data)
         if hasattr(self, 'pref_map_tab'): self.pref_map_tab.update_data(new_data)
         # Update stats bar
         self.update_prefecture_stats_display(new_data)


    # ** NEW: Helper to update stats bar in prefecture window **
    def update_prefecture_stats_display(self, data):
         if not hasattr(self, 'pref_stats_label'): return # Check if label exists

         pop_values = [d[1] for d in data if d[1] is not None]
         approval_values = [d[3] for d in data if d[3] is not None]
         unemployment_values = [d[4] for d in data if d[4] is not None]
         gdp_values = [d[5] for d in data if d[5] is not None]
         growth_values = [d[7] for d in data if len(d) > 7 and d[7] is not None] # Check index

         total_pop = sum(pop_values)
         avg_approval = sum(approval_values) / len(approval_values) if approval_values else 0
         avg_unemployment = sum(unemployment_values) / len(unemployment_values) if unemployment_values else 0
         total_gdp = sum(gdp_values)
         avg_growth = sum(growth_values) / len(growth_values) if growth_values else 0 # Simple average for display

         stats_text = (f"Total Pop: {total_pop:,} | Avg Approval: {avg_approval:.1f}% | "
                       f"Avg Unemployment: {avg_unemployment:.1f}% | Total GDP: ${total_gdp:.1f}B | Avg Growth: {avg_growth:+.2f}%")
         self.pref_stats_label.config(text=stats_text)

    # ** NEW: Handle prefecture window closing **
    def on_prefecture_window_close(self):
        self.prefecture_window_open = False
        if hasattr(self, 'prefecture_window'): # Check if window exists
             try: self.prefecture_window.destroy()
             except tk.TclError: pass # Ignore error if already destroyed
        self.prefecture_window = None # Clear reference

    def add_prefecture_button(self):
        if hasattr(self, 'menu_frame'):
            prefecture_btn = tk.Button(self.menu_frame, text="Prefecture Data", command=self.show_prefecture_data, bg="#009688", fg="white", font=("Arial", 10))
            prefecture_btn.pack(side=tk.LEFT, padx=5)
            if hasattr(self, 'end_game_btn'): # Ensure End Game stays right
                self.end_game_btn.pack_forget(); self.end_game_btn.pack(side=tk.RIGHT, padx=5)

    def save_game(self):
        if not self.simulation: messagebox.showerror("Error", "No game running to save."); return
        if self.simulation.election_in_progress:
             messagebox.showwarning("Save Blocked", "Cannot save during an election.")
             return
        # if not self.simulation.running: messagebox.showwarning("Save Info", "Cannot save ended game."); return

        try:
            slot = simpledialog.askinteger("Save Game", "Enter save slot (1-3):", minvalue=1, maxvalue=3)
            if slot is None: return
            save_file = f"pm_simulator_save_{slot}.pkl"
            try:
                with open(save_file, "wb") as f: pickle.dump(self.simulation, f)
                messagebox.showinfo("Save Complete", f"Game saved to slot {slot}")
            except Exception as e: messagebox.showerror("Save Error", f"Could not save game data: {str(e)}")
        except Exception as e: messagebox.showerror("Error", f"Failed to save game: {str(e)}")


    def quit_game(self):
        # Close prefecture window if open
        if self.prefecture_window_open: self.on_prefecture_window_close()

        if self.simulation and self.simulation.running:
             if messagebox.askyesno("Quit", "A game is running. Are you sure you want to quit?\n(Unsaved progress will be lost)"):
                 self.root.destroy()
        else:
             if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
                 self.root.destroy()

def main():
    root = tk.Tk()
    # Font/DPI/Encoding settings (keep as is)
    if hasattr(sys, 'getwindowsversion'):
        try: from ctypes import windll; windll.shcore.SetProcessDpiAwareness(1)
        except: pass
        try: import ctypes; ctypes.windll.kernel32.SetConsoleCP(65001); ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        except: pass
    app = JapanPMSimulatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
