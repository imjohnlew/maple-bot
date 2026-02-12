from flask import Flask, render_template, request, jsonify
import json
import os
import webbrowser
from threading import Timer

app = Flask(__name__)
CONFIG_FILE = "bot_config_v2.json"

# Default values identical to other scripts so nothing breaks if file missing
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
    },
    "GAME_WINDOW_NAME": "MapleStory",
    "AUTO_FOCUS_GAME": True
}

def load_config():
    config_data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Merge defaults (deep merge for nested dicts)
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
    
    # Ensure default string keys exist
    if 'GAME_WINDOW_NAME' not in config_data:
        config_data['GAME_WINDOW_NAME'] = DEFAULTS['GAME_WINDOW_NAME']
        
    return config_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify(load_config())

@app.route('/api/config', methods=['POST'])
def save_config():
    try:
        new_config = request.json
        # validate types just in case (simple check)
        # In a real app we'd schema validate, but here we trust the user mostly
        
        # Ensure we don't wipe existing keys not in the UI
        current = load_config()
        current.update(new_config) 
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(current, f, indent=4)
        return jsonify({"status": "success", "message": "Saved successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Auto-open browser after 1.5s
    Timer(1.5, open_browser).start()
    print("Starting Web UI on http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False) 
