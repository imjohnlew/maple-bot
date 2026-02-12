import time
import pyautogui
from pynput import keyboard
import json
import os

CONFIG_FILE = "bot_config_v2.json"

# --- Configuration State ---
# Blind Mode Timers
SHIFT_INTERVAL = 0.5
POTION_INTERVAL = 5.0

# Disable FailSafe (User can use ESC to quit)
pyautogui.FAILSAFE = False

# Minimap / Auto-Walk
MINIMAP_REGION = None      # (left, top, width, height)
PLAYER_DOT_COLOR = None    # (R, G, B)
HOME_X = None              # X-coordinate on minimap to stay at
WALK_TOLERANCE = 5         # Pixels on minimap allowed before moving

# Setup State
MINIMAP_START_POS = None

# Runtime State
RUNNING = False
EXIT_PROGRAM = False

# Smart Potion State
HP_CHECK_POINT = None  # (x, y, (r, g, b))
MP_CHECK_POINT = None
POTION_MODE = "SAFE" # "SAFE" (Default: drink if color GONE) or "DANGER" (Drink if color APPEARS/MATCHES)

# Runtime State
RUNNING = False
EXIT_PROGRAM = False

# Smart Potion State
# Smart Potion State
HP_CHECK_POINT = None  # (x, y, (r, g, b))
MP_CHECK_POINT = None
LIE_DETECTOR_POINT = None # New
POTION_MODE = "SAFE" # "SAFE" (Default: drink if color GONE) or "DANGER" (Drink if color APPEARS/MATCHES)
AUTO_FOCUS_GAME = True
LIE_CHECK_INTERVAL = 5.0

# System Keys Defaults
SYSTEM_KEYS = {
    "START_STOP": "[",
    "SET_MINIMAP": "]",
    "SET_HOME": "\\",
    "SET_HP": "-",
    "SET_MP": "=",
    "SET_LIE": "0",
    "TOGGLE_MODE": "9"
}

KEYS = {
    'SHIFT': 'shift',
    'POTION_HP': ';',
    'POTION_MP': 'l',
    'LEFT': 'left',
    'RIGHT': 'right'
}

