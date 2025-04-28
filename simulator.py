# main.py
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

# Prefecture Data
PREFECTURE_NAMES = [
    "Hokkaido", "Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima", "Ibaraki", "Tochigi", "Gunma", 
    "Saitama", "Chiba", "Tokyo", "Kanagawa", "Niigata", "Toyama", "Ishikawa", "Fukui", "Yamanashi", "Nagano", 
    "Gifu", "Shizuoka", "Aichi", "Mie", "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama", "Tottori", 
    "Shimane", "Okayama", "Hiroshima", "Yamaguchi", "Tokushima", "Kagawa", "Ehime", "Kochi", "Fukuoka", 
    "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima", "Okinawa"
]

DEFAULT_PM_NAME = "Taro Yamada"
DEFAULT_PARTY_NAME = "Progressive Alliance"

class Prefecture:
    def __init__(self, name):
        self.name = name
        self.population = random.randint(1000000, 10000000)  # Random population between 1M and 10M
        self.economy = random.uniform(0.5, 1.5)  # Random economic score
        self.approval = random.uniform(40.0, 60.0)  # Random approval rating
        self.unemployment = random.uniform(3.0, 10.0)  # Random unemployment rate
        self.environment = random.uniform(3.0, 10.0)  # Random environmental score

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
            self.global_approval = (total_approval / total_population)
        return self.global_approval

class RivalParty:
    def __init__(self, name):
        self.name = name
        self.base_popularity = random.uniform(40.0, 60.0)  # Rival's base popularity

