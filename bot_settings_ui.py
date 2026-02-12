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
    },
    "SYSTEM_KEYS": {
        "START_STOP": "[",
        "SET_MINIMAP": "]",
        "SET_HOME": "\\",
        "SET_HP": "-",
        "SET_MP": "=",
        "SET_LIE": "0",
        "TOGGLE_MODE": "9"
    }
}

class BotSettingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maple Bot Settings")
        self.root.geometry("450x700") # Increased height for new keys

        self.entries = {}
        self.key_vars = {} # For Game Keys
        self.sys_key_vars = {} # For System Keys
        
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
                # Ensure nested dicts (KEYS, SYSTEM_KEYS) have all fields
                if not isinstance(self.config_data[key], dict):
                     self.config_data[key] = val
                else:
                    for subkey, subval in val.items():
                        if subkey not in self.config_data[key]:
                            self.config_data[key][subkey] = subval

    def create_widgets(self):
        # Scrollable Container (Simple approach: just a frame, if it gets too big we might need canvas)
        # For now, just a frame is fine, window is tall enough.
        container = tk.Frame(self.root, padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        tk.Label(container, text="Bot Configuration", font=("Arial", 16, "bold")).pack(pady=(0, 15))

        # --- Frames for 2-column layout optional, but list is fine ---

        # Timers Section
        self.create_section_label(container, "Timers (Seconds)")
        self.create_entry(container, "Shift Interval (Attack)", "SHIFT_INTERVAL")
        self.create_entry(container, "Potion Interval (Fallback)", "POTION_INTERVAL")

        # Movement Section
        self.create_section_label(container, "Movement")
        self.create_entry(container, "Walk Tolerance (Pixels)", "WALK_TOLERANCE")

        # Game Keys Section
        self.create_section_label(container, "Game Key Bindings")
        game_keys_frame = tk.Frame(container)
        game_keys_frame.pack(fill=tk.X, pady=5)
        
        self.key_vars = {}
        for key_name in ["SHIFT", "POTION_HP", "POTION_MP", "LEFT", "RIGHT"]:
            self.create_key_row(game_keys_frame, key_name, "KEYS", self.key_vars)

        # System Hotkeys Section (NEW)
        self.create_section_label(container, "System Hotkeys (Control Bot)")
        sys_keys_frame = tk.Frame(container)
        sys_keys_frame.pack(fill=tk.X, pady=5)
        
        self.sys_key_vars = {}
        for key_name in ["START_STOP", "SET_MINIMAP", "SET_HOME", "SET_HP", "SET_MP", "SET_LIE", "TOGGLE_MODE"]:
            self.create_key_row(sys_keys_frame, key_name, "SYSTEM_KEYS", self.sys_key_vars)

        # Save Button
        tk.Button(container, text="Save Settings", command=self.save_settings, bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(pady=20, fill=tk.X)

    def create_key_row(self, parent, key_name, config_section, storage_dict):
        row = tk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=key_name, width=20, anchor="w").pack(side=tk.LEFT)
        
        initial_val = self.config_data[config_section].get(key_name, "")
        var = tk.StringVar(value=str(initial_val))
        storage_dict[key_name] = var
        tk.Entry(row, textvariable=var).pack(side=tk.RIGHT, expand=True, fill=tk.X)

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

            # Update SYSTEM_KEYS
            if "SYSTEM_KEYS" not in self.config_data:
                self.config_data["SYSTEM_KEYS"] = {}
            for key_name, var in self.sys_key_vars.items():
                self.config_data["SYSTEM_KEYS"][key_name] = var.get()

            # Write to file
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            
            messagebox.showinfo("Success", "Settings saved successfully!\nBot will auto-reload shortly.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BotSettingsApp(root)
    root.mainloop()
