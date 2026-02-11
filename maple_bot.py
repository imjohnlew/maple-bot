import time
import pyautogui
from pynput import keyboard
import json
import os

CONFIG_FILE = "bot_config_v2.json"

# --- Configuration State ---
# Blind Mode Timers
SHIFT_INTERVAL = 0.5
POTION_INTERVAL = 4.0

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
        'HOME_X': HOME_X
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f)
        print(f"[Config] Saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"[Config] Save failed: {e}")

def load_config():
    global MINIMAP_REGION, PLAYER_DOT_COLOR, HOME_X
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                if 'MINIMAP_REGION' in data: MINIMAP_REGION = tuple(data['MINIMAP_REGION'])
                if 'PLAYER_DOT_COLOR' in data: PLAYER_DOT_COLOR = tuple(data['PLAYER_DOT_COLOR'])
                if 'HOME_X' in data: HOME_X = data['HOME_X']
            print(f"[Config] Loaded: Minimap={MINIMAP_REGION}, HomeX={HOME_X}")
        except Exception as e:
            print(f"[Config] Load failed: {e}")

def colors_match(c1, c2, tolerance=10):
    if not c1 or not c2: return False
    return all(abs(a - b) <= tolerance for a, b in zip(c1[:3], c2[:3]))

def find_player_on_minimap():
    if not MINIMAP_REGION or not PLAYER_DOT_COLOR:
        return None

    left, top, w, h = MINIMAP_REGION
    
    # Take screenshot of minimap with Region support fix
    # On macOS, screenshot(region=...) needs ints
    region_ints = (int(left), int(top), int(w), int(h))
    
    try:
        im = pyautogui.screenshot(region=region_ints)
    except Exception:
        # Fallback specifically for potential float errors or out of bounds
        return None

    width, height = im.size
    
    # Search for player color
    # We scan center-out or just linear? Linear is fast enough for small minimaps.
    for x in range(width):
        # Scan Y first? No, X is fine.
        for y in range(height):
            # getpixel locally is 0..width-1
            px = im.getpixel((x, y))
            if colors_match(px, PLAYER_DOT_COLOR, tolerance=10): # Increased tolerance slightly for robustness
                # Return relative X (0..width)
                return x
    return None

def on_press(key):
    global RUNNING, EXIT_PROGRAM, MINIMAP_START_POS, MINIMAP_REGION, PLAYER_DOT_COLOR, HOME_X
    
    try:
        # F8: Start/Stop
        if key == keyboard.Key.f8:
            RUNNING = not RUNNING
            print(f"\n[{'RUNNING' if RUNNING else 'PAUSED'}]")
            if RUNNING:
                print(" -> Pressing Shift every 0.5s")
                print(" -> Pressing L/; every 4.0s")
                if MINIMAP_REGION and HOME_X:
                    print(f" -> Auto-Walking enabled (Home X: {HOME_X})")
                else:
                    print(" -> Auto-Walk DISABLED (Set Minimap F4 & Home F5 first)")

        if key == keyboard.Key.esc:
            EXIT_PROGRAM = True
            return False

        # F4: Set Minimap Region (Top-Left then Bottom-Right)
        if key == keyboard.Key.f4:
            x, y = pyautogui.position()
            if MINIMAP_START_POS is None:
                MINIMAP_START_POS = (x, y)
                print(f"[Minimap] Top-Left: ({x}, {y}). NOW Click Bottom-Right (F4).")
            else:
                x1, y1 = MINIMAP_START_POS
                final_x, final_y = min(x1, x), min(y1, y)
                w, h = abs(x - x1), abs(y - y1)
                MINIMAP_REGION = (final_x, final_y, w, h)
                MINIMAP_START_POS = None
                print(f"[Minimap] Set: {MINIMAP_REGION}")
                save_config()

        # F5: Set Home (Hover over yellow dot on minimap)
        if key == keyboard.Key.f5:
            if not MINIMAP_REGION:
                print("Set Minimap (F4) first!")
                return
            
            x, y = pyautogui.position()
            # Verify mouse is inside minimap
            mx, my, mw, mh = MINIMAP_REGION
            if not (mx <= x <= mx + mw and my <= y <= my + mh):
                print("Error: Mouse not inside defined Minimap region!")
                return

            # Capture color under mouse
            # Robust way for macOS Retina/Multi-monitor
            try:
                im_pixel = pyautogui.screenshot(region=(x, y, 1, 1))
                color = im_pixel.getpixel((0, 0))
            except Exception:
                print("Error: Could not read pixel color. Try ensuring mouse is on screen.")
                return

            PLAYER_DOT_COLOR = color
            
            # Calculate relative X
            HOME_X = x - mx
            
            print(f"[Home] Set! Player Color: {color}, Relative X: {HOME_X}")
            save_config()

    except Exception as e:
        print(f"Key Error: {e}")

# ... (imports)
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
    print("=== Maple Bot (Blind + AutoWalk) ===")
    print("F4: Set Minimap Region (Top-Left -> Bottom-Right)")
    print("F5: Set Home Position (Hover over YOUR yellow dot on minimap)")
    print("F8: Start/Stop")
    print("ESC: Quit")
    print("------------------------------------")
    
    load_config()
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    last_shift = 0
    last_potion = 0
    
    # State for walking
    holding_key = None # 'left' or 'right'

    while not EXIT_PROGRAM:
        if RUNNING:
            now = time.time()

            # 1. Blind Key Presses
            if now - last_shift >= SHIFT_INTERVAL:
                # print(" [Action] Shift") # Uncomment to debug
                press_game_key(KEYS['SHIFT'])
                last_shift = now
            
            if now - last_potion >= POTION_INTERVAL:
                print(" [Action] Potions (; and l)")
                press_game_key(KEYS['POTION_HP']) # ;
                press_game_key(KEYS['POTION_MP']) # l
                last_potion = now

            # 2. Auto-Walk Logic
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
                                    keyboard_controller.release(Key.right)
                                keyboard_controller.press(Key.left)
                                holding_key = 'left'
                        else:
                             # Walk Right
                            if holding_key != 'right':
                                if holding_key: 
                                    keyboard_controller.release(Key.left)
                                keyboard_controller.press(Key.right)
                                holding_key = 'right'
                    else:
                        # Home
                        if holding_key:
                            if holding_key == 'left':
                                keyboard_controller.release(Key.left)
                            if holding_key == 'right':
                                keyboard_controller.release(Key.right)
                            holding_key = None
            
            time.sleep(0.05) 
        
        else:
            if holding_key:
                if holding_key == 'left':
                    keyboard_controller.release(Key.left)
                if holding_key == 'right':
                    keyboard_controller.release(Key.right)
                holding_key = None
            time.sleep(0.1)

    listener.join()

if __name__ == "__main__":
    main()
