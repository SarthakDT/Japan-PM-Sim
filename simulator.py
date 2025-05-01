# main.py
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

DEFAULT_PM_NAME = "Shigeru Ishiba"
DEFAULT_PARTY_NAME = "Liberal Democratic Party"

class Prefecture:
    def __init__(self, name, population=None):
        self.name = name
        # Use provided population or fallback to a scaled default
        self.population = population if population is not None else random.randint(1000000, 10000000)
        self.economy = random.uniform(0.5, 1.5)  # Random economic score
        self.approval = random.uniform(40.0, 60.0)  # Random approval rating
        self.unemployment = random.uniform(3.0, 10.0)  # Random unemployment rate
        self.environment = random.uniform(3.0, 10.0)  # Random environmental score
    
    def normalize_values(self):
        """Ensure all values are within valid ranges"""
        self.approval = min(100, max(0, self.approval))
        self.unemployment = min(30, max(1, self.unemployment))
        self.environment = min(10, max(0, self.environment))
        self.economy = min(3, max(0.1, self.economy))

class PrimeMinister:
    def __init__(self, name, party_name):
        self.name = name
        self.party_name = party_name
        self.global_approval = 50.0  # Start with 50% approval rating
        self.base_popularity = random.uniform(50.0, 70.0)  # Base popularity
        
        # Policy effectiveness attributes
        self.economy_skill = random.uniform(0.5, 1.5)
        self.unemployment_skill = random.uniform(0.5, 1.5)
        self.environment_skill = random.uniform(0.5, 1.5)
        self.welfare_skill = random.uniform(0.5, 1.5)
        
    def calculate_global_approval(self, prefectures):
        # Calculate global approval based on prefecture averages
        total_approval = 0
        total_population = 0
        
        for prefecture in prefectures:
            total_approval += prefecture.approval * prefecture.population
            total_population += prefecture.population
            
        if total_population > 0:
            self.global_approval = min(100, max(0, (total_approval / total_population)))
        return self.global_approval

class RivalParty:
    def __init__(self, name):
        self.name = name
        self.base_popularity = random.uniform(40.0, 60.0)  # Rival's base popularity

class CountryStatistics:
    def __init__(self):
        # Economy data (real current values)
        self.economy = {
            'gdp_ppp': 6.31,  # $ trillion
            'gdp_nominal': 4.204,  # $ trillion
            'gdp_per_capita': 36990.33,  # USD
            'inflation': 3.2,  # % (March 2025)
            'growth_rate': 0.9,  # % (2025 projection)
            'top_prefectures_gdp': [
                ("Tokyo", 74003),
                ("Aichi", 52119),
                ("Ibaraki", 46594),
                ("Tochigi", 46086),
                ("Shiga", 45952)
            ]  # USD PPP
        }
        # Demographics data (real current values)
        self.demographics = {
            'population': 125921755,
            'density': 333.2,  # per km²
            'migration_rate': 0.08,  # %
            'birth_rate': 5.7,  # per 1000
            'top_prefectures_pop': [
                ("Tokyo", 13834925),
                ("Kanagawa", 9209442),
                ("Osaka", 8849635),
                ("Aichi", 7575530),
                ("Saitama", 7390054)
            ],
            'immigration': {
                'total_foreigners': 3768977,
                'source_countries': [
                    ("China", 873286),
                    ("Vietnam", 634361),
                    ("South Korea", 409238),
                    ("Nepal", 124356),  # Added specific value
                    ("Brazil", 206886)  # Added specific value
                ],
                'immigration_rate': 10.5  # % growth (2024)
            }
        }

