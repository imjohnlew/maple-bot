import pyautogui
import sys
from PIL import Image

print(f"Platform: {sys.platform}")
print(f"Screen Size (Main): {pyautogui.size()}")

try:
    # Use coordinates known to be from the secondary monitor based on previous logs
    # Or fallback to mouse if mouse is already in that region
    # But coordinate (3292, 2044) was logged previously.
    test_coords = [(3292, 2044), pyautogui.position()]
    
    for (x, y) in test_coords:
        print(f"\n--- Testing Coordinate ({x}, {y}) ---")
        
        # Try capturing region
        try:
            # On macOS, region is (left, top, width, height)
            im = pyautogui.screenshot(region=(x, y, 1, 1))
            color = im.getpixel((0, 0))
            print(f"SUCCESS: Captured region at ({x}, {y}) -> Color: {color}")
        except Exception as e:
            print(f"FAILED: region capture at ({x}, {y}): {e}")

        # Try direct pixel()
        try:
            color = pyautogui.pixel(x, y)
            print(f"Direct pixel() call at ({x}, {y}): {color}")
        except Exception as e:
            print(f"Direct pixel() call failed: {e}")

except Exception as e:
    print(f"General Error: {e}")
