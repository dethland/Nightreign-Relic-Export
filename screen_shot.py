import os
# import time
from pydirectinput import press
import pygetwindow as gw
import mss

# Folder to save screenshots
screenshot_folder = "screen_shot_temp"
os.makedirs(screenshot_folder, exist_ok=True)

max_screenshots = 10  # Set the number of screenshots to take
turn_wait_time = 0.05

region_left_ratio = 0.56
region_top_ratio = 0.72
region_right_ratio = 0.88
region_down_ratio = 0.92

test_ram_array = []

def shot_and_turn():
    global test_ram_array
    win = gw.getActiveWindow()
    with mss.mss() as sct:
        for count in range(1, max_screenshots + 1):
            # Get the currently focused window
            if win is not None:
                monitor = {
                    "left": int(win.width * region_left_ratio),
                    "top": int(win.height * region_top_ratio),
                    "width": int(win.width * (region_right_ratio - region_left_ratio)),
                    "height": int(win.height * (region_down_ratio - region_top_ratio))
                }
                # print(
                #     f"Debug: left={win.left * region_left_ratio} (int={int(win.left * region_left_ratio)}), "
                #     f"top={win.top * region_top_ratio} (int={int(win.top * region_top_ratio)})"
                # )

                img = sct.grab(monitor)
                test_ram_array.append(img)
                # timestamp = time.strftime("%Y%m%d_%H%M%S")
                # filename = os.path.join(screenshot_folder, f"screenshot_{timestamp}.png")
                # mss.tools.to_png(img.rgb, img.size, output=filename)
                # print(f"Screenshot {count}/{max_screenshots} saved to {filename}")
            else:
                print("No active window found. Skipping screenshot.")

            press('right')
            
    for idx, img in enumerate(test_ram_array, 1):
        filename = os.path.join(screenshot_folder, f"screenshot_{idx}.png")
        mss.tools.to_png(img.rgb, img.size, output=filename)