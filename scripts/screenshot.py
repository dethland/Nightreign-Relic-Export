import os
import mss
from PIL import Image
import win32gui
import win32con
import ctypes


screenshot_folder = "screen_shot_temp"
screen_name = "ELDEN RING NIGHTREIGN"
os.makedirs(screenshot_folder, exist_ok=True)


relic_info_region_tuple = (
    0.5595935912465807, 0.7208333333333333, 0.9163735834310277, 0.9243888888888889)

relic_inventory_region_tuple = (
    0.48125, 0.19537037037037036, 0.9338541666666667, 0.6787037037037037)

progress_bar_region_tuple = (
    0.9427083333333334, 0.21203703703703702, 0.9473958333333333, 0.6574074074074074)

sorting_region_tuple = (0.76796875, 0.15625, 0.835546875, 0.18055555555555555)


try:
    # PROCESS_PER_MONITOR_DPI_AWARE = 2
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    # Fallback for older versions
    ctypes.windll.user32.SetProcessDPIAware()



def get_client_rect(hwnd):
    # Get client rect (no borders, no title bar)
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    left_top = win32gui.ClientToScreen(hwnd, (left, top))
    right_bottom = win32gui.ClientToScreen(hwnd, (right, bottom))
    return (left_top[0], left_top[1], right_bottom[0], right_bottom[1])


def capture_window_content(window_title, region=None):
    hwnd = win32gui.FindWindow(None, window_title)

    x1, y1, x2, y2 = get_client_rect(hwnd)
    print(x1, y1, x2, y2)
    width = x2 - x1
    height = y2 - y1

    if region == None:
        monitor = {
            "top": y1,
            "left": x1,
            "width": width,
            "height": height
        }
    else:
        rx1, ry1, rx2, ry2 = region
        top_pixel = y1 + int(ry1 * height)
        left_pixel = x1 + int(rx1 * width)
        new_width = int(width * (rx2 - rx1))
        new_height = int(height * (ry2 - ry1))
        monitor = {
            "top": top_pixel,
            "left": left_pixel,
            "width": new_width,
            "height": new_height
        }

    with mss.mss() as sct:
        screenshot = sct.grab(monitor)
        img = Image.frombytes(
            "RGB", (screenshot.width, screenshot.height), screenshot.rgb)

    return img


def screenshot_relic_info():
    return capture_window_content(screen_name, relic_info_region_tuple)


def screenshot_relic_inventory():
    return capture_window_content(screen_name, relic_inventory_region_tuple)


def screenshot_progress_bar():
    return capture_window_content(screen_name, progress_bar_region_tuple)


def screenshot_whole():
    return capture_window_content(screen_name)



if __name__ == "__main__":
    # Bring the target window to the foreground first
    hwnd = win32gui.FindWindow(None, screen_name)
    if not hwnd:
        raise Exception(f"Window '{screen_name}' not found")
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)

    img = screenshot_whole()
    other = screenshot_relic_info()
    # other_img = capture_window_content("ELDEN RING NIGHTREIGN")
    if img:
        img.save(os.path.join(screenshot_folder, "screenshot_testing.png"))
        other.save(os.path.join(screenshot_folder, "other_img.png"))
