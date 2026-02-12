import pyautogui
import time
import sys

print("Expected behavior: This script will type 'a' every second.")
print("Focus on a text editor NOW.")
print("You have 5 seconds...")

for i in range(5, 0, -1):
    print(f"{i}...")
    time.sleep(1)

print("Starting to type...")
for i in range(10):
    print(f"Typing 'a' ({i+1}/10)")
    try:
        pyautogui.write('a')
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(1)

print("Done.")