class Simulation:
    def __init__(self, fresh=True, pm_name=None, party_name=None):
        self.prefectures = [Prefecture(name) for name in PREFECTURE_NAMES]
        
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
        self.rivals = [
            RivalParty("Liberal Unity Party"),
            RivalParty("Nationalist Front"),
            RivalParty("Green Harmony Movement")
        ]
        self.events = []  # Track recent events

    def make_policy(self, policy_type):
        """Make a policy and influence the approval rating"""
        policy_effect = 0
        policy_name = ""
        
        if policy_type == "economy":
            # Boost the economy with a policy
            policy_effect = random.uniform(2.0, 7.0) * self.pm.economy_skill
            policy_name = random.choice([
                "Economic Stimulus Package",
                "Industrial Development Plan",
                "Trade Expansion Initiative",
                "Foreign Investment Promotion"
            ])
            # Update prefecture economies
            for prefecture in self.prefectures:
                prefecture.economy += random.uniform(0.05, 0.15)
                prefecture.approval += random.uniform(1.0, 3.0)
        
        elif policy_type == "unemployment":
            # Lower unemployment with a policy
            policy_effect = random.uniform(1.5, 5.0) * self.pm.unemployment_skill
            policy_name = random.choice([
                "Job Creation Initiative",
                "Workforce Training Program",
                "Small Business Support Act",
                "Employment Subsidy Program"
            ])
            # Update prefecture unemployment
            for prefecture in self.prefectures:
                prefecture.unemployment -= random.uniform(0.3, 0.8)
                prefecture.unemployment = max(1.0, prefecture.unemployment)  # Can't go below 1%
                prefecture.approval += random.uniform(1.0, 2.5)
        
        elif policy_type == "environment":
            # Implement environmental protection policies
            policy_effect = random.uniform(1.0, 4.0) * self.pm.environment_skill
            policy_name = random.choice([
                "Green Energy Initiative",
                "National Park Preservation Act",
                "Emissions Reduction Plan",
                "Sustainable Development Program"
            ])
            # Update prefecture environment scores
            for prefecture in self.prefectures:
                prefecture.environment += random.uniform(0.2, 0.7)
                prefecture.approval += random.uniform(0.5, 2.0)
        
        elif policy_type == "welfare":
            # Welfare reform policy
            policy_effect = random.uniform(2.0, 6.0) * self.pm.welfare_skill
            policy_name = random.choice([
                "Universal Healthcare Reform",
                "Pension System Overhaul",
                "Social Security Enhancement",
                "Family Support Package"
            ])
            # Update prefecture approvals directly
            for prefecture in self.prefectures:
                prefecture.approval += random.uniform(1.5, 3.5)
        
        # Calculate new global approval
        self.pm.calculate_global_approval(self.prefectures)
        self.approval_history.append(self.pm.global_approval)
        
        # Add to events
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
            
            # Keep approval within bounds
            prefecture.approval = max(0, min(prefecture.approval, 100))
        
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
        
        return event_type, event_name
        
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
        
        # Start with welcome screen
        self.show_welcome_screen()

    def show_welcome_screen(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Welcome frame
        welcome_frame = tk.Frame(self.root, bg="#f0f0f8", padx=20, pady=20)
        welcome_frame.pack(expand=True)
        
        # Game title
        title_label = tk.Label(welcome_frame, text="日本首相シミュレーター", 
                              font=("Arial", 32, "bold"), bg="#f0f0f8")
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(welcome_frame, text="Japan Prime Minister Simulator", 
                                 font=("Arial", 18), bg="#f0f0f8")
        subtitle_label.pack(pady=10)
        
        # Player info frame
        info_frame = tk.Frame(welcome_frame, bg="#f0f0f8", pady=20)
        info_frame.pack()
        
        tk.Label(info_frame, text="Your Name:", font=("Arial", 12), bg="#f0f0f8").grid(row=0, column=0, sticky="e", pady=5)
        self.name_entry = tk.Entry(info_frame, font=("Arial", 12), width=25)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=5)
        self.name_entry.insert(0, "Taro Yamada")
        
        tk.Label(info_frame, text="Party Name:", font=("Arial", 12), bg="#f0f0f8").grid(row=1, column=0, sticky="e", pady=5)
        self.party_entry = tk.Entry(info_frame, font=("Arial", 12), width=25)
        self.party_entry.grid(row=1, column=1, sticky="w", pady=5)
        self.party_entry.insert(0, "Progressive Alliance")
        
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

    def start_new_game(self):
        pm_name = self.name_entry.get().strip()
        party_name = self.party_entry.get().strip()
        
        if not pm_name:
            pm_name = "Taro Yamada"
        if not party_name:
            party_name = "Progressive Alliance"
            
        self.simulation = Simulation(fresh=True, pm_name=pm_name, party_name=party_name)
        self.setup_game_screen()

    def load_game(self):
        try:
            slot = simpledialog.askinteger("Load Game", "Enter save slot (1-3):", 
                                         minvalue=1, maxvalue=3)
            if slot is None:  # User canceled
                return
                
            save_file = f"pm_simulator_save_{slot}.pkl"
            if not os.path.exists(save_file):
                messagebox.showerror("Error", f"Save file for slot {slot} not found")
                return
                
            with open(save_file, "rb") as f:
                self.simulation = pickle.load(f)
            
            self.setup_game_screen()
            messagebox.showinfo("Load Complete", f"Game loaded from slot {slot}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load game: {str(e)}")

    def setup_game_screen(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
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
        
        # Middle section with graph and event log
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
        policy_frame = tk.Frame(main_frame, bg="#f0f0f8", pady=10)
        policy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create a frame for policy buttons with 2x2 grid
        btn_frame = tk.Frame(policy_frame, bg="#f0f0f8")
        btn_frame.pack()
        
        # Policy buttons
        economy_btn = tk.Button(btn_frame, text="Boost Economy 📈", 
                              command=self.boost_economy, width=20, height=2,
                              bg="#4CAF50", fg="white", font=("Arial", 11))
        economy_btn.grid(row=0, column=0, padx=5, pady=5)
        
        unemployment_btn = tk.Button(btn_frame, text="Lower Unemployment 👷", 
                                   command=self.lower_unemployment, width=20, height=2,
                                   bg="#2196F3", fg="white", font=("Arial", 11))
        unemployment_btn.grid(row=0, column=1, padx=5, pady=5)
        
        environment_btn = tk.Button(btn_frame, text="Environmental Policy 🌳", 
                                  command=self.environment_protection, width=20, height=2,
                                  bg="#009688", fg="white", font=("Arial", 11))
        environment_btn.grid(row=1, column=0, padx=5, pady=5)
        
        welfare_btn = tk.Button(btn_frame, text="Welfare Reform ⚕️", 
                              command=self.welfare_reform, width=20, height=2,
                              bg="#FF9800", fg="white", font=("Arial", 11))
        welfare_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # Next day button
        next_day_btn = tk.Button(policy_frame, text="Next Day ➡️", 
                               command=self.next_day, width=42, height=1,
                               bg="#9C27B0", fg="white", font=("Arial", 11))
        next_day_btn.pack(pady=10)
        
        # Bottom menu
        menu_frame = tk.Frame(main_frame, bg="#f0f0f8")
        menu_frame.pack(fill=tk.X, padx=10, pady=5)
        
        save_btn = tk.Button(menu_frame, text="Save Game", command=self.save_game,
                          bg="#673AB7", fg="white", font=("Arial", 10))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        quit_btn = tk.Button(menu_frame, text="End Game", command=self.show_welcome_screen,
                          bg="#f44336", fg="white", font=("Arial", 10))
        quit_btn.pack(side=tk.RIGHT, padx=5)
        
        # Create approval graph
        self.create_approval_graph()
        
        # Update event list
        self.update_event_list()

    def create_approval_graph(self):
        # Clear any existing graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        # Create figure and plot
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.tight_layout()
        
        # Get approval data
        approval_data = self.simulation.approval_history
        
        # If we have enough data points, create a date-based x-axis
        if len(approval_data) > 1:
            # Create date range
            base_date = datetime.date(self.simulation.year, self.simulation.month, self.simulation.day)
            dates = [base_date - datetime.timedelta(days=len(approval_data)-i-1) for i in range(len(approval_data))]
            
            ax.plot(dates, approval_data, marker='o', linestyle='-', color='#2196F3', linewidth=2)
            
            # Format x-axis
            if len(dates) > 30:
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            else:
                days_interval = max(1, len(dates) // 5) if len(dates) > 5 else 1
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=days_interval))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
                
            plt.xticks(rotation=30)
        else:
            # Not enough data points yet, use simple indices
            ax.plot([0], approval_data, marker='o', linestyle='-', color='#2196F3')
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

    def boost_economy(self):
        effect, policy = self.simulation.make_policy("economy")
        messagebox.showinfo("Policy Implemented", 
                          f"You implemented {policy}.\nApproval change: +{effect:.2f}%")
        self.update_display()

    def lower_unemployment(self):
        effect, policy = self.simulation.make_policy("unemployment")
        messagebox.showinfo("Policy Implemented", 
                          f"You implemented {policy}.\nApproval change: +{effect:.2f}%")
        self.update_display()

    def environment_protection(self):
        effect, policy = self.simulation.make_policy("environment")
        messagebox.showinfo("Policy Implemented", 
                          f"You implemented {policy}.\nApproval change: +{effect:.2f}%")
        self.update_display()

    def welfare_reform(self):
        effect, policy = self.simulation.make_policy("welfare")
        messagebox.showinfo("Policy Implemented", 
                          f"You implemented {policy}.\nApproval change: +{effect:.2f}%")
        self.update_display()

    def next_day(self):
        event_type, event_name = self.simulation.advance_day()
        
        if event_type:
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

    def save_game(self):
        try:
            slot = simpledialog.askinteger("Save Game", "Enter save slot (1-3):", 
                                         minvalue=1, maxvalue=3)
            if slot is None:  # User canceled
                return
                
            save_file = f"pm_simulator_save_{slot}.pkl"
            with open(save_file, "wb") as f:
                pickle.dump(self.simulation, f)
            messagebox.showinfo("Save Complete", f"Game saved to slot {slot}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save game: {str(e)}")

    def quit_game(self):
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.root.destroy()

def main():
    root = tk.Tk()
    app = JapanPMSimulatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()