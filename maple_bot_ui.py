import tkinter as tk
from tkinter import ttk
import threading
import pyautogui
import time
import json
import os
from pynput import keyboard

# --- Copied/Adapted from maple_bot.py ---
# Determine absolute path for config to ensure persistence works regardless of CWD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "bot_config_v2.json")

# Defaults
CUSTOM_TASKS = [] # List of dicts: {'key': 'a', 'interval': 1.0, 'enabled': True, 'last_run': 0}
WALK_TOLERANCE = 5
POTION_MODE = "SAFE"
ENABLE_JUMP = False

KEYS = {
    'SHIFT': 'shift',
    'POTION_HP': ';',
    'POTION_MP': 'l',
    'LEFT': 'left',
    'RIGHT': 'right'
}

SYSTEM_KEYS = {
    "START_STOP": "[",
    "TOGGLE_JUMP": "0",
    "SET_MINIMAP": "]",
    "SET_HOME": "\\",
    "SET_HP": "-",
    "SET_MP": "=",
    "TOGGLE_MODE": "9"
}

# State
RUNNING = False
MINIMAP_REGION = None
PLAYER_DOT_COLOR = None
HOME_X = None
HP_CHECK_POINT = None
MP_CHECK_POINT = None
MINIMAP_START_POS = None

def load_config():
    global MINIMAP_REGION, PLAYER_DOT_COLOR, HOME_X, HP_CHECK_POINT, MP_CHECK_POINT, POTION_MODE, ENABLE_JUMP
    global CUSTOM_TASKS, WALK_TOLERANCE, KEYS, SYSTEM_KEYS
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                if 'MINIMAP_REGION' in data: MINIMAP_REGION = tuple(data['MINIMAP_REGION'])
                if 'PLAYER_DOT_COLOR' in data: PLAYER_DOT_COLOR = tuple(data['PLAYER_DOT_COLOR'])
                if 'HOME_X' in data: HOME_X = data['HOME_X']
                if 'HP_CHECK_POINT' in data and data['HP_CHECK_POINT']: 
                    hp = data['HP_CHECK_POINT']
                    HP_CHECK_POINT = (hp[0], hp[1], tuple(hp[2]))
                if 'MP_CHECK_POINT' in data and data['MP_CHECK_POINT']:
                    mp = data['MP_CHECK_POINT']
                    MP_CHECK_POINT = (mp[0], mp[1], tuple(mp[2]))

                if 'POTION_MODE' in data: POTION_MODE = data['POTION_MODE']
                if 'ENABLE_JUMP' in data: ENABLE_JUMP = bool(data['ENABLE_JUMP'])
                
                if 'WALK_TOLERANCE' in data: WALK_TOLERANCE = int(data['WALK_TOLERANCE'])
                if 'KEYS' in data: KEYS.update(data['KEYS'])
                if 'SYSTEM_KEYS' in data: SYSTEM_KEYS.update(data['SYSTEM_KEYS'])

                # Load or Migrate Tasks
                if 'CUSTOM_TASKS' in data:
                    CUSTOM_TASKS = data['CUSTOM_TASKS']
                    # Reset last_run for safety
                    for t in CUSTOM_TASKS: t['last_run'] = 0
                else:
                    # Migration from old format
                    print("Migrating old config to CUSTOM_TASKS...")
                    CUSTOM_TASKS = []
                    if 'SHIFT_INTERVAL' in data:
                        CUSTOM_TASKS.append({'key': KEYS.get('SHIFT', 'shift'), 'interval': float(data['SHIFT_INTERVAL']), 'enabled': True, 'last_run': 0})
                    if 'POTION_INTERVAL' in data:
                        CUSTOM_TASKS.append({'key': KEYS.get('POTION_HP', ';'), 'interval': float(data['POTION_INTERVAL']), 'enabled': True, 'last_run': 0})
                        CUSTOM_TASKS.append({'key': KEYS.get('POTION_MP', 'l'), 'interval': float(data['POTION_INTERVAL']), 'enabled': True, 'last_run': 0})
                    if 'D_INTERVAL' in data:
                        CUSTOM_TASKS.append({'key': 'd', 'interval': float(data['D_INTERVAL']), 'enabled': True, 'last_run': 0})

        except Exception as e:
            print(f"Config Load Error: {e}")

