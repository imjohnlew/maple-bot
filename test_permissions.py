import pyautogui
import time
import sys
from pynput.keyboard import Controller, Key

def test_screen_recording():
    print("--- Testing Screen Recording Permission ---")
    try:
        # Attempt to take a small screenshot
        img = pyautogui.screenshot(region=(0, 0, 100, 100))
        print("✅ Screenshot successful!")
        return True
    except Exception as e:
        print(f"❌ Screenshot FAILED: {e}")
        print("Please check: System Settings > Privacy & Security > Screen Recording")
        return False

def test_accessibility():
    print("\n--- Testing Accessibility Permission (Keyboard Control) ---")
    keyboard = Controller()
    try:
        # Attempt to press a benign key (like Shift)
        keyboard.press(Key.shift)
        time.sleep(0.1)
        keyboard.release(Key.shift)
        print("✅ Keyboard press successful!")
        return True
    except Exception as e:
        print(f"❌ Keyboard press FAILED: {e}")
        print("Please check: System Settings > Privacy & Security > Accessibility")
        return False

if __name__ == "__main__":
    print("Running MacOS Permission Test (Do NOT use sudo)...")
    time.sleep(1)
    
    screen_ok = test_screen_recording()
    access_ok = test_accessibility()
    
    if screen_ok and access_ok:
        print("\n🎉 All permissions appear to be correct!")
    else:
        print("\n⚠️  Permissions missing. Please grant permissions to your Terminal application (e.g., iTerm, Terminal, VSCode).")