class PrefectureTab:
    """A container for prefecture data tab in the notebook"""
    def __init__(self, parent, prefecture_data):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.prefecture_data = prefecture_data
        self.setup_ui()
        
    def setup_ui(self):
        # Setup sorter and filters at the top
        sort_frame = tk.Frame(self.frame, bg="#f0f0f8")
        sort_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(sort_frame, text="Sort by:", bg="#f0f0f8").pack(side=tk.LEFT, padx=5)
        sort_options = ["Prefecture Name", "Population", "Economy", "Approval Rating", "Unemployment Rate", "Environment Score"]
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
        
        # Create treeview
        columns = ("name", "population", "economy", "approval", "unemployment", "environment")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                          yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Define column headings
        self.tree.heading("name", text="Prefecture", command=lambda: self.sort_treeview("name", False))
        self.tree.heading("population", text="Population", command=lambda: self.sort_treeview("population", True))
        self.tree.heading("economy", text="Economy", command=lambda: self.sort_treeview("economy", True))
        self.tree.heading("approval", text="Approval %", command=lambda: self.sort_treeview("approval", True))
        self.tree.heading("unemployment", text="Unemployment %", command=lambda: self.sort_treeview("unemployment", True))
        self.tree.heading("environment", text="Environment", command=lambda: self.sort_treeview("environment", True))
        
        # Set column widths
        self.tree.column("name", width=120, anchor=tk.W)
        self.tree.column("population", width=120, anchor=tk.E)
        self.tree.column("economy", width=80, anchor=tk.E)
        self.tree.column("approval", width=80, anchor=tk.E)
        self.tree.column("unemployment", width=120, anchor=tk.E)
        self.tree.column("environment", width=100, anchor=tk.E)
        
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
        # Determine current sort direction
        if self.sort_var.get() == column:
            self.sort_asc_var.set(not self.sort_asc_var.get())
        else:
            self.sort_var.set(column)
            self.sort_asc_var.set(True)
        
        self.populate_tree()
        
    def populate_tree(self):
        """Populate the treeview with sorted and filtered data"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get sort column
        sort_column = self.sort_var.get()
        column_mapping = {
            "Prefecture Name": 0,
            "Population": 1,
            "Economy": 2,
            "Approval Rating": 3,
            "Unemployment Rate": 4,
            "Environment Score": 5
        }
        sort_idx = column_mapping.get(sort_column, 0)
        
        # Get search filter
        search_text = self.search_entry.get().lower()
        
        # Filter and sort data
        filtered_data = [data for data in self.prefecture_data if search_text in data[0].lower()]
        sorted_data = sorted(filtered_data, 
                           key=lambda x: x[sort_idx], 
                           reverse=not self.sort_asc_var.get())
        
        # Insert data
        for i, data in enumerate(sorted_data):
            name, population, economy, approval, unemployment, environment = data
            formatted_pop = f"{population:,}"  # Add commas for readability
            self.tree.insert("", i, values=(name, formatted_pop, f"{economy:.2f}", 
                                          f"{approval:.1f}%", f"{unemployment:.1f}%", 
                                          f"{environment:.1f}"))
            
    def update_data(self, new_data):
        """Update with new prefecture data"""
        self.prefecture_data = new_data
        self.populate_tree()

class RegionAnalysisTab:
    """A container for region analysis tab in the notebook"""
    def __init__(self, parent, prefecture_data):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.prefecture_data = prefecture_data
        self.setup_ui()
        
    def setup_ui(self):
        # Define regions
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
        display_options = ["Population", "Approval", "Economy", "Unemployment", "Environment"]
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
        # Clear previous charts
        self.fig.clear()
        
        # Get selected display option
        display_type = self.display_var.get()
        
        # Set up subplots
        ax1 = self.fig.add_subplot(121)  # Pie chart
        ax2 = self.fig.add_subplot(122)  # Bar chart
        
        # Process data based on display type
        region_data = {}
        
        # Map display type to data index
        data_idx = {"Population": 1, "Economy": 2, "Approval": 3, "Unemployment": 4, "Environment": 5}
        idx = data_idx.get(display_type, 1)
        
        # Calculate data by region
        for region_name, prefectures in self.regions.items():
            region_prefs = [p for p in self.prefecture_data if p[0] in prefectures]
            
            if region_prefs:
                if display_type == "Population":
                    # Sum population
                    region_data[region_name] = sum(p[idx] for p in region_prefs)
                else:
                    # Calculate population-weighted average for other metrics
                    total_pop = sum(p[1] for p in region_prefs)
                    weighted_avg = sum(p[1] * p[idx] for p in region_prefs) / total_pop if total_pop > 0 else 0
                    region_data[region_name] = weighted_avg
        
        # Sort and prepare data for charts
        sorted_items = sorted(region_data.items(), key=lambda x: x[1], reverse=True)
        labels, values = zip(*sorted_items)
        
        # Create pie chart
        explode = [0.05] * len(labels)  # Add slight explosion effect
        
        if display_type == "Population":
            # Format labels with population values
            formatted_labels = [f"{l}\n({v:,.0f})" for l, v in zip(labels, values)]
            ax1.pie(values, labels=None, autopct='%1.1f%%', startangle=90, 
                  shadow=False, explode=explode)
            title = f"Region {display_type} Distribution"
        else:
            # Format labels with metric values
            unit = "%" if display_type in ["Approval", "Unemployment"] else ""
            formatted_labels = [f"{l}\n({v:.1f}{unit})" for l, v in zip(labels, values)]
            ax1.pie(values, labels=None, autopct='%1.1f%%', startangle=90, 
                  shadow=False, explode=explode)
            title = f"Region {display_type} Distribution"
            
        ax1.axis('equal')
        ax1.set_title(title)
        ax1.legend(labels, loc="center left", bbox_to_anchor=(1, 0.5))
        
        # Create bar chart
        colors = plt.cm.viridis(np.linspace(0, 0.9, len(labels)))
        ax2.bar(labels, values, color=colors)
        
        if display_type == "Population":
            # Format y-axis for population in millions
            ax2.set_ylabel('Population')
            # Format y-axis with millions
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/1000000:.1f}M'))
        else:
            unit = "%" if display_type in ["Approval", "Unemployment"] else ""
            ax2.set_ylabel(f'{display_type} {unit}')
        
        ax2.set_title(f'{display_type} by Region')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        self.fig.tight_layout()
        self.canvas.draw()
        
    def update_data(self, new_data):
        """Update with new prefecture data"""
        self.prefecture_data = new_data
        self.update_chart()

class PrefectureMapTab:
    """A container for prefecture map visualization"""
    def __init__(self, parent, prefecture_data):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.prefecture_data = prefecture_data
        self.setup_ui()
        
    def setup_ui(self):
        # Control frame at top
        control_frame = tk.Frame(self.frame, bg="#f0f0f8")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(control_frame, text="Color by:", bg="#f0f0f8").pack(side=tk.LEFT, padx=5)
        self.color_var = tk.StringVar(value="Approval")
        color_options = ["Approval", "Population", "Economy", "Unemployment", "Environment"]
        color_menu = ttk.Combobox(control_frame, textvariable=self.color_var, 
                                values=color_options, width=15)
        color_menu.pack(side=tk.LEFT, padx=5)
        color_menu.bind("<<ComboboxSelected>>", lambda e: self.draw_map())
        
        # Create canvas for map
        self.canvas = tk.Canvas(self.frame, bg="white", width=600, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Information label
        self.info_label = tk.Label(self.frame, text="Hover over a prefecture to see details", 
                                 bg="#f0f0f8", font=("Arial", 10))
        self.info_label.pack(pady=5)
        
        # Draw the initial map
        self.draw_map()
        
    def draw_map(self):
        """Draw a simplified map of Japan with prefecture data"""
        self.canvas.delete("all")
        
        # Create a simplified map layout
        # This is a stylized representation - not geographically accurate
        
        # Define regions with relative positions
        region_layouts = {
            "Hokkaido": {"x": 450, "y": 50, "width": 120, "height": 100},
            "Tohoku": {"x": 450, "y": 170, "width": 80, "height": 150},
            "Kanto": {"x": 450, "y": 330, "width": 90, "height": 90},
            "Chubu": {"x": 360, "y": 330, "width": 80, "height": 80},
            "Kansai": {"x": 300, "y": 350, "width": 70, "height": 70},
            "Chugoku": {"x": 220, "y": 330, "width": 80, "height": 50},
            "Shikoku": {"x": 240, "y": 400, "width": 70, "height": 40},
            "Kyushu": {"x": 150, "y": 350, "width": 70, "height": 100},
            "Okinawa": {"x": 80, "y": 450, "width": 30, "height": 30}
        }
        
        # Define regions and their prefectures
        regions = {
            "Hokkaido": ["Hokkaido"],
            "Tohoku": ["Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima"],
            "Kanto": ["Ibaraki", "Tochigi", "Gunma", "Saitama", "Chiba", "Tokyo", "Kanagawa"],
            "Chubu": ["Niigata", "Toyama", "Ishikawa", "Fukui", "Yamanashi", "Nagano", "Gifu", "Shizuoka", "Aichi"],
            "Kansai": ["Mie", "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama"],
            "Chugoku": ["Tottori", "Shimane", "Okayama", "Hiroshima", "Yamaguchi"],
            "Shikoku": ["Tokushima", "Kagawa", "Ehime", "Kochi"],
            "Kyushu": ["Fukuoka", "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima"],
            "Okinawa": ["Okinawa"]
        }
        
        # Draw region outlines and fill with colors based on data
        for region_name, layout in region_layouts.items():
            x, y, width, height = layout["x"], layout["y"], layout["width"], layout["height"]
            
            # Get prefectures in this region
            prefecture_names = regions.get(region_name, [])
            prefecture_data_list = [p for p in self.prefecture_data if p[0] in prefecture_names]
            
            # Calculate the average value for the selected metric for this region
            display_type = self.color_var.get()
            data_idx = {"Population": 1, "Economy": 2, "Approval": 3, "Unemployment": 4, "Environment": 5}
            idx = data_idx.get(display_type, 3)  # Default to Approval
            
            if prefecture_data_list:
                if display_type == "Population":
                    # Sum for population
                    total_value = sum(p[idx] for p in prefecture_data_list)
                    # Normalize for coloring (0-1 scale)
                    max_pop = 15000000  # Approximate max population for scaling
                    normalized_value = min(1.0, total_value / max_pop)
                else:
                    # Weighted average for other metrics
                    total_pop = sum(p[1] for p in prefecture_data_list)
                    total_value = sum(p[1] * p[idx] for p in prefecture_data_list) / total_pop if total_pop > 0 else 0
                    
                    # Normalize based on typical ranges
                    if display_type == "Approval":
                        normalized_value = total_value / 100.0  # 0-100%
                    elif display_type == "Economy":
                        normalized_value = total_value / 5.0  # 0-5 scale
                    elif display_type == "Unemployment":
                        normalized_value = 1.0 - (total_value / 30.0)  # Invert: lower is better
                    else:  # Environment
                        normalized_value = total_value / 10.0  # 0-10 scale
            else:
                normalized_value = 0.5  # Default mid-value if no data
                
            # Convert normalized value to color (green for high, red for low)
            # Except unemployment where it's inverted
            if display_type == "Unemployment":
                r = int(255 * normalized_value)
                g = int(255 * (1 - normalized_value))
            else:
                r = int(255 * (1 - normalized_value))
                g = int(255 * normalized_value)
            b = 100
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            # Draw the region rectangle with rounded corners
            region_id = self.canvas.create_rectangle(x, y, x+width, y+height, 
                                                  fill=color, outline="black", width=2)
            
            # Add region name
            self.canvas.create_text(x + width/2, y + height/2, text=region_name, 
                                  font=("Arial", 10, "bold"))
            
            # Bind hover event to show prefecture details
            self.canvas.tag_bind(region_id, "<Enter>", 
                              lambda e, rn=region_name, plist=prefecture_data_list, 
                              dt=display_type, tv=total_value: 
                              self.show_region_info(rn, plist, dt, tv))
            self.canvas.tag_bind(region_id, "<Leave>", self.clear_info)
            
        # Add legend
        self.draw_legend(display_type)
        
    def draw_legend(self, display_type):
        """Draw a color legend for the map"""
        legend_x, legend_y = 50, 50
        legend_width, legend_height = 20, 200
        
        # Draw legend background
        self.canvas.create_rectangle(legend_x, legend_y, 
                                  legend_x + legend_width, legend_y + legend_height,
                                  fill="white", outline="black")
        
        # Draw color gradient
        steps = 20
        for i in range(steps):
            y_step = i * (legend_height / steps)
            value = 1 - (i / steps)  # 1 at top, 0 at bottom
            
            # Same color logic as in draw_map
            if display_type == "Unemployment":
                r = int(255 * value)
                g = int(255 * (1 - value))
            else:
                r = int(255 * (1 - value))
                g = int(255 * value)
            b = 100
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            self.canvas.create_rectangle(legend_x, legend_y + y_step,
                                      legend_x + legend_width, legend_y + y_step + (legend_height / steps),
                                      fill=color, outline="")
        
        # Add labels
        if display_type == "Unemployment":
            top_label = "Low"
            bottom_label = "High"
        else:
            top_label = "High"
            bottom_label = "Low"
            
        self.canvas.create_text(legend_x + legend_width + 10, legend_y, 
                             text=top_label, anchor="w")
        self.canvas.create_text(legend_x + legend_width + 10, legend_y + legend_height, 
                             text=bottom_label, anchor="w")
        
        # Title
        self.canvas.create_text(legend_x + legend_width/2, legend_y - 10, 
                             text=f"{display_type}", anchor="s")
    
    def show_region_info(self, region_name, prefecture_list, display_type, total_value):
        """Display information about the region on hover"""
        if not prefecture_list:
            text = f"{region_name}: No data available"
        else:
            if display_type == "Population":
                formatted_value = f"{total_value:,.0f}"
            elif display_type in ["Approval", "Unemployment"]:
                formatted_value = f"{total_value:.1f}%"
            else:
                formatted_value = f"{total_value:.2f}"
                
            prefectures = ", ".join([p[0] for p in prefecture_list])
            text = f"{region_name} - {display_type}: {formatted_value}\nPrefectures: {prefectures}"
            
        self.info_label.config(text=text)
    
    def clear_info(self, event):
        """Clear the information display"""
        self.info_label.config(text="Hover over a prefecture to see details")
        
    def update_data(self, new_data):
        """Update with new prefecture data"""
        self.prefecture_data = new_data
        self.draw_map()

class Simulation:
    def __init__(self, fresh=True, pm_name=None, party_name=None):
        # Create a population mapping from real data
        self.stats = CountryStatistics()
        prefecture_populations = {}
        
        # Add the top 5 prefectures by population from real data
        for name, pop in self.stats.demographics['top_prefectures_pop']:
            prefecture_populations[name] = pop
        
        # Calculate remaining population to distribute among other prefectures
        remaining_population = self.stats.demographics['population'] - sum(prefecture_populations.values())
        remaining_prefectures = [name for name in PREFECTURE_NAMES if name not in prefecture_populations]
        
        # Distribute remaining population proportionally (with some randomness)
        if remaining_prefectures:
            avg_pop = remaining_population / len(remaining_prefectures)
            for name in remaining_prefectures:
                # Add some variation (±15%)
                prefecture_populations[name] = int(avg_pop * random.uniform(0.85, 1.15))
        
        # Create prefecture objects with real population data
        self.prefectures = [Prefecture(name, prefecture_populations.get(name)) for name in PREFECTURE_NAMES]
        
        # Use provided names or defaults for GUI mode
        if pm_name is None:
            self.pm_name = DEFAULT_PM_NAME
        else:
            self.pm_name = pm_name
            
        if party_name is None:
            self.party_name = DEFAULT_PARTY_NAME
        else:
            self.party_name = party_name
            
        self.pm = PrimeMinister(self.pm_name, self.party_name)
        self.day = 1
        self.month = 1
        self.year = 2025
        self.running = True
        self.pm.calculate_global_approval(self.prefectures)
        self.approval_history = [self.pm.global_approval]
        self.approval_dates = [datetime.date(self.year, self.month, self.day)]
        self.rivals = [
            RivalParty("Constitutional Democratic Party"),
            RivalParty("Democratic Party for the People"),
            RivalParty("Nihon Ishin no Kai"),
        ]
        self.events = []  # Track recent events

    def make_policy(self, policy_type):
        """Make a policy and influence the approval rating (all are now high risk/high reward)"""
        policy_effect = 0
        policy_name = ""
        catastrophic = False

        # Helper: 50/50 chance of positive or negative outcome
        def high_risk_outcome(pos_range, neg_range):
            if random.random() < 0.5:
                return random.uniform(*pos_range), True
            else:
                return -random.uniform(*neg_range), False

        if policy_type == "economy":
            policy_effect, positive = high_risk_outcome((6, 14), (7, 15))
            policy_name = random.choice([
                "Economic Stimulus Package",
                "Industrial Development Plan",
                "Trade Expansion Initiative",
                "Foreign Investment Promotion"
            ])
            for prefecture in self.prefectures:
                if positive:
                    prefecture.economy += random.uniform(0.15, 0.3)
                    prefecture.approval += random.uniform(4.0, 7.0)
                else:
                    prefecture.economy -= random.uniform(0.12, 0.22)
                    prefecture.approval -= random.uniform(5.0, 10.0)
                prefecture.normalize_values()
            
            # Add these lines for more stat changes:
            self.stats.economy['gdp_nominal'] *= (1.03 if positive else 0.97)
            self.stats.economy['gdp_ppp'] *= (1.025 if positive else 0.98)
            self.stats.economy['gdp_per_capita'] *= (1.02 if positive else 0.985)
            self.stats.economy['growth_rate'] += (0.15 if positive else -0.2)
            self.stats.economy['inflation'] += (-0.1 if positive else 0.15)
            self.stats.demographics['migration_rate'] += (0.01 if positive else -0.015)

        elif policy_type == "unemployment":
            policy_effect, positive = high_risk_outcome((5, 10), (6, 12))
            policy_name = random.choice([
                "Job Creation Initiative",
                "Workforce Training Program",
                "Small Business Support Act",
                "Employment Subsidy Program"
            ])
            for prefecture in self.prefectures:
                if positive:
                    prefecture.unemployment -= random.uniform(1.5, 3.0)
                    prefecture.approval += random.uniform(3.0, 7.0)
                else:
                    prefecture.unemployment += random.uniform(1.0, 2.5)
                    prefecture.approval -= random.uniform(4.0, 8.0)
                prefecture.unemployment = max(1.0, prefecture.unemployment)
                prefecture.normalize_values()
            
            # Add these lines for more stat changes:
            self.stats.economy['gdp_per_capita'] *= (1.01 if positive else 0.99)
            self.stats.economy['growth_rate'] += (0.1 if positive else -0.15)
            self.stats.demographics['migration_rate'] += (0.005 if positive else -0.01)

        elif policy_type == "environment":
            policy_effect, positive = high_risk_outcome((4, 9), (5, 11))
            policy_name = random.choice([
                "Green Energy Initiative",
                "National Park Preservation Act",
                "Emissions Reduction Plan",
                "Sustainable Development Program"
            ])
            for prefecture in self.prefectures:
                if positive:
                    prefecture.environment += random.uniform(0.6, 1.2)
                    prefecture.approval += random.uniform(2.0, 6.0)
                else:
                    prefecture.environment -= random.uniform(0.5, 1.0)
                    prefecture.approval -= random.uniform(3.0, 7.0)
                prefecture.normalize_values()
            
            # Add these lines for more stat changes:
            self.stats.economy['gdp_nominal'] *= (1.005 if positive else 0.995)
            self.stats.demographics['migration_rate'] += (0.02 if positive else -0.01)

        elif policy_type == "welfare":
            policy_effect, positive = high_risk_outcome((6, 12), (7, 14))
            policy_name = random.choice([
                "Universal Healthcare Reform",
                "Pension System Overhaul",
                "Social Security Enhancement",
                "Family Support Package"
            ])
            for prefecture in self.prefectures:
                if positive:
                    prefecture.approval += random.uniform(4.0, 8.0)
                    self.stats.demographics['birth_rate'] += 0.2
                else:
                    prefecture.approval -= random.uniform(6.0, 12.0)
                    self.stats.demographics['birth_rate'] -= 0.1
                prefecture.normalize_values()
            
            # Add these lines for more stat changes:
            self.stats.economy['gdp_nominal'] *= (1.01 if positive else 0.99)
            self.stats.economy['gdp_per_capita'] *= (1.005 if positive else 0.995)
            self.stats.demographics['migration_rate'] += (0.015 if positive else -0.02)

        # Negative impact policy
        elif policy_type == "austerity":
            policy_effect, positive = high_risk_outcome((4, 8), (8, 16))
            policy_name = random.choice([
                "Austerity Budget Cuts",
                "Public Sector Layoffs",
                "Welfare Reduction Act"
            ])
            for prefecture in self.prefectures:
                if positive:
                    prefecture.economy += random.uniform(0.05, 0.2)
                    prefecture.unemployment -= random.uniform(0.3, 1.0)
                    prefecture.approval += random.uniform(2.0, 5.0)
                else:
                    prefecture.economy -= random.uniform(0.1, 0.25)
                    prefecture.unemployment += random.uniform(1.0, 2.0)
                    prefecture.approval -= random.uniform(4.0, 8.0)
                prefecture.normalize_values()
            
            # Add these lines for more stat changes:
            self.stats.economy['gdp_nominal'] *= (1.01 if positive else 0.96)
            self.stats.economy['gdp_ppp'] *= (1.01 if positive else 0.97)
            self.stats.economy['inflation'] += (-0.2 if positive else 0.3)
            self.stats.demographics['migration_rate'] += (-0.02 if positive else -0.04)

        elif policy_type == "corrupt_deal":
            policy_effect, positive = high_risk_outcome((3, 8), (8, 16))
            policy_name = random.choice([
                "Secret Corruption Deal",
                "Crony Contract Awarded",
                "Illegal Campaign Funding"
            ])
            for prefecture in self.prefectures:
                if positive:
                    prefecture.approval += random.uniform(1.0, 3.0)
                else:
                    prefecture.approval -= random.uniform(5.0, 10.0)
                prefecture.normalize_values()
            
            # Add these lines for more stat changes:
            self.stats.economy['gdp_nominal'] *= (1.005 if positive else 0.98)
            self.stats.demographics['migration_rate'] += (-0.01 if positive else -0.03)

        # High risk/high reward
        elif policy_type == "nuclear_energy_gamble":
            if random.random() < 0.5:
                policy_effect = random.uniform(12.0, 20.0)
                policy_name = "Nuclear Energy Expansion Success"
                for prefecture in self.prefectures:
                    prefecture.economy += random.uniform(0.3, 0.6)
                    prefecture.environment -= random.uniform(0.1, 0.3)
                    prefecture.approval += random.uniform(7.0, 14.0)
                    prefecture.normalize_values()
                
                # Add these lines for more stat changes:
                self.stats.economy['gdp_nominal'] *= 1.06
                self.stats.economy['gdp_ppp'] *= 1.04
                self.stats.economy['gdp_per_capita'] *= 1.03
                self.stats.economy['growth_rate'] += 0.3
                self.stats.demographics['migration_rate'] += 0.03
            else:
                policy_effect = -random.uniform(15.0, 30.0)
                policy_name = "Nuclear Accident Disaster"
                for prefecture in self.prefectures:
                    prefecture.environment -= random.uniform(2.0, 4.0)
                    prefecture.approval -= random.uniform(12.0, 20.0)
                    prefecture.normalize_values()
                
                # Add these lines for more stat changes:
                self.stats.economy['gdp_nominal'] *= 0.94
                self.stats.economy['gdp_ppp'] *= 0.94
                self.stats.economy['gdp_per_capita'] *= 0.95
                self.stats.demographics['migration_rate'] -= 0.05
                catastrophic = True

        elif policy_type == "tech_gamble":
            if random.random() < 0.3:
                policy_effect = random.uniform(15.0, 25.0)
                policy_name = "AI Tech Revolution"
                for prefecture in self.prefectures:
                    prefecture.economy += random.uniform(0.5, 1.0)
                    prefecture.unemployment -= random.uniform(1.0, 2.0)
                    prefecture.approval += random.uniform(10.0, 16.0)
                    prefecture.normalize_values()
                
                # Add these lines for more stat changes:
                self.stats.economy['gdp_nominal'] *= 1.10
                self.stats.economy['gdp_ppp'] *= 1.08
                self.stats.economy['gdp_per_capita'] *= 1.05
                self.stats.economy['growth_rate'] += 0.5
                self.stats.demographics['migration_rate'] += 0.04
            else:
                policy_effect = -random.uniform(12.0, 20.0)
                policy_name = "Tech Bubble Burst"
                for prefecture in self.prefectures:
                    prefecture.economy -= random.uniform(0.2, 0.5)
                    prefecture.unemployment += random.uniform(1.0, 2.0)
                    prefecture.approval -= random.uniform(8.0, 14.0)
                    prefecture.normalize_values()
                
                # Add these lines for more stat changes:
                self.stats.economy['gdp_nominal'] *= 0.93
                self.stats.economy['gdp_ppp'] *= 0.95
                self.stats.economy['gdp_per_capita'] *= 0.96
                self.stats.economy['growth_rate'] -= 0.3
                self.stats.demographics['migration_rate'] -= 0.02

        self.pm.calculate_global_approval(self.prefectures)
        if catastrophic:
            self.events.append(f"Catastrophe: {policy_name}")
        else:
            self.events.append(f"Implemented {policy_name}")
        return policy_effect, policy_name

    def random_event(self):
        """Random events that affect approval rating"""
        # 20% chance of random event
        if random.random() > 0.2:
            return None, None
            
        event_type = random.choice(["scandal", "natural_disaster", "economic_boom", "foreign_success"])
        event_name = ""
        effect = 0
        
        if event_type == "scandal":
            event_name = random.choice([
                "Cabinet Minister Resignation Scandal",
                "Corruption Allegations Surface",
                "Government Funds Misuse Exposed",
                "Controversial Statement Backlash"
            ])
            effect = -random.uniform(3.0, 8.0)
            
        elif event_type == "natural_disaster":
            event_name = random.choice([
                "Typhoon Strikes Eastern Japan",
                "Earthquake in Kansai Region",
                "Flooding in Northern Prefectures",
                "Volcanic Activity Warning"
            ])
            effect = -random.uniform(2.0, 5.0)
            
        elif event_type == "economic_boom":
            event_name = random.choice([
                "Stock Market Rally",
                "Major Foreign Investment Deal",
                "Tourism Industry Boom",
                "New Technology Sector Growth"
            ])
            effect = random.uniform(3.0, 7.0)
            
        elif event_type == "foreign_success":
            event_name = random.choice([
                "Successful Trade Agreement",
                "Diplomatic Victory at UN",
                "International Peace Initiative",
                "Strategic Alliance Formed"
            ])
            effect = random.uniform(2.0, 6.0)
        
        # Apply effect to prefectures
        for prefecture in self.prefectures:
            # Different prefectures are affected differently
            local_effect = effect * random.uniform(0.7, 1.3)
            prefecture.approval += local_effect
            prefecture.normalize_values()
        
        # Recalculate global approval
        self.pm.calculate_global_approval(self.prefectures)
        
        # Add to events list
        self.events.append(event_name)
        
        if len(self.events) > 5:  # Keep only the 5 most recent events
            self.events.pop(0)
            
        return event_type, event_name
        
    def advance_day(self):
        """Advance the simulation by one day"""
        self.day += 1
        if self.day > 30:
            self.day = 1
            self.month += 1
            if self.month > 12:
                self.month = 1
                self.year += 1
                
        # Check for random events
        event_type, event_name = self.random_event()
        
        # Update approval history
        self.approval_history.append(self.pm.global_approval)
        self.approval_dates.append(datetime.date(self.year, self.month, self.day))
        
        return event_type, event_name
    
    def skip_year(self):
        """Skip ahead by one year in the simulation"""
        original_date = datetime.date(self.year, self.month, self.day)
        
        # Store current date for quarterly data points
        start_year = self.year
        
        # Advance the year
        self.year += 1
        
        # Handle February 29 edge case in leap years
        if self.month == 2 and self.day == 29 and not (self.year % 4 == 0 and (self.year % 100 != 0 or self.year % 400 == 0)):
            self.day = 28
        
        # Generate 4-8 significant events throughout the year
        num_events = random.randint(4, 8)
        for _ in range(num_events):
            event_type, event_name = self.random_event()
        
        # Add quarterly data points for smoother graph - properly spaced through the year
        end_date = datetime.date(self.year, self.month, self.day)
        days_to_add = (end_date - original_date).days
        
        # Add several data points between start and end for a smoother graph
        num_points = min(12, days_to_add // 30)  # At most monthly points, at least quarterly
        
        if num_points > 0:
            days_per_step = days_to_add / (num_points + 1)
            for i in range(1, num_points + 1):
                days_to_add_here = int(i * days_per_step)
                point_date = original_date + datetime.timedelta(days=days_to_add_here)
                
                # Apply some fluctuation to approval for realistic trends
                # Calculate weighted average between original and end approval
                progress = i / (num_points + 1)
                base_approval = (1 - progress) * self.approval_history[0] + progress * self.pm.global_approval
                fluctuation = random.uniform(-3, 3)  # Smaller fluctuation for realistic trends
                self.pm.global_approval = min(100, max(0, base_approval + fluctuation))
                self.approval_history.append(self.pm.global_approval)
                self.approval_dates.append(point_date)
        
        # Add the final point at the new date
        self.approval_history.append(self.pm.global_approval)
        self.approval_dates.append(end_date)
        
        return True
        
    def get_prefecture_data(self):
        """Return data about all prefectures for display"""
        return [(p.name, p.population, p.economy, p.approval, p.unemployment, p.environment) 
                for p in self.prefectures]

    def get_recent_events(self):
        """Get the list of recent events"""
        return self.events

class JapanPMSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nihon Seiji 伝説 (Japan Politics Legend)")
        self.root.geometry("900x750")
        self.root.configure(bg="#f0f0f8")  # Light bluish background
        
        # Configure font that supports Japanese and emoji
        default_font = tk.font.nametofont("TkDefaultFont")
        default_font.configure(family="Arial Unicode MS", size=10)
        text_font = tk.font.nametofont("TkTextFont")
        text_font.configure(family="Arial Unicode MS", size=10)
        fixed_font = tk.font.nametofont("TkFixedFont")
        fixed_font.configure(family="Arial Unicode MS", size=10)
        
        # Apply fonts
        self.root.option_add("*Font", default_font)
        
        # Start with welcome screen
        self.show_welcome_screen()

    def show_welcome_screen(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Welcome frame
        welcome_frame = tk.Frame(self.root, bg="#f0f0f8", padx=20, pady=20)
        welcome_frame.pack(expand=True)
        
        # Game title with proper font
        title_label = tk.Label(welcome_frame, text="日本首相シミュレーター", 
                            font=("Arial Unicode MS", 32, "bold"), bg="#f0f0f8")
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(welcome_frame, text="Japan Prime Minister Simulator", 
                                font=("Arial Unicode MS", 18), bg="#f0f0f8")
        subtitle_label.pack(pady=10)
        
        # Player info frame
        info_frame = tk.Frame(welcome_frame, bg="#f0f0f8", pady=20)
        info_frame.pack()
        
        tk.Label(info_frame, text="Your Name:", font=("Arial Unicode MS", 12), bg="#f0f0f8").grid(row=0, column=0, sticky="e", pady=5)
        self.name_entry = tk.Entry(info_frame, font=("Arial Unicode MS", 12), width=25)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=5)
        self.name_entry.insert(0, DEFAULT_PM_NAME)
        
        tk.Label(info_frame, text="Party Name:", font=("Arial Unicode MS", 12), bg="#f0f0f8").grid(row=1, column=0, sticky="e", pady=5)
        self.party_entry = tk.Entry(info_frame, font=("Arial Unicode MS", 12), width=25)
        self.party_entry.grid(row=1, column=1, sticky="w", pady=5)
        self.party_entry.insert(0, DEFAULT_PARTY_NAME)
        
        # Buttons
        button_frame = tk.Frame(welcome_frame, bg="#f0f0f8", pady=20)
        button_frame.pack()
        
        new_game_btn = tk.Button(button_frame, text="Start New Game", 
                                font=("Arial", 12), command=self.start_new_game,
                                bg="#4CAF50", fg="white", padx=20, pady=10)
        new_game_btn.grid(row=0, column=0, padx=10)
        
        load_game_btn = tk.Button(button_frame, text="Load Game", 
                                 font=("Arial", 12), command=self.load_game,
                                 bg="#2196F3", fg="white", padx=20, pady=10)
        load_game_btn.grid(row=0, column=1, padx=10)
        
        quit_btn = tk.Button(button_frame, text="Quit", 
                           font=("Arial", 12), command=self.quit_game,
                           bg="#f44336", fg="white", padx=20, pady=10)
        quit_btn.grid(row=0, column=2, padx=10)

    def show_country_stats(self):
        stats = self.simulation.stats
        msg = (
            f"--- Economy ---\n"
            f"GDP (PPP): ${stats.economy['gdp_ppp']} trillion\n"
            f"GDP (Nominal): ${stats.economy['gdp_nominal']} trillion\n"
            f"GDP per Capita: ${stats.economy['gdp_per_capita']}\n"
            f"Inflation: {stats.economy['inflation']}%\n"
            f"Growth Rate: {stats.economy['growth_rate']}%\n"
            f"Top Prefectures by GDP:\n" +
            "\n".join([f"  {name}: ${gdp}" for name, gdp in stats.economy['top_prefectures_gdp']]) +
            f"\n\n--- Demographics ---\n"
            f"Population: {stats.demographics['population']}\n"
            f"Density: {stats.demographics['density']} per km²\n"
            f"Migration Rate: {stats.demographics['migration_rate']}%\n"
            f"Birth Rate: {stats.demographics['birth_rate']} per 1000\n"
            f"Top Prefectures by Population:\n" +
            "\n".join([f"  {name}: {pop}" for name, pop in stats.demographics['top_prefectures_pop']]) +
            f"\n\n--- Immigration ---\n"
            f"Total Foreigners: {stats.demographics['immigration']['total_foreigners']}\n"
            f"Immigration Rate: {stats.demographics['immigration']['immigration_rate']}%\n"
            f"Top Source Countries:\n" +
            "\n".join([f"  {name}: {num if num else 'N/A'}" for name, num in stats.demographics['immigration']['source_countries']])
        )
        messagebox.showinfo("Country Statistics", msg)

    def skip_year(self):
        """Skip ahead by one year in the simulation"""
        if messagebox.askyesno("Skip One Year", 
                              "Are you sure you want to skip ahead one full year?\n\n"
                              "This will generate several random events and could significantly "
                              "impact your approval rating."):
            self.simulation.skip_year()
            messagebox.showinfo("Time Advanced", 
                              f"One year has passed. The date is now "
                              f"{self.simulation.day}/{self.simulation.month}/{self.simulation.year}.")
            self.update_display()

    def start_new_game(self):
        pm_name = self.name_entry.get().strip()
        party_name = self.party_entry.get().strip()
        
        if not pm_name:
            pm_name = DEFAULT_PM_NAME
        if not party_name:
            party_name = DEFAULT_PARTY_NAME
            
        self.simulation = Simulation(fresh=True, pm_name=pm_name, party_name=party_name)
        self.setup_game_screen()

    def load_game(self):
        try:
            slot = simpledialog.askinteger("Load Game", "Enter save slot (1-3):",
                                    minvalue=1, maxvalue=3)
            if slot is None: # User canceled
                return
            save_file = f"pm_simulator_save_{slot}.pkl"
            if not os.path.exists(save_file):
                messagebox.showerror("Error", f"Save file for slot {slot} not found")
                return
            try:
                with open(save_file, "rb") as f:
                    self.simulation = pickle.load(f)
                self.setup_game_screen()
                messagebox.showinfo("Load Complete", f"Game loaded from slot {slot}")
            except (IOError, PermissionError) as file_err:
                messagebox.showerror("File Error", f"Could not read save file: {str(file_err)}")
            except (pickle.UnpicklingError, AttributeError, EOFError, ImportError, IndexError) as pickle_err:
                messagebox.showerror("Data Error", f"Save file is corrupted or incompatible: {str(pickle_err)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load game: {str(e)}")

    def setup_game_screen(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Allow window resizing
        self.root.resizable(True, True)
        self.root.minsize(800, 600)
            
        # Main game container
        main_frame = tk.Frame(self.root, bg="#f0f0f8")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top info panel
        self.info_frame = tk.Frame(main_frame, bg="#e1e1f0", padx=10, pady=10)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # PM info
        self.title_label = tk.Label(self.info_frame, 
                                  text=f"Prime Minister {self.simulation.pm.name} ({self.simulation.pm.party_name})", 
                                  font=("Arial", 16, "bold"), bg="#e1e1f0")
        self.title_label.grid(row=0, column=0, columnspan=2, sticky="w")
        
        # Date and approval
        self.date_label = tk.Label(self.info_frame, 
                                 text=f"Date: {self.simulation.day}/{self.simulation.month}/{self.simulation.year}", 
                                 font=("Arial", 12), bg="#e1e1f0")
        self.date_label.grid(row=1, column=0, sticky="w")
        
        self.approval_label = tk.Label(self.info_frame, 
                                     text=f"Approval Rating: {self.simulation.pm.global_approval:.2f}%", 
                                     font=("Arial", 12), bg="#e1e1f0")
        self.approval_label.grid(row=1, column=1, sticky="e")
        
        # Middle section with graph and event log - make it resizable
        middle_frame = tk.Frame(main_frame, bg="#f0f0f8")
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Graph frame
        self.graph_frame = tk.Frame(middle_frame, bg="white", bd=2, relief=tk.GROOVE)
        self.graph_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Event log frame
        event_frame = tk.Frame(middle_frame, bg="white", bd=2, relief=tk.GROOVE, width=300)
        event_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Configure middle frame columns
        middle_frame.grid_columnconfigure(0, weight=7)
        middle_frame.grid_columnconfigure(1, weight=3)
        middle_frame.grid_rowconfigure(0, weight=1)
        
        # Events title
        tk.Label(event_frame, text="Recent Events", font=("Arial", 14, "bold"), 
                bg="white").pack(anchor="w", padx=10, pady=5)
        
        # Event list
        self.event_listbox = tk.Listbox(event_frame, font=("Arial", 11), 
                                      height=10, width=35, bd=0, highlightthickness=0)
        self.event_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Bottom section with policy buttons
        policy_frame = tk.Frame(main_frame, bg="#f0f0f8", pady=5)
        policy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create a frame for policy buttons with 4×2 grid
        btn_frame = tk.Frame(policy_frame, bg="#f0f0f8")
        btn_frame.pack()

        # Define button styles - smaller height for compactness
        btn_width = 15
        btn_height = 1
        btn_font = ("Arial", 10)

        # First row - 4 buttons side-by-side
        economy_btn = tk.Button(btn_frame, text="Economy", 
                            command=lambda: self.policy_action("economy"), width=btn_width, height=btn_height,
                            bg="#4CAF50", fg="white", font=btn_font)
        economy_btn.grid(row=0, column=0, padx=3, pady=3)

        unemployment_btn = tk.Button(btn_frame, text="Jobs", 
                                command=lambda: self.policy_action("unemployment"), width=btn_width, height=btn_height,
                                bg="#2196F3", fg="white", font=btn_font)
        unemployment_btn.grid(row=0, column=1, padx=3, pady=3)

        environment_btn = tk.Button(btn_frame, text="Environment", 
                                command=lambda: self.policy_action("environment"), width=btn_width, height=btn_height,
                                bg="#009688", fg="white", font=btn_font)
        environment_btn.grid(row=0, column=2, padx=3, pady=3)

        welfare_btn = tk.Button(btn_frame, text="Welfare", 
                            command=lambda: self.policy_action("welfare"), width=btn_width, height=btn_height,
                            bg="#FF9800", fg="white", font=btn_font)
        welfare_btn.grid(row=0, column=3, padx=3, pady=3)

        # Second row - 4 buttons side-by-side
        austerity_btn = tk.Button(btn_frame, text="Austerity",
                            command=lambda: self.policy_action("austerity"), width=btn_width, height=btn_height,
                            bg="#b71c1c", fg="white", font=btn_font)
        austerity_btn.grid(row=1, column=0, padx=3, pady=3)

        corrupt_btn = tk.Button(btn_frame, text="Corruption",
                            command=lambda: self.policy_action("corrupt_deal"), width=btn_width, height=btn_height,
                            bg="#616161", fg="white", font=btn_font)
        corrupt_btn.grid(row=1, column=1, padx=3, pady=3)

        nuclear_btn = tk.Button(btn_frame, text="Nuclear",
                            command=lambda: self.policy_action("nuclear_energy_gamble"), width=btn_width, height=btn_height,
                            bg="#fbc02d", fg="black", font=btn_font)
        nuclear_btn.grid(row=1, column=2, padx=3, pady=3)

        tech_btn = tk.Button(btn_frame, text="Tech",
                        command=lambda: self.policy_action("tech_gamble"), width=btn_width, height=btn_height,
                        bg="#1976d2", fg="white", font=btn_font)
        tech_btn.grid(row=1, column=3, padx=3, pady=3)

        # Control buttons frame
        control_frame = tk.Frame(policy_frame, bg="#f0f0f8")
        control_frame.pack(pady=5)

        # Next day and Skip Year buttons side by side
        next_day_btn = tk.Button(control_frame, text="Next Day ➡️", 
                            command=self.next_day, width=btn_width*2, height=btn_height,
                            bg="#9C27B0", fg="white", font=btn_font)
        next_day_btn.grid(row=0, column=0, padx=3, pady=3)

        skip_year_btn = tk.Button(control_frame, text="Skip Year ⏩", 
                            command=self.skip_year, width=btn_width*2, height=btn_height,
                            bg="#673AB7", fg="white", font=btn_font)
        skip_year_btn.grid(row=0, column=1, padx=3, pady=3)

        # Bottom Menu        
        self.menu_frame = tk.Frame(main_frame, bg="#f0f0f8")  # Changed to instance variable
        self.menu_frame.pack(fill=tk.X, padx=10, pady=5)

        save_btn = tk.Button(self.menu_frame, text="Save Game", command=self.save_game,
                  bg="#673AB7", fg="white", font=("Arial", 10))
        save_btn.pack(side=tk.LEFT, padx=5)

        # Country stats button
        stats_btn = tk.Button(self.menu_frame, text="Country Stats", command=self.show_country_stats,
                        bg="#607D8B", fg="white", font=("Arial", 10))
        stats_btn.pack(side=tk.LEFT, padx=5)

        quit_btn = tk.Button(self.menu_frame, text="End Game", command=self.show_welcome_screen,
                        bg="#f44336", fg="white", font=("Arial", 10))
        quit_btn.pack(side=tk.RIGHT, padx=5)

        # Add prefecture data button
        self.add_prefecture_button()
        
        # Create approval graph
        self.create_approval_graph()
        
        # Update event list
        self.update_event_list()

    # Fix for create_approval_graph method in JapanPMSimulatorApp class
    def create_approval_graph(self):
        # Clear any existing graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        # Create figure and plot with proper DPI and size for Tkinter
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        
        # Get approval data and dates
        approval_data = self.simulation.approval_history
        approval_dates = self.simulation.approval_dates

        if len(approval_data) > 1:
            dates = approval_dates
            ax.plot(dates, approval_data, marker='o', markersize=3, linestyle='-', color='#2196F3', linewidth=1.5)
            
            # Format x-axis based on time range
            date_range = max(dates) - min(dates)
            
            if date_range.days > 365:
                # For spans over a year, show only months
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
            elif date_range.days > 90:
                # For spans over 3 months
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
            else:
                # For shorter spans
                days_interval = max(1, date_range.days // 5)
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=days_interval))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
                
            plt.xticks(rotation=0)  # Vertical labels with newlines already in format

        else:
            # Not enough data points yet, use simple indices
            ax.plot([0], [approval_data[0]], marker='o', linestyle='-', color='#2196F3')
            ax.set_xlim(-0.1, 0.1)
            ax.set_xticks([0])
            ax.set_xticklabels(['Start'])
           
        # Style and labels
        ax.set_title("Approval Rating Over Time", fontsize=12)
        ax.set_ylabel("Approval (%)")
        ax.grid(True, linestyle='--', alpha=0.7)
        
        y_min = max(0, min(approval_data) - 10)
        y_max = min(100, max(approval_data) + 10)
        ax.set_ylim(y_min, y_max)
        
        # Add threshold lines
        ax.axhline(y=50, color='gray', linestyle='--', alpha=0.7)
        ax.annotate('50%', xy=(0, 50), xytext=(-25, 0), 
                textcoords='offset points', fontsize=8, color='gray')
                
        # Add padding to prevent cutoff
        plt.tight_layout(pad=1.2)
        
        # Create canvas for the graph
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def update_event_list(self):
        # Clear event list
        self.event_listbox.delete(0, tk.END)
        
        # Add events to list
        events = self.simulation.get_recent_events()
        for event in events:
            self.event_listbox.insert(tk.END, event)
            
        # Always see the most recent event
        if events:
            self.event_listbox.see(tk.END)

    def update_display(self):
        # Update info labels
        self.date_label.config(text=f"Date: {self.simulation.day}/{self.simulation.month}/{self.simulation.year}")
        self.approval_label.config(text=f"Approval Rating: {self.simulation.pm.global_approval:.2f}%")
        
        # Update graph and event list
        self.create_approval_graph()
        self.update_event_list()

    def policy_action(self, policy_type):
        # Implement the policy
        effect, policy = self.simulation.make_policy(policy_type)
        
        # Show appropriate message based on outcome
        if self.simulation.events and "Catastrophe" in self.simulation.events[-1]:
            messagebox.showerror("Policy Disaster", f"Disaster! {policy}\nApproval change: {effect:.2f}%")
        elif effect < 0:
            messagebox.showwarning("Policy Backfired", f"{policy}\nApproval change: {effect:.2f}%")
        else:
            messagebox.showinfo("Policy Implemented", f"You implemented {policy}.\nApproval change: +{effect:.2f}%")
        
        # Advance to the next day after policy implementation
        event_type, event_name = self.simulation.advance_day()
        
        # Handle any random events that occurred on the next day
        if event_type and event_name:
            effect_description = ""
            if event_type == "scandal" or event_type == "natural_disaster":
                emoji = "🔥" if event_type == "scandal" else "⚠️"
                effect_description = "Your approval rating has dropped!"
            else:
                emoji = "📈" if event_type == "economic_boom" else "🌏"
                effect_description = "Your approval rating has increased!"
            messagebox.showinfo("Event Occurred",
                            f"{emoji} {event_name}\n\n{effect_description}")
        
        # Update display with new data
        self.update_display()

    # Remove redundant individual policy methods since we use policy_action for all buttons

    def next_day(self):
        event_type, event_name = self.simulation.advance_day()
        if event_type and event_name:
            effect_description = ""
            if event_type == "scandal" or event_type == "natural_disaster":
                emoji = "🔥" if event_type == "scandal" else "⚠️"
                effect_description = "Your approval rating has dropped!"
            else:
                emoji = "📈" if event_type == "economic_boom" else "🌏"
                effect_description = "Your approval rating has increased!"
            messagebox.showinfo("Event Occurred",
                            f"{emoji} {event_name}\n\n{effect_description}")
        self.update_display()

    def initialize_prefecture_data(self):
        """Initialize prefecture data with real statistics"""
        # Real prefecture data (Name, Population, Economy, Approval, Unemployment, Environment)
        self.prefecture_data = [
            ("Hokkaido", 5250000, 3.8, 55.0, 4.2, 82.5),
            ("Aomori", 1246000, 3.2, 52.3, 4.5, 80.1),
            ("Iwate", 1210000, 3.3, 53.6, 3.9, 83.4),
            ("Miyagi", 2306000, 3.9, 54.1, 3.7, 75.2),
            ("Akita", 966000, 3.1, 50.8, 4.3, 81.3),
            ("Yamagata", 1078000, 3.4, 53.2, 3.6, 82.7),
            ("Fukushima", 1846000, 3.6, 49.5, 3.8, 72.5),
            ("Ibaraki", 2860000, 4.1, 53.8, 3.5, 71.2),
            ("Tochigi", 1934000, 4.0, 54.2, 3.4, 76.8),
            ("Gunma", 1942000, 3.9, 53.9, 3.3, 75.4),
            ("Saitama", 7350000, 4.2, 52.7, 3.6, 68.9),
            ("Chiba", 6259000, 4.3, 53.1, 3.5, 70.2),
            ("Tokyo", 14000000, 5.0, 58.4, 3.2, 65.8),
            ("Kanagawa", 9200000, 4.6, 56.3, 3.4, 69.3),
            ("Niigata", 2223000, 3.7, 54.8, 3.6, 79.7),
            ("Toyama", 1044000, 3.8, 56.2, 3.1, 80.4),
            ("Ishikawa", 1138000, 3.9, 57.1, 3.0, 78.6),
            ("Fukui", 768000, 3.7, 56.9, 3.0, 81.2),
            ("Yamanashi", 811000, 3.6, 53.4, 3.3, 83.9),
            ("Nagano", 2049000, 3.8, 56.3, 3.1, 84.5),
            ("Gifu", 1987000, 3.8, 54.2, 3.2, 78.3),
            ("Shizuoka", 3644000, 4.2, 55.6, 3.1, 77.2),
            ("Aichi", 7552000, 4.5, 56.8, 3.0, 71.8),
            ("Mie", 1781000, 3.9, 54.3, 3.2, 76.1),
            ("Shiga", 1414000, 4.0, 56.1, 3.0, 80.8),
            ("Kyoto", 2583000, 4.1, 57.4, 3.3, 76.5),
            ("Osaka", 8809000, 4.4, 53.2, 3.9, 64.3),
            ("Hyogo", 5466000, 4.2, 54.1, 3.7, 72.1),
            ("Nara", 1331000, 3.8, 53.5, 3.4, 79.3),
            ("Wakayama", 925000, 3.5, 52.8, 3.6, 78.5),
            ("Tottori", 556000, 3.4, 54.3, 3.4, 82.6),
            ("Shimane", 674000, 3.3, 55.1, 3.3, 83.2),
            ("Okayama", 1890000, 3.9, 55.8, 3.2, 77.4),
            ("Hiroshima", 2804000, 4.1, 56.2, 3.3, 75.9),
            ("Yamaguchi", 1358000, 3.7, 53.9, 3.5, 76.8),
            ("Tokushima", 728000, 3.6, 53.2, 3.4, 79.5),
            ("Kagawa", 956000, 3.8, 54.6, 3.3, 76.2),
            ("Ehime", 1339000, 3.7, 53.8, 3.5, 77.3),
            ("Kochi", 698000, 3.4, 52.9, 3.8, 80.1),
            ("Fukuoka", 5104000, 4.2, 56.3, 3.6, 73.2),
            ("Saga", 815000, 3.6, 53.9, 3.4, 78.5),
            ("Nagasaki", 1327000, 3.5, 54.2, 3.5, 79.8),
            ("Kumamoto", 1748000, 3.7, 55.1, 3.3, 80.2),
            ("Oita", 1135000, 3.7, 54.8, 3.4, 78.9),
            ("Miyazaki", 1073000, 3.5, 53.6, 3.6, 81.3),
            ("Kagoshima", 1602000, 3.6, 54.3, 3.5, 80.7),
            ("Okinawa", 1454000, 3.4, 58.2, 3.9, 82.4)
        ]
        return self.prefecture_data

    def show_prefecture_data(self):
        """Open a window showing detailed prefecture data"""
        # Create a new toplevel window
        prefecture_window = tk.Toplevel(self.root)
        prefecture_window.title("Japan Prefecture Data")
        prefecture_window.geometry("900x600")
        prefecture_window.configure(bg="#f0f0f8")
        
        # Add a title
        title_label = tk.Label(prefecture_window, text="Japan Prefecture Data", 
                            font=("Arial Unicode MS", 18, "bold"), bg="#f0f0f8")
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(prefecture_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Get prefecture data (initialize if not already done)
        if not hasattr(self, 'prefecture_data'):
            prefecture_data = self.initialize_prefecture_data()
        else:
            prefecture_data = self.prefecture_data
        
        # Create tabs
        data_tab = PrefectureTab(notebook, prefecture_data)
        analysis_tab = RegionAnalysisTab(notebook, prefecture_data)
        map_tab = PrefectureMapTab(notebook, prefecture_data)
        
        # Add tabs to notebook
        notebook.add(data_tab.frame, text="Prefecture Data")
        notebook.add(analysis_tab.frame, text="Regional Analysis")
        notebook.add(map_tab.frame, text="Prefecture Map")
        
        # Status bar with summary statistics
        stats_frame = tk.Frame(prefecture_window, bg="#e1e1f0", padx=10, pady=5)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Calculate some statistics
        pop_values = [data[1] for data in prefecture_data]
        approval_values = [data[3] for data in prefecture_data]
        unemployment_values = [data[4] for data in prefecture_data]
        
        total_pop = sum(pop_values)
        avg_approval = sum(approval_values) / len(approval_values) if approval_values else 0
        avg_unemployment = sum(unemployment_values) / len(unemployment_values) if unemployment_values else 0
        
        # Display statistics
        stats_label = tk.Label(stats_frame, 
                            text=f"Total Population: {total_pop:,} | Average Approval: {avg_approval:.1f}% | Average Unemployment: {avg_unemployment:.1f}%",
                            bg="#e1e1f0", font=("Arial", 10))
        stats_label.pack(pady=5)
        
        # Update button to refresh with current game data
        def update_prefecture_data():
            if hasattr(self, 'simulation'):
                new_data = self.simulation.get_prefecture_data()
                data_tab.update_data(new_data)
                analysis_tab.update_data(new_data)
                map_tab.update_data(new_data)
                
                # Update statistics
                pop_values = [data[1] for data in new_data]
                approval_values = [data[3] for data in new_data]
                unemployment_values = [data[4] for data in new_data]
                
                total_pop = sum(pop_values)
                avg_approval = sum(approval_values) / len(approval_values) if approval_values else 0
                avg_unemployment = sum(unemployment_values) / len(unemployment_values) if unemployment_values else 0
                
                stats_label.config(text=f"Total Population: {total_pop:,} | Average Approval: {avg_approval:.1f}% | Average Unemployment: {avg_unemployment:.1f}%")
        
        # Buttons frame
        button_frame = tk.Frame(prefecture_window, bg="#f0f0f8")
        button_frame.pack(pady=10)
        
        # Add update button
        update_btn = tk.Button(button_frame, text="Update with Current Game Data", 
                            command=update_prefecture_data, bg="#4CAF50", fg="white")
        update_btn.pack(side=tk.LEFT, padx=10)
        
        # Close button
        close_btn = tk.Button(button_frame, text="Close", 
                            command=prefecture_window.destroy, bg="#f44336", fg="white")
        close_btn.pack(side=tk.LEFT, padx=10)
        
        # Make window resizable
        prefecture_window.resizable(True, True)
        
        # Set minimum size
        prefecture_window.minsize(800, 500)

    def add_prefecture_button(self):
        """Add a button to the game UI to access prefecture data"""
        if hasattr(self, 'menu_frame'):
            prefecture_btn = tk.Button(self.menu_frame, text="Prefecture Data", 
                                command=self.show_prefecture_data,
                                bg="#009688", fg="white", font=("Arial", 10))
            prefecture_btn.pack(side=tk.LEFT, padx=5)

    def save_game(self):
        try:
            slot = simpledialog.askinteger("Save Game", "Enter save slot (1-3):",
                                    minvalue=1, maxvalue=3)
            if slot is None: # User canceled
                return
            save_file = f"pm_simulator_save_{slot}.pkl"
            try:
                with open(save_file, "wb") as f:
                    pickle.dump(self.simulation, f)
                messagebox.showinfo("Save Complete", f"Game saved to slot {slot}")
            except (IOError, PermissionError) as file_err:
                messagebox.showerror("File Error", f"Could not write to save file: {str(file_err)}")
            except (TypeError) as pickle_err:
                messagebox.showerror("Data Error", f"Could not save game data: {str(pickle_err)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save game: {str(e)}")

    def quit_game(self):
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.root.destroy()

def main():
    root = tk.Tk()
    
    # Enable UTF-8 support for emojis and Japanese characters
    if hasattr(sys, 'getwindowsversion'):  # Windows specific
        try:
            # Try to set DPI awareness for better font rendering
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
            
        # Add code to support UTF-8 on Windows
        import ctypes
        ctypes.windll.kernel32.SetConsoleCP(65001)
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    
    app = JapanPMSimulatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
# This code is a simple simulation of a Prime Minister's term in Japan, where the player can make policies, face events, and manage approval ratings.
# It uses Tkinter for the GUI and Matplotlib for plotting approval ratings over time.