def save_config():
    # Clean tasks for saving (remove runtime keys like last_run if we wanted, but keeping them is fine/harmless or reset them)
    # We'll valid keys only
    tasks_to_save = []
    for t in CUSTOM_TASKS:
        tasks_to_save.append({
            'key': t['key'],
            'interval': t['interval'],
            'enabled': t.get('enabled', True)
        })

    data = {
        'MINIMAP_REGION': MINIMAP_REGION,
        'PLAYER_DOT_COLOR': PLAYER_DOT_COLOR,
        'HOME_X': HOME_X,
        'HP_CHECK_POINT': HP_CHECK_POINT,
        'MP_CHECK_POINT': MP_CHECK_POINT,
        'POTION_MODE': POTION_MODE,
        'ENABLE_JUMP': ENABLE_JUMP,
        'WALK_TOLERANCE': WALK_TOLERANCE,
        'KEYS': KEYS,
        'SYSTEM_KEYS': SYSTEM_KEYS,
        'CUSTOM_TASKS': tasks_to_save
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except:
        pass

def colors_match(c1, c2, tolerance=10):
    if not c1 or not c2: return False
    return all(abs(a - b) <= tolerance for a, b in zip(c1[:3], c2[:3]))

def find_player_on_minimap():
    if not MINIMAP_REGION or not PLAYER_DOT_COLOR: return None
    left, top, w, h = MINIMAP_REGION
    try:
        im = pyautogui.screenshot(region=(int(left), int(top), int(w), int(h)))
        width, height = im.size
        for x in range(width):
            for y in range(height):
                if colors_match(im.getpixel((x, y)), PLAYER_DOT_COLOR, tolerance=10):
                    return x
    except:
        pass
    return None

def normalize_key(key):
    try:
        if hasattr(key, 'char') and key.char: return key.char
        return key.name
    except:
        return str(key)

# --- UI Class ---
class MapleBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MapleBot")
        self.root.geometry("360x600") # Increased width and height for better layout
        
        # Position Top Left or similar
        self.root.geometry("+50+50")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.90)
        self.root.configure(bg="#222")
        
        load_config()
        self.create_widgets()
        
        # Threads
        self.exit_flag = False
        threading.Thread(target=self.bot_loop, daemon=True).start()
        threading.Thread(target=self.key_listener, daemon=True).start()

        # Permissions Check
        try:
            x, y = pyautogui.position()
        except Exception:
            self.status_var.set("No Permission!")
            self.lbl_status.config(fg="yellow")

    def create_widgets(self):
        # Header Status
        self.status_var = tk.StringVar(value="PAUSED")
        self.lbl_status = tk.Label(self.root, textvariable=self.status_var, fg="#e74c3c", bg="#222", font=("Helvetica", 16, "bold"))
        self.lbl_status.pack(pady=5)
        
        # Start/Stop Button
        self.btn_run = tk.Button(self.root, text="Start Bot", command=self.toggle_running, bg="#2ecc71", fg="black")
        self.btn_run.pack(fill=tk.X, padx=20, pady=5)
        
        # --- Task List (Treeview) ---
        frm_list = tk.Frame(self.root, bg="#222")
        frm_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(frm_list, text="Key Intervals", fg="white", bg="#222").pack(anchor="w")

        # Treeview
        columns = ("key", "interval")
        self.tree = ttk.Treeview(frm_list, columns=columns, show="headings", height=6)
        self.tree.heading("key", text="Key")
        self.tree.column("key", width=60)
        self.tree.heading("interval", text="Secs")
        self.tree.column("interval", width=60)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frm_list, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscroll=scrollbar.set)

        # Delete Button (Contextual or below)
        
        # --- Add/Edit Task Section ---
        frm_add = tk.Frame(self.root, bg="#222")
        frm_add.pack(fill=tk.X, padx=10, pady=5)
        
        # Row 1: Inputs
        row1 = tk.Frame(frm_add, bg="#222")
        row1.pack(fill=tk.X, pady=2)
        
        tk.Label(row1, text="Key:", fg="white", bg="#222", width=5).pack(side=tk.LEFT)
        self.ent_key = tk.Entry(row1, width=8, bg="#333", fg="white")
        self.ent_key.pack(side=tk.LEFT, padx=5)
        
        tk.Label(row1, text="Sec:", fg="white", bg="#222", width=5).pack(side=tk.LEFT)
        self.ent_int = tk.Entry(row1, width=8, bg="#333", fg="white")
        self.ent_int.pack(side=tk.LEFT, padx=5)
        
        # Row 2: Buttons
        row2 = tk.Frame(frm_add, bg="#222")
        row2.pack(fill=tk.X, pady=5)
        
        # Use frames or pack options to distribute buttons evenly
        btn_add = tk.Button(row2, text="Add", command=self.add_task, bg="#2ecc71", fg="black", width=6)
        btn_add.pack(side=tk.LEFT, padx=2)

        btn_upd = tk.Button(row2, text="Update", command=self.update_task, bg="#3498db", fg="black", width=6)
        btn_upd.pack(side=tk.LEFT, padx=2)

        btn_del = tk.Button(row2, text="Delete", command=self.delete_task, bg="#e74c3c", fg="black", width=6)
        btn_del.pack(side=tk.LEFT, padx=2)

        # Bind Box Selection
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.refresh_task_list()

        # Sub-status
        self.info_var = tk.StringVar(value="Waiting...")
        tk.Label(self.root, textvariable=self.info_var, fg="#aaa", bg="#222", font=("Helvetica", 10)).pack(pady=2)

        # Controls Grid (Shortcuts)
        frm_controls_header = tk.Frame(self.root, bg="#222")
        frm_controls_header.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.btn_toggle_shortcuts = tk.Button(frm_controls_header, text="Hide Shortcuts [-]", command=self.toggle_shortcuts, 
                                              bg="#444", fg="white", relief=tk.FLAT, font=("Helvetica", 10))
        self.btn_toggle_shortcuts.pack(fill=tk.X)

        self.frm_shortcuts = tk.Frame(self.root, bg="#222")
        self.frm_shortcuts.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Helper to make label rows
        def row(txt, key):
            f = tk.Frame(self.frm_shortcuts, bg="#222")
            f.pack(fill=tk.X, pady=2)
            tk.Label(f, text=txt, fg="white", bg="#222", width=15, anchor="w").pack(side=tk.LEFT)
            tk.Label(f, text=f"[{key}]", fg="#eea", bg="#222", font=("Courier", 10, "bold")).pack(side=tk.RIGHT)

        row("Start/Stop", SYSTEM_KEYS['START_STOP'])
        row("Jump Toggle", SYSTEM_KEYS['TOGGLE_JUMP'])
        row("Set Minimap", SYSTEM_KEYS['SET_MINIMAP'])
        row("Set Home", SYSTEM_KEYS['SET_HOME'])
        row("Set HP Pt", SYSTEM_KEYS['SET_HP'])
        row("Set MP Pt", SYSTEM_KEYS['SET_MP'])
        row("Toggle Mode", SYSTEM_KEYS['TOGGLE_MODE'])

    def refresh_task_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for task in CUSTOM_TASKS:
            self.tree.insert("", tk.END, values=(task['key'], task['interval']))

    def on_tree_select(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            item = self.tree.item(selected_items[0])
            vals = item['values']
            if vals:
                self.ent_key.delete(0, tk.END)
                self.ent_key.insert(0, str(vals[0]))
                self.ent_int.delete(0, tk.END)
                self.ent_int.insert(0, str(vals[1]))

    def add_task(self):
        k = self.ent_key.get().strip()
        i = self.ent_int.get().strip()
        if k and i:
            try:
                interval = float(i)
                CUSTOM_TASKS.append({'key': k, 'interval': interval, 'enabled': True, 'last_run': 0})
                save_config()
                self.refresh_task_list()
                # self.ent_key.delete(0, tk.END) # Keep values for easy rapid entry or modification
                # self.ent_int.delete(0, tk.END)
            except ValueError:
                pass

    def update_task(self):
        selected_items = self.tree.selection()
        if not selected_items: return
        
        k = self.ent_key.get().strip()
        i = self.ent_int.get().strip()
        if k and i:
            try:
                interval = float(i)
                item_id = selected_items[0]
                index = self.tree.index(item_id)
                
                if 0 <= index < len(CUSTOM_TASKS):
                    CUSTOM_TASKS[index]['key'] = k
                    CUSTOM_TASKS[index]['interval'] = interval
                    save_config()
                    self.refresh_task_list()
            except ValueError:
                pass

    def delete_task(self):
        selected_items = self.tree.selection()
        if selected_items:
            # Get index of the first selected item
            item_id = selected_items[0]
            index = self.tree.index(item_id)
            if 0 <= index < len(CUSTOM_TASKS):
                CUSTOM_TASKS.pop(index)
                save_config()
                self.refresh_task_list()

    def toggle_shortcuts(self):
        if self.frm_shortcuts.winfo_viewable():
            self.frm_shortcuts.pack_forget()
            self.btn_toggle_shortcuts.config(text="Show Shortcuts [+]")
        else:
            self.frm_shortcuts.pack(fill=tk.BOTH, expand=True, padx=10)
            self.btn_toggle_shortcuts.config(text="Hide Shortcuts [-]")
        
    def toggle_running(self):
        global RUNNING
        RUNNING = not RUNNING
        self.update_ui()

    def update_ui(self):
        # Update Status Color/Text
        s = "RUNNING" if RUNNING else "PAUSED"
        color = "#2ecc71" if RUNNING else "#e74c3c"
        self.status_var.set(s)
        self.lbl_status.config(fg=color)
        
        # Update Button
        btn_txt = "Stop Bot" if RUNNING else "Start Bot"
        self.btn_run.config(text=btn_txt, bg="#e74c3c" if RUNNING else "#2ecc71")
        
        # Info Text
        j = "ON" if ENABLE_JUMP else "OFF"
        m = "Set" if MINIMAP_REGION else "No"
        h = "Set" if HOME_X else "No"
        self.info_var.set(f"Jump: {j} | Map: {m} | Home: {h}")

    def key_listener(self):
        def on_press(key):
            global RUNNING, MINIMAP_START_POS, MINIMAP_REGION, PLAYER_DOT_COLOR, HOME_X, HP_CHECK_POINT, MP_CHECK_POINT, POTION_MODE, ENABLE_JUMP
            
            k = normalize_key(key)
            if key == keyboard.Key.esc:
                self.root.quit()
                return False
                
            updated = False
            
            # Start/Stop
            if k == SYSTEM_KEYS['START_STOP']:
                RUNNING = not RUNNING
                updated = True
                
            # Toggle Jump
            elif k == SYSTEM_KEYS['TOGGLE_JUMP']:
                ENABLE_JUMP = not ENABLE_JUMP
                updated = True
                save_config()

            # Minimap
            elif k == SYSTEM_KEYS['SET_MINIMAP']:
                x, y = pyautogui.position()
                if MINIMAP_START_POS is None:
                    MINIMAP_START_POS = (x, y)
                    print("Map Start Set")
                else:
                    x1, y1 = MINIMAP_START_POS
                    MINIMAP_REGION = (min(x1,x), min(y1,y), abs(x-x1), abs(y-y1))
                    MINIMAP_START_POS = None
                    save_config()
                updated = True

            # Home
            elif k == SYSTEM_KEYS['SET_HOME']:
                 if MINIMAP_REGION:
                     x, y = pyautogui.position()
                     # relative check logic simplified for UI responsiveness
                     try:
                         color = pyautogui.screenshot(region=(x,y,1,1)).getpixel((0,0))
                         PLAYER_DOT_COLOR = color
                         HOME_X = x - MINIMAP_REGION[0]
                         save_config()
                     except: pass
                 updated = True

            # HP/MP
            elif k == SYSTEM_KEYS['SET_HP']:
                x, y = pyautogui.position()
                try:
                    c = pyautogui.screenshot(region=(x,y,1,1)).getpixel((0,0))
                    HP_CHECK_POINT = (x, y, c)
                    save_config()
                except: pass
                updated = True
                
            elif k == SYSTEM_KEYS['SET_MP']:
                x, y = pyautogui.position()
                try:
                    c = pyautogui.screenshot(region=(x,y,1,1)).getpixel((0,0))
                    MP_CHECK_POINT = (x, y, c)
                    save_config()
                except: pass
                updated = True
            
            # Mode
            elif k == SYSTEM_KEYS['TOGGLE_MODE']:
                POTION_MODE = "DANGER" if POTION_MODE == "SAFE" else "SAFE"
                save_config()
                updated = True

            if updated:
                self.root.after(0, self.update_ui)

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def bot_loop(self):
        # Local state is less relevant now as we store last_run in CUSTOM_TASKS
        holding_key = None
        shift_count = 0
        holding_key = None
        
        while True:
            if not RUNNING:
                if holding_key:
                    pyautogui.keyUp(holding_key)
                    holding_key = None
                time.sleep(0.1)
                continue
            
            now = time.time()
            
            try:
                # 1. Generic Task Loop
                for task in CUSTOM_TASKS:
                    if not task.get('enabled', True): continue
                    
                    key = task['key']
                    interval = task['interval']
                    last = task.get('last_run', 0)
                    
                    if now - last >= interval:
                        # Handle multiple keys if comma separated? For now basic support
                        pyautogui.press(key)
                        
                        # Special case: Jump if legacy condition met? 
                        # We'll just stick to the generic 'space' task if user wants it.
                        # But for backward compatibility with 'ENABLE_JUMP' which does Shift+Jump:
                        if key == KEYS['SHIFT'] and ENABLE_JUMP:
                             # This is a bit hacky, but keeps specific "Jump Attack" logic if the key matches 'shift'
                             # Alternatively, the user should just add 'space' as a task with same interval.
                             # But 'Jump' usually means 'Shift' then 'Space' immediately.
                             time.sleep(0.05)
                             pyautogui.press('space')

                        task['last_run'] = now
                    
                # 3. Auto Walk
                if MINIMAP_REGION and PLAYER_DOT_COLOR and HOME_X is not None:
                    curr_x = find_player_on_minimap()
                    if curr_x is not None:
                        diff = curr_x - HOME_X
                        if abs(diff) > WALK_TOLERANCE:
                            if diff > 0: # Too far right, go left
                                 if holding_key != 'left':
                                     if holding_key: pyautogui.keyUp('right')
                                     pyautogui.keyDown('left')
                                     holding_key = 'left'
                            else: # Too far left, go right
                                 if holding_key != 'right':
                                     if holding_key: pyautogui.keyUp('left')
                                     pyautogui.keyDown('right')
                                     holding_key = 'right'
                        else:
                            if holding_key:
                                pyautogui.keyUp(holding_key)
                                holding_key = None
            except Exception as e:
                print(f"Bot Loop Error: {e}")
                # If permisson fail, it might flood loop, so maybe stop running?
                # or just sleep
                time.sleep(1)
            
            time.sleep(0.05)

if __name__ == "__main__":
    root = tk.Tk()
    app = MapleBotApp(root)
    root.after(100, app.update_ui)
    root.mainloop()
