import os
import mss
from PIL import Image
import win32gui
import win32con


# Folder to save screenshots
screenshot_folder = "screen_shot_temp"
screen_name = "ELDEN RING NIGHTREIGN"
os.makedirs(screenshot_folder, exist_ok=True)


relic_info_region_tuple = (0.558984375, 0.7201388888888889, 0.878125, 0.8958333333333334)

relic_invetory_region_tuple = (0.48125, 0.19537037037037036, 0.9338541666666667, 0.6787037037037037)

progress_bar_region_array = (0.9427083333333334, 0.21203703703703702, 0.9473958333333333, 0.6574074074074074)

sorting_region_tuple = (0.76796875, 0.15625, 0.835546875, 0.18055555555555555)

    



def screenshot_relic_info():
    return capture_window_content(screen_name, relic_info_region_tuple)


def screenshot_relic_inventory():
    return capture_window_content(screen_name, relic_invetory_region_tuple)


def screenshot_progress_bar():
    return capture_window_content(screen_name, progress_bar_region_array)


def screenshot_whole():
    return capture_window_content(screen_name)


def tuple_to_crop_box(region_tuple, img_size):
    """
    Convert a region tuple (top_left_x_margin, top_left_y_margin, size_x, size_y)
    with margin values in 0-1, to a crop box (left, top, right, bottom) in pixels.
    """
    img_width, img_height = img_size
    left = int(region_tuple[0] * img_width)
    top = int(region_tuple[1] * img_height)
    right = left + int(region_tuple[2] * img_width)
    bottom = top + int(region_tuple[3] * img_height)
    return (left, top, right, bottom)



def capture_window_content(window_title, region=None):
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        raise Exception(f"Window '{window_title}' not found")


    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)

    # Get client area coordinates
    x1, y1, x2, y2 = get_client_rect(hwnd)
    width = x2 - x1
    height = y2 - y1
    
    if region == None:
        region = (0, 0, 1, 1)

    rx1, ry1, rx2, ry2 = region
    new_width = int(width * (rx2 - rx1))
    new_height = int(height * (ry2 - ry1))

    # Use mss to capture that region
    with mss.mss() as sct:
        monitor = {"top": y1+int(ry1*height), "left": x1 + int(rx1 * width), "width": new_width, "height": new_height}
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)

    return img


def get_client_rect(hwnd):
    # Get client rect (no borders, no title bar)
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    # Convert client coords to screen coords
    left_top = win32gui.ClientToScreen(hwnd, (left, top))
    right_bottom = win32gui.ClientToScreen(hwnd, (right, bottom))
    return (left_top[0], left_top[1], right_bottom[0], right_bottom[1])



def get_region(my_region_tuple):
    # my_region_tuple = (top, left, right, down)
    hwnd = win32gui.FindWindow(None, "ELDEN RING NIGHTREIGN")
    window_tuple = get_client_rect(hwnd)
 
    region = {
        "top": int(window_tuple[2] * my_region_tuple[1]),
        "left": int(window_tuple[3] * my_region_tuple[0]),
        "width": int(window_tuple[2] * (my_region_tuple[2] - my_region_tuple[0])),
        "height": int(window_tuple[3] * (my_region_tuple[3] - my_region_tuple[1]))
    }
    return region



if __name__ == "__main__":
    img = screenshot_whole()
    other = screenshot_progress_bar()
    # other_img = capture_window_content("ELDEN RING NIGHTREIGN")
    if img:
        img.save(os.path.join(screenshot_folder, "screenshot_testing.png"))
        other.save(os.path.join(screenshot_folder, "other_img.png"))
    # test_img_size = (1920, 1080)
    # test_region_tuple = (0.1, 0.2, 0.5, 0.3)
    # crop_box = tuple_to_crop_box(test_region_tuple, test_img_size)
    # print(f"Test region tuple: {test_region_tuple}")
    # print(f"Image size: {test_img_size}")
    # print(f"Crop box (left, top, right, bottom): {crop_box}")
