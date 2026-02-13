import pyautogui
import time
import sys
from pynput import keyboard

import json
import os

# Configuration
TOTAL_ITEMS = 10000
MAX_PER_BUY = 200
LOOPS = TOTAL_ITEMS // MAX_PER_BUY  # 50 loops
DELAY_BETWEEN_ACTIONS = 0.5  # Time to wait after click/type
AUTOBUY_CONFIG_FILE = "autobuy_config.json"

# Fail-safe (Move mouse to corner to abort)
pyautogui.FAILSAFE = True

# Global State
running_buy_sequence = False
stop_requested = False
INPUT_BOX_POS = None  # Stores (x, y) of the input box
CONFIRM_BTN_POS = None # Stores (x, y) of the Confirm button

def load_config():
    global INPUT_BOX_POS, CONFIRM_BTN_POS
    if os.path.exists(AUTOBUY_CONFIG_FILE):
        try:
            with open(AUTOBUY_CONFIG_FILE, 'r') as f:
                data = json.load(f)
                INPUT_BOX_POS = tuple(data.get('INPUT_BOX_POS')) if data.get('INPUT_BOX_POS') else None
                CONFIRM_BTN_POS = tuple(data.get('CONFIRM_BTN_POS')) if data.get('CONFIRM_BTN_POS') else None
                if INPUT_BOX_POS: print(f"[Config] Loaded Input Position: {INPUT_BOX_POS}")
                if CONFIRM_BTN_POS: print(f"[Config] Loaded Confirm Position: {CONFIRM_BTN_POS}")
        except Exception as e:
            print(f"[Config] Error loading: {e}")

def save_config():
    data = {
        'INPUT_BOX_POS': INPUT_BOX_POS,
        'CONFIRM_BTN_POS': CONFIRM_BTN_POS
    }
    try:
        with open(AUTOBUY_CONFIG_FILE, 'w') as f:
            json.dump(data, f)
        print("[Config] Saved positions to file.")
    except Exception as e:
        print(f"[Config] Error saving: {e}")

def on_press(key):
    global running_buy_sequence, stop_requested, INPUT_BOX_POS, CONFIRM_BTN_POS
    try:
        if key == keyboard.Key.f8:
            x, y = pyautogui.position()
            CONFIRM_BTN_POS = (x, y)
            print(f"\n[Set] Confirm Button location saved at ({x}, {y})")
            save_config()

        elif key == keyboard.Key.f9:
            x, y = pyautogui.position()
            INPUT_BOX_POS = (x, y)
            print(f"\n[Set] Input Box location saved at ({x}, {y})")
            save_config()
            
        elif key == keyboard.Key.f10:
            if not running_buy_sequence:
                if INPUT_BOX_POS is None:
                    print("\n[Error] Please set the Input Box location first (Press F9)!")
                elif CONFIRM_BTN_POS is None:
                    print("\n[Error] Please set the Confirm Button location first (Press F8)!")
                else:
                    print("\n[Start] F10 pressed - Starting buy loop...")
                    running_buy_sequence = True
                    
        elif key == keyboard.Key.esc:
            print("\n[Stop] ESC pressed - Stopping...")
            stop_requested = True
            return False
    except AttributeError:
        pass

def perform_buy_loop():
    global running_buy_sequence, stop_requested, INPUT_BOX_POS, CONFIRM_BTN_POS
    
    # Capture the item location immediately when loop starts (where user hovered)
    item_x, item_y = pyautogui.position()
    print(f" -> Item Location captured at ({item_x}, {item_y})")
    
    print(f" -> Will attempt to buy {LOOPS} batches of {MAX_PER_BUY} items.")
    
    for i in range(LOOPS):
        if stop_requested:
            print("\n[Stopped] Sequence aborted by user.")
            break
            
        print(f" -> Buying Batch {i+1}/{LOOPS}")
        
        # 1. Click Item (Explicit double click)
        pyautogui.moveTo(item_x, item_y)
        pyautogui.click()
        time.sleep(0.08)
        pyautogui.click()
        
        time.sleep(0.8) # Wait for dialog (Reduced slightly for speed)
        
        # 2. Click Input Box
        if INPUT_BOX_POS:
            pyautogui.click(INPUT_BOX_POS)
            time.sleep(0.15)
        
        # 3. Type '200'
        pyautogui.write(str(MAX_PER_BUY), interval=0.05) # Slightly faster typing
        time.sleep(0.2)
        
        # 4. Click Confirm Button (Instead of Enter)
        if CONFIRM_BTN_POS:
            pyautogui.click(CONFIRM_BTN_POS)
            time.sleep(0.3)
        
        # Buffer for network/animation
        time.sleep(0.5)
        
    print("\n[Done] Buy sequence finished.")
    running_buy_sequence = False

def main():
    print("=== MapleShop Auto-Buyer ===")
    print(f"Target: Buy {TOTAL_ITEMS} items (Stacks of {MAX_PER_BUY})")
    print("---------------------------------")
    print("1. Open Shop Window & Double click an item manually to open the dialog.")
    print("2. Hover mouse over the INPUT BOX (where you type number).")
    print("3. Press [F9] to save this Input Box location.")
    print("4. Hover mouse over the CONFIRM BUTTON (Yellow button).")
    print("5. Press [F8] to save Confirm Button location.")
    print("   (You can close the dialog manually now)")
    print("---------------------------------")
    print("6. Hover mouse over the ITEM you want to buy.")
    print("7. Press [F10] to start the auto-buy loop.")
    print("8. Press [ESC] to stop instantly.")
    print("---------------------------------")

    # Load previously saved locations
    load_config()

    # Start listener in non-blocking way
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    global running_buy_sequence, stop_requested
    try:
        while not stop_requested:
            if running_buy_sequence:
                perform_buy_loop()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()

if __name__ == "__main__":
    main()
