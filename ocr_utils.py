import pytesseract
from PIL import Image, ImageOps
import re

# Set tesseract path explicitly for Apple Silicon if needed
# Try standard paths if not found in PATH
import shutil
TESS_CMD = shutil.which("tesseract")
if not TESS_CMD:
    TESS_CMD = "/opt/homebrew/bin/tesseract"
    
pytesseract.pytesseract.tesseract_cmd = TESS_CMD

def preprocess_image(im):
    # Convert to grayscale
    gray = ImageOps.grayscale(im)
    # Binarize: Make text black, background white (or vice versa)
    # Assuming text is bright (white) on dark (red/blue/gray)
    # Threshold at 150-200.
    thresh = gray.point(lambda p: 255 if p > 180 else 0)
    return thresh

def extract_numbers(text):
    # Matches "1234/5678" or "1234 / 5678"
    # Also handles common OCR errors: "l" for "1", "O" for "0", "|" for "/"
    
    clean = text.replace("l", "1").replace("I", "1").replace("O", "0").replace("|", "/")
    
    # Regex for "number / number"
    match = re.search(r"([\d.,]+)\s*/\s*([\d.,]+)", clean)
    if match:
        curr_s = match.group(1).replace(",", "").replace(".", "")
        max_s = match.group(2).replace(",", "").replace(".", "")
        try:
            return int(curr_s), int(max_s)
        except:
            pass
            
    # Regex for single number (percentage?) or just current value
    # match = re.search(r"([\d.,]+)", clean)
    return None, None

def ocr_region(start_x, start_y, end_x, end_y):
    import pyautogui
    width = end_x - start_x
    height = end_y - start_y
    if width < 1 or height < 1:
        return None, "Invalid Region"
        
    try:
        # Capture
        im = pyautogui.screenshot(region=(start_x, start_y, width, height))
        # Preprocess
        proc_im = preprocess_image(im)
        # OCR
        # psm 7 = Treat the image as a single text line.
        text = pytesseract.image_to_string(proc_im, config='--psm 7')
        return proc_im, text.strip()
    except Exception as e:
        return None, str(e)
