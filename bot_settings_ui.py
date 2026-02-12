import tkinter as tk
from tkinter import messagebox
import json
import os

CONFIG_FILE = "bot_config_v2.json"

# Default values if config is missing or partial
DEFAULTS = {
    "SHIFT_INTERVAL": 0.5,
    "POTION_INTERVAL": 5.0,
    "WALK_TOLERANCE": 5,
    "KEYS": {
        "SHIFT": "shift",
        "POTION_HP": ";",
        "POTION_MP": "l",
        "LEFT": "left",
        "RIGHT": "right"
    }
}

class BotSettingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maple Bot Settings")
        self.root.geometry("400x500")

        self.entries = {}
        
        self.load_config()
        self.create_widgets()

    def load_config(self):
        self.config_data = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.config_data = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")
        
        # Merge with defaults for missing keys
        for key, val in DEFAULTS.items():
            if key not in self.config_data:
                self.config_data[key] = val
            elif isinstance(val, dict):
                # Ensure nested dicts (KEYS) have all fields
                if not isinstance(self.config_data[key], dict):
                     self.config_data[key] = val
                else:
                    for subkey, subval in val.items():
                        if subkey not in self.config_data[key]:
                            self.config_data[key][subkey] = subval

    def create_widgets(self):
        # Container
        container = tk.Frame(self.root, padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        tk.Label(container, text="Bot Configuration", font=("Arial", 16, "bold")).pack(pady=(0, 20))

        # Timers Section
        self.create_section_label(container, "Timers (Seconds)")
        self.create_entry(container, "Shift Interval (Attack Speed)", "SHIFT_INTERVAL")
        self.create_entry(container, "Potion Interval (Fallback)", "POTION_INTERVAL")

        # Movement Section
        self.create_section_label(container, "Movement")
        self.create_entry(container, "Walk Tolerance (Pixels)", "WALK_TOLERANCE")

        # Keys Section
        self.create_section_label(container, "Key Bindings")
        
        keys_frame = tk.Frame(container)
        keys_frame.pack(fill=tk.X, pady=5)
        
        # We handle KEYS differently as it's a nested dict
        self.key_vars = {}
        for key_name in ["SHIFT", "POTION_HP", "POTION_MP", "LEFT", "RIGHT"]:
            row = tk.Frame(keys_frame)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=key_name, width=15, anchor="w").pack(side=tk.LEFT)
            
            initial_val = self.config_data["KEYS"].get(key_name, "")
            var = tk.StringVar(value=str(initial_val))
            self.key_vars[key_name] = var
            tk.Entry(row, textvariable=var).pack(side=tk.RIGHT, expand=True, fill=tk.X)

        # Save Button
        tk.Button(container, text="Save Settings", command=self.save_settings, bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(pady=20, fill=tk.X)

    def create_section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Arial", 12, "bold"), anchor="w").pack(fill=tk.X, pady=(15, 5))

    def create_entry(self, parent, label_text, config_key):
        row = tk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=label_text, width=25, anchor="w").pack(side=tk.LEFT)
        
        initial_val = self.config_data.get(config_key, "")
        var = tk.StringVar(value=str(initial_val))
        self.entries[config_key] = var
        tk.Entry(row, textvariable=var).pack(side=tk.RIGHT, expand=True, fill=tk.X)

    def save_settings(self):
        try:
            # Update config_data from simple entries
            for key, var in self.entries.items():
                val = var.get()
                # Try to convert to float/int if possible
                try:
                    if '.' in val:
                        self.config_data[key] = float(val)
                    else:
                        self.config_data[key] = int(val)
                except ValueError:
                    self.config_data[key] = val

            # Update KEYS
            for key_name, var in self.key_vars.items():
                self.config_data["KEYS"][key_name] = var.get()

            # Write to file
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            
            messagebox.showinfo("Success", "Settings saved successfully!\nRestart the bot to apply changes.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BotSettingsApp(root)
    root.mainloop()
