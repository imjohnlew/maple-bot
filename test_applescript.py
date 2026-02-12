import subprocess
import time

print("Expected behavior: This script will type 'a' every second using AppleScript.")
print("Focus on a text editor NOW.")
print("You have 5 seconds...")

for i in range(5, 0, -1):
    print(f"{i}...")
    time.sleep(1)

print("Starting to type...")
for i in range(10):
    print(f"Typing 'a' ({i+1}/10)")
    try:
        # specific for macos
        cmd = """osascript -e 'tell application "System Events" to keystroke "a"'"""
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(1)

print("Done.")
