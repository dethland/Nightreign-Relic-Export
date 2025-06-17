import os
import pygetwindow as gw
import mss
import pytesseract
from PIL import Image
import time
import keyboard


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Folder to save screenshots
screenshot_folder = "screen_shot_temp"
os.makedirs(screenshot_folder, exist_ok=True)

max_screenshots = 10  # Set the number of screenshots to take
turn_wait_time = 0.05

region_left_ratio = 0.56
region_top_ratio = 0.72
region_right_ratio = 0.88
region_down_ratio = 0.92


def screenshot_relic_description():
    win = gw.getActiveWindow()
    with mss.mss() as sct:
        # Get the currently focused window
        if win is not None:
            monitor = {
                "left": int(win.width * region_left_ratio),
                "top": int(win.height * region_top_ratio),
                "width": int(win.width * (region_right_ratio - region_left_ratio)),
                "height": int(win.height * (region_down_ratio - region_top_ratio))
            }
            img = sct.grab(monitor)
            pil_img = Image.frombytes("RGB", img.size, img.rgb)
            return pil_img
        else:
            print("No active window found. Skipping screenshot.")



def screenshot_relic_inventory():
    pass


def screen_shot_region(region):
    win = gw.getActiveWindow()
    if win is None:
        return None
    with mss.mss() as sct:
        img = sct.grab(region)
    


def get_region(my_region_tuple):
    # my_region_tuple = (top, left, right, down)
    win = gw.getActiveWindow()
    if win is None:
        return None
    region = {
        "top": int(win.height * my_region_tuple[0]),
        "left": int(win.width * my_region_tuple[1]),
        "width": int(win.width * (my_region_tuple[2] - my_region_tuple[1])),
        "height": int(win.height * (my_region_tuple[3] - my_region_tuple[0]))
    }
    return region


def main():
    print("Press Ctrl+F12 to take a screenshot of the relic description. Press ESC to exit.")
    screenshot_count = 0
    while screenshot_count < max_screenshots:
        if keyboard.is_pressed('esc'):
            print("Exiting.")
            break
        if keyboard.is_pressed('ctrl+shift+f12'):
            win = gw.getActiveWindow()
           
            img = screenshot_relic_description()
            if img:
                filename = os.path.join(screenshot_folder, f"screenshot_{screenshot_count + 1}.png")
                img.save(filename)
                print(f"Saved {filename}")
                screenshot_count += 1
            time.sleep(0.5)  # Prevent multiple triggers per press
            
        time.sleep(0.05)

if __name__ == "__main__":
    main()