def save_config():
    data = {
        'MINIMAP_REGION': MINIMAP_REGION,
        'PLAYER_DOT_COLOR': PLAYER_DOT_COLOR,
        'HOME_X': HOME_X,
        'HP_CHECK_POINT': HP_CHECK_POINT,
        'MP_CHECK_POINT': MP_CHECK_POINT,
        'LIE_DETECTOR_POINT': LIE_DETECTOR_POINT,
        'POTION_MODE': POTION_MODE,
        'SHIFT_INTERVAL': SHIFT_INTERVAL,
        'POTION_INTERVAL': POTION_INTERVAL,
        'WALK_TOLERANCE': WALK_TOLERANCE,
        'KEYS': KEYS,
        'SYSTEM_KEYS': SYSTEM_KEYS,
        'GAME_WINDOW_NAME': GAME_WINDOW_NAME,
        'AUTO_FOCUS_GAME': AUTO_FOCUS_GAME,
        'LIE_CHECK_INTERVAL': LIE_CHECK_INTERVAL
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"[Config] Saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"[Config] Save failed: {e}")

from AppKit import NSWorkspace
import subprocess

def load_config():
    global MINIMAP_REGION, PLAYER_DOT_COLOR, HOME_X, HP_CHECK_POINT, MP_CHECK_POINT, POTION_MODE, LIE_DETECTOR_POINT
    global SHIFT_INTERVAL, POTION_INTERVAL, WALK_TOLERANCE, KEYS, SYSTEM_KEYS, GAME_WINDOW_NAME, AUTO_FOCUS_GAME, LIE_CHECK_INTERVAL
    
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
                if 'LIE_DETECTOR_POINT' in data and data['LIE_DETECTOR_POINT']:
                    ld = data['LIE_DETECTOR_POINT']
                    LIE_DETECTOR_POINT = (ld[0], ld[1], tuple(ld[2]))

                if 'POTION_MODE' in data: POTION_MODE = data['POTION_MODE']
                
                # New Configs
                if 'SHIFT_INTERVAL' in data: SHIFT_INTERVAL = float(data['SHIFT_INTERVAL'])
                if 'POTION_INTERVAL' in data: POTION_INTERVAL = float(data['POTION_INTERVAL'])
                if 'WALK_TOLERANCE' in data: WALK_TOLERANCE = int(data['WALK_TOLERANCE'])
                if 'KEYS' in data: KEYS.update(data['KEYS'])
                if 'SYSTEM_KEYS' in data: SYSTEM_KEYS.update(data['SYSTEM_KEYS'])
                
                # App Focus
                GAME_WINDOW_NAME = data.get('GAME_WINDOW_NAME', "MapleStory")
                AUTO_FOCUS_GAME = data.get('AUTO_FOCUS_GAME', True)
                LIE_CHECK_INTERVAL = float(data.get('LIE_CHECK_INTERVAL', 5.0))

            print(f"[Config] Loaded: Minimap={bool(MINIMAP_REGION)}, HomeX={HOME_X}")
            print(f"[Config] Intervals: Shift={SHIFT_INTERVAL}s, Potion={POTION_INTERVAL}s")
            print(f"[Config] Target App: {GAME_WINDOW_NAME}")
        except Exception as e:
            print(f"[Config] Load failed: {e}")

def ensure_game_focus():
    """Checks if the game is focused. If not, activates it."""
    try:
        active_app = NSWorkspace.sharedWorkspace().frontmostApplication().localizedName()
        if active_app != GAME_WINDOW_NAME:
            # print(f"[System] Switching focus to {GAME_WINDOW_NAME}...")
            script = f'tell application "{GAME_WINDOW_NAME}" to activate'
            subprocess.run(['osascript', '-e', script], capture_output=True)
            time.sleep(0.1) # Wait for swap
            return False # Indicate we just swapped, maybe skip this frame's action
    except Exception:
        pass
    return True

def normalize_key(key):
    """Convert pynput key object to string matching config."""
    try:
        if hasattr(key, 'char') and key.char:
            return key.char
        else:
            # Special keys like Key.f8 -> 'f8', Key.esc -> 'esc'
            return key.name
    except:
        return str(key)

def on_press(key):
    global RUNNING, EXIT_PROGRAM, MINIMAP_START_POS, MINIMAP_REGION, PLAYER_DOT_COLOR, HOME_X, HP_CHECK_POINT, MP_CHECK_POINT, LIE_DETECTOR_POINT, POTION_MODE
    
    key_str = normalize_key(key)
    
    try:
        if key == keyboard.Key.esc:
            EXIT_PROGRAM = True
            return False

        # Start/Stop
        if key_str == SYSTEM_KEYS['START_STOP']:
            RUNNING = not RUNNING
            print(f"\n[{'RUNNING' if RUNNING else 'PAUSED'}]")
            if RUNNING:
                print(" -> Keys: Shift (0.5s)")
                if HP_CHECK_POINT or MP_CHECK_POINT:
                    print(f" -> Smart Potion: [{POTION_MODE} LOGIC]") 
                    if POTION_MODE == "SAFE":
                        print("    (Drink if Color DISAPPEARS)")
                    else:
                        print("    (Drink if Color APPEARS/MATCHES)")
                else:
                    print(" -> Timer Potion (Fallback): Every 5.0s")
                
                if MINIMAP_REGION and HOME_X:
                    print(f" -> Auto-Walking ENABLED (Home X: {HOME_X})")
                else:
                    print(" -> Auto-Walk DISABLED (Set Minimap first)")
                
                if LIE_DETECTOR_POINT:
                    print(" -> Lie Detector Alarm ENABLED (Watching Point)")

        # Toggle Potion Mode
        if key_str == SYSTEM_KEYS['TOGGLE_MODE']:
            if POTION_MODE == "SAFE":
                POTION_MODE = "DANGER"
                print("\n[Potion Mode] SWITCHED TO: DANGER (White Bar detection)")
                print(" -> Logic: Drink potion if pixel MATCHES the saved color.")
                print(" -> Tip: Set Points on the EMPTY/WHITE part of the bar.")
            else:
                POTION_MODE = "SAFE"
                print("\n[Potion Mode] SWITCHED TO: SAFE (Red Bar detection)")
                print(" -> Logic: Drink potion if pixel DOES NOT match the saved color.")
                print(" -> Tip: Set Points on the FULL/RED part of the bar.")
            save_config()

        # Set Minimap Region (Top-Left then Bottom-Right)
        if key_str == SYSTEM_KEYS['SET_MINIMAP']:
            x, y = pyautogui.position()
            if MINIMAP_START_POS is None:
                MINIMAP_START_POS = (x, y)
                print(f"[Minimap] Top-Left: ({x}, {y}). NOW Click Bottom-Right ({SYSTEM_KEYS['SET_MINIMAP']}).")
            else:
                x1, y1 = MINIMAP_START_POS
                final_x, final_y = min(x1, x), min(y1, y)
                w, h = abs(x - x1), abs(y - y1)
                MINIMAP_REGION = (final_x, final_y, w, h)
                MINIMAP_START_POS = None
                print(f"[Minimap] Set: {MINIMAP_REGION}")
                save_config()

        # Set Home (Hover over yellow dot on minimap)
        if key_str == SYSTEM_KEYS['SET_HOME']:
            if not MINIMAP_REGION:
                print("Set Minimap first!")
                return
            
            x, y = pyautogui.position()
            # Verify mouse is inside minimap
            mx, my, mw, mh = MINIMAP_REGION
            if not (mx <= x <= mx + mw and my <= y <= my + mh):
                print("Error: Mouse not inside defined Minimap region!")
                return
            
            # Capture color under mouse
            try:
                im_pixel = pyautogui.screenshot(region=(x, y, 1, 1))
                color = im_pixel.getpixel((0, 0))
            except Exception:
                print("Error: Could not read pixel color.")
                return

            PLAYER_DOT_COLOR = color
            # Calculate relative X
            HOME_X = x - mx
            
            print(f"[Home] Set! Player Color: {color}, Relative X: {HOME_X}")
            save_config()

        # Set HP Check Point
        if key_str == SYSTEM_KEYS['SET_HP']:
            x, y = pyautogui.position()
            try:
                px = pyautogui.screenshot(region=(x, y, 1, 1))
                color = px.getpixel((0, 0))
                HP_CHECK_POINT = (x, y, color)
                print(f"[HP Logic] Set at ({x}, {y}) Color: {color}")
                if POTION_MODE == "SAFE":
                    print(" -> Watch for this color to DISAPPEAR (e.g. Red)")
                else:
                    print(" -> Watch for this color to APPEAR (e.g. White/Empty)")
                save_config()
            except Exception as e:
                print(f"Error setting HP: {e}")

        # Set MP Check Point
        if key_str == SYSTEM_KEYS['SET_MP']:
            x, y = pyautogui.position()
            try:
                px = pyautogui.screenshot(region=(x, y, 1, 1))
                color = px.getpixel((0, 0))
                MP_CHECK_POINT = (x, y, color)
                print(f"[MP Logic] Set at ({x}, {y}) Color: {color}")
                save_config()
            except Exception as e:
                print(f"Error setting MP: {e}")

        # Set Lie Detector Check Point
        if key_str == SYSTEM_KEYS['SET_LIE']:
            try:
                x, y = pyautogui.position()
                
                # Check current state
                if 'LIE_CAPTURE_START' not in globals() or globals()['LIE_CAPTURE_START'] is None:
                    globals()['LIE_CAPTURE_START'] = (x, y)
                    print(f"[Lie Setup] Start Point Set: ({x}, {y}). NOW Move mouse to Bottom-Right & Press {SYSTEM_KEYS['SET_LIE']} again.")
                else:
                    x1, y1 = globals()['LIE_CAPTURE_START']
                    # Calculate region
                    left, top = min(x1, x), min(y1, y)
                    width, height = abs(x - x1), abs(y - y1)
                    
                    if width < 10 or height < 10:
                        print("[Lie Setup] Too small! Try again.")
                        globals()['LIE_CAPTURE_START'] = None
                        return

                    # Capture & Save
                    r_ints = (int(left), int(top), int(width), int(height))
                    im = pyautogui.screenshot(region=r_ints)
                    lie_file = "maple_lie_detector.png"
                    im.save(lie_file)
                    
                    LIE_DETECTOR_POINT = r_ints # Store tuple just in case, but rely on file
                    globals()['LIE_CAPTURE_START'] = None
                    
                    print(f"[Lie Setup] CAPTURED & SAVED to '{lie_file}'!")
                    print(" -> Logic: Will now scan FULL SCREEN for this image.")
                    print(" -> Tip: Best target is the static 'Type what you see.' header.")
                    save_config()

            except Exception as e:
                print(f"Error setting Lie Detector: {e}")

    except Exception as e:
        print(f"Key Error: {e}")
from pynput.keyboard import Key, Controller

keyboard_controller = Controller()

def press_game_key(key_char):
    # key_char is like 'shift', ';', 'l'
    # pynput needs Key.shift for special keys, or just the char for normal keys.
    
    target_key = key_char
    if key_char == 'shift':
        target_key = Key.shift
    elif key_char == 'left':
        target_key = Key.left
    elif key_char == 'right':
        target_key = Key.right
    # Add other special keys if needed (e.g. 'end', 'delete')
    
    try:
        keyboard_controller.press(target_key)
        time.sleep(0.1) # Longer hold for Mac/Game
        keyboard_controller.release(target_key)
    except Exception as e:
        print(f"Key Error with pynput: {e}")

def main():
    global CURRENT_TARGET, RUNNING
    # Load config first to get keys
    load_config()
    
    print("=== Maple Bot (Blind + AutoWalk + SmartPot) ===")
    print(f"{SYSTEM_KEYS['SET_MINIMAP']}: Set Minimap Region")
    print(f"{SYSTEM_KEYS['SET_HOME']}: Set Home Position")
    print(f"{SYSTEM_KEYS['SET_HP']}: Set HP Check Point")
    print(f"{SYSTEM_KEYS['SET_MP']}: Set MP Check Point")
    print(f"{SYSTEM_KEYS['SET_LIE']}: Set Lie Detector Check Point")
    print(f"{SYSTEM_KEYS['START_STOP']}: Start/Stop")
    print("ESC: Quit")
    print("------------------------------------")
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    last_shift = 0
    last_potion = 0
    shift_count = 0  # To track for Jump
    
    # State for walking
    holding_key = None # 'left' or 'right'
    
    last_lie_check = 0

    last_config_check = 0
    last_mtime = 0
    if os.path.exists(CONFIG_FILE):
        last_mtime = os.path.getmtime(CONFIG_FILE)

    while not EXIT_PROGRAM:
        current_time = time.time()
        
        # Check for config updates every 1 second
        if current_time - last_config_check > 1.0:
            if os.path.exists(CONFIG_FILE):
                try:
                    mtime = os.path.getmtime(CONFIG_FILE)
                    if mtime > last_mtime:
                        print("\n[System] Config change detected. Reloading...")
                        load_config()
                        last_mtime = mtime
                except Exception:
                    pass
            last_config_check = current_time

        if RUNNING:
            now = current_time
            
            # Ensure Game is Focused
            if AUTO_FOCUS_GAME and not ensure_game_focus():
                continue

            # 1. Blind Key Presses (Shift / Attack)
            if now - last_shift >= SHIFT_INTERVAL:
                pyautogui.press(KEYS['SHIFT'])
                shift_count += 1
                
                # Every 2nd Shift, Jump (Space)
                if shift_count % 2 == 0:
                     # Add a tiny delay so it registers as "Shift + Space" or "Shift then Space"
                    time.sleep(0.05)
                    pyautogui.press('space')
                    # print(" [Action] Jump!") 

                last_shift = now
            
            # --- TIMER POTION LOGIC (Simple & Reliable) ---
            if now - last_potion >= POTION_INTERVAL:
                print(" [Timer] Potions (; and l)")
                pyautogui.press(KEYS['POTION_HP']) 
                pyautogui.press(KEYS['POTION_MP'])
                last_potion = now

            # 3. Lie Detector Check (Image Search)
            lie_file = "maple_lie_detector.png"
            if os.path.exists(lie_file):
                # Optimization: Only check every N seconds (e.g. 5s)
                # Lie detectors give plenty of time (30s+), so 5s is safe and saves CPU
                if now - last_lie_check >= LIE_CHECK_INTERVAL:
                    last_lie_check = now
                    try:
                        # Scan screen for the saved image
                        # Need opencv-python installed for confidence param (defaults to exact if not)
                        # Use grayscale=True for speed
                        position = pyautogui.locateOnScreen(lie_file, confidence=0.8, grayscale=True)
                        
                        if position:
                            print(f"\n[ALARM] LIE DETECTOR FOUND at {position}! Pausing Bot...")
                            RUNNING = False 
                            
                            # Play Sound Alarm (Mac specific)
                            for _ in range(5):
                                os.system('afplay /System/Library/Sounds/Glass.aiff')
                                time.sleep(0.5)
                            
                            print(" -> Bot PAUSED. Solve it, then press Start.")
                    except Exception as e:
                        # print(f"Lie scan error: {e}")
                        pass
            elif LIE_DETECTOR_POINT:
                # Fallback to old pixel check if no image but point exists (legacy support)
                lx, ly, l_target_color = LIE_DETECTOR_POINT
                try:
                    if isinstance(l_target_color, tuple) and len(l_target_color) >= 3:
                        if pyautogui.onScreen(lx, ly) and colors_match(pyautogui.pixel(lx, ly), l_target_color, tolerance=5):
                            print("\n[ALARM] LIE DETECTOR (Pixel) DETECTED! Pausing Bot...")
                            RUNNING = False
                            for _ in range(5):
                                os.system('afplay /System/Library/Sounds/Glass.aiff')
                                time.sleep(0.5)
                except Exception:
                    pass

            # 4. Auto-Walk Logic
            if MINIMAP_REGION and PLAYER_DOT_COLOR and HOME_X is not None:
                current_x = find_player_on_minimap()
                
                if current_x is not None:
                    # Logic: Move back to Home X
                    diff = current_x - HOME_X
                    
                    if abs(diff) > WALK_TOLERANCE:
                        if diff > 0:
                            # Walk Left
                            if holding_key != 'left':
                                if holding_key: 
                                    pyautogui.keyUp('right')
                                pyautogui.keyDown('left')
                                holding_key = 'left'
                        else:
                             # Walk Right
                            if holding_key != 'right':
                                if holding_key: 
                                    pyautogui.keyUp('left')
                                pyautogui.keyDown('right')
                                holding_key = 'right'
                    else:
                        # Home
                        if holding_key:
                            if holding_key == 'left':
                                pyautogui.keyUp('left')
                            if holding_key == 'right':
                                pyautogui.keyUp('right')
                            holding_key = None
            
            time.sleep(0.05) 
        
        else:
            if holding_key:
                if holding_key == 'left':
                    pyautogui.keyUp('left')
                if holding_key == 'right':
                    pyautogui.keyUp('right')
                holding_key = None
            time.sleep(0.1)

    listener.join()

if __name__ == "__main__":
    main()
