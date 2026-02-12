import json
import os
import time

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

def load_config():
    config_data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Merge with defaults
    for key, val in DEFAULTS.items():
        if key not in config_data:
            config_data[key] = val
        elif isinstance(val, dict):
            if not isinstance(config_data[key], dict):
                 config_data[key] = val
            else:
                for subkey, subval in val.items():
                    if subkey not in config_data[key]:
                        config_data[key][subkey] = subval
    return config_data

def save_config(config_data):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        print("\n[Success] Settings saved! Bot will update automatically.")
    except Exception as e:
        print(f"\n[Error] Failed to save settings: {e}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu(config):
    print("\n=== Maple Bot Settings (CLI) ===")
    print("1. Timers")
    print(f"   [1] Shift Interval: {config.get('SHIFT_INTERVAL')}s")
    print(f"   [2] Potion Interval: {config.get('POTION_INTERVAL')}s")
    print("\n2. Movement")
    print(f"   [3] Walk Tolerance: {config.get('WALK_TOLERANCE')} px")
    print("\n3. Game Keys")
    k = config.get('KEYS', {})
    print(f"   [4] Shift/Attack: {k.get('SHIFT')}")
    print(f"   [5] HP Potion:    {k.get('POTION_HP')}")
    print(f"   [6] MP Potion:    {k.get('POTION_MP')}")
    print(f"   [7] Left Key:     {k.get('LEFT')}")
    print(f"   [8] Right Key:    {k.get('RIGHT')}")
    print("\n4. System Hotkeys")
    s = config.get('SYSTEM_KEYS', {})
    print(f"   [9] Start/Stop:   {s.get('START_STOP')}")
    print(f"   [10] Set Minimap: {s.get('SET_MINIMAP')}")
    print(f"   [11] Set Home:    {s.get('SET_HOME')}")
    print(f"   [12] Set HP Pt:   {s.get('SET_HP')}")
    print(f"   [13] Set MP Pt:   {s.get('SET_MP')}")
    print(f"   [14] Set Lie Pt:  {s.get('SET_LIE')}")
    print(f"   [15] Toggle Mode: {s.get('TOGGLE_MODE')}")
    print("\n[Q] Quit")

def edit_value(config, key, subkey=None, subsubkey=None):
    current = config.get(key)
    if subkey:
        current = current.get(subkey)
    
    prompt = f"Enter new value for {subkey if subkey else key} (Current: {current}): "
    new_val = input(prompt)
    if not new_val.strip():
        return

    # Helper to update
    if subkey:
        target = config[key]
        target_key = subkey
    else:
        target = config
        target_key = key

    # Type conversion
    try:
        if isinstance(current, float):
            target[target_key] = float(new_val)
        elif isinstance(current, int):
            target[target_key] = int(new_val)
        else:
            target[target_key] = new_val
        save_config(config)
    except ValueError:
        print("Invalid format!")
        time.sleep(1)

def main():
    while True:
        config = load_config()
        print_menu(config)
        choice = input("\nSelect option to edit (or Q to quit): ").strip().lower()
        
        if choice == 'q':
            break
        
        mapping = {
            '1': ('SHIFT_INTERVAL', None),
            '2': ('POTION_INTERVAL', None),
            '3': ('WALK_TOLERANCE', None),
            '4': ('KEYS', 'SHIFT'),
            '5': ('KEYS', 'POTION_HP'),
            '6': ('KEYS', 'POTION_MP'),
            '7': ('KEYS', 'LEFT'),
            '8': ('KEYS', 'RIGHT'),
            '9': ('SYSTEM_KEYS', 'START_STOP'),
            '10': ('SYSTEM_KEYS', 'SET_MINIMAP'),
            '11': ('SYSTEM_KEYS', 'SET_HOME'),
            '12': ('SYSTEM_KEYS', 'SET_HP'),
            '13': ('SYSTEM_KEYS', 'SET_MP'),
            '14': ('SYSTEM_KEYS', 'SET_LIE'),
            '15': ('SYSTEM_KEYS', 'TOGGLE_MODE'),
        }

        if choice in mapping:
            key, subkey = mapping[choice]
            edit_value(config, key, subkey)
        else:
            pass

if __name__ == "__main__":
    main()
