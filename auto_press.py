import time
import threading
from pynput import keyboard
from pynput.keyboard import Controller, Key

# Default settings
KEY_TO_PRESS = Key.space
INTERVAL = 0.5
RUNNING = False
EXIT_PROGRAM = False

keyboard_controller = Controller()

def on_press(key):
    global RUNNING, EXIT_PROGRAM
    try:
        if key == Key.esc:
            print("\nExiting program...")
            RUNNING = False
            EXIT_PROGRAM = True
            return False  # Stop listener
        elif key == Key.f8:  # Optional: Toggle with F8
            RUNNING = not RUNNING
            state = "Running" if RUNNING else "Paused"
            print(f"\n[{state}] Press F8 to toggle, ESC to exit.")
    except AttributeError:
        pass

def press_worker():
    while not EXIT_PROGRAM:
        if RUNNING:
            keyboard_controller.press(KEY_TO_PRESS)
            keyboard_controller.release(KEY_TO_PRESS)
            print(".", end="", flush=True)  # Visual feedback
            time.sleep(INTERVAL)
        else:
            time.sleep(0.1)

def main():
    global KEY_TO_PRESS, INTERVAL, RUNNING
    
    print("--- Auto Key Presser ---")
    print("Default key: SPACE")
    print("Default interval: 0.5 seconds")
    
    user_key = input("Enter key to press (leave empty for SPACE, type 'enter' for ENTER): ").strip().lower()
    if user_key == 'enter':
        KEY_TO_PRESS = Key.enter
    elif user_key:
        if len(user_key) == 1:
            KEY_TO_PRESS = user_key
        else:
            print("Invalid key length, using default SPACE.")

    user_interval = input("Enter interval in seconds (default 0.5): ").strip()
    if user_interval:
        try:
            INTERVAL = float(user_interval)
        except ValueError:
            print("Invalid number, using default 0.5s.")

    print(f"\nSettings: Pressing '{KEY_TO_PRESS}' every {INTERVAL}s.")
    print("Instructions:")
    print("1. Press F8 to START/STOP the pressing.")
    print("2. Press ESC to QUIT the program.")
    
    # Start the key pressing thread
    t = threading.Thread(target=press_worker)
    t.start()

    # Start the listener (blocking)
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
    
    t.join()

if __name__ == "__main__":
    main()
