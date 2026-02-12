import pyautogui
import time

print("=== Color Inspector Tool ===")
print("Hover over your HP/MP bar to check the color values.")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        x, y = pyautogui.position()
        try:
            # Get color at mouse position
            color = pyautogui.pixel(x, y)
            
            # Print cleanly on one line
            # format: (R, G, B) at (X, Y)
            print(f"\r Pos: ({x:4}, {y:4})  Color: {color}   ", end="", flush=True)
        except Exception as e:
            pass
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopped.")
