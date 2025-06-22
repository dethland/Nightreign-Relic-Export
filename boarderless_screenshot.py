import win32gui
import win32con
import win32api
import mss
from PIL import Image

def get_client_rect(hwnd):
    # Get client rect (no borders, no title bar)
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    # Convert client coords to screen coords
    left_top = win32gui.ClientToScreen(hwnd, (left, top))
    right_bottom = win32gui.ClientToScreen(hwnd, (right, bottom))
    return (left_top[0], left_top[1], right_bottom[0], right_bottom[1])

def capture_window_content(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        raise Exception(f"Window '{window_title}' not found")

    # Bring to front
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)

    # Get client area coordinates
    x1, y1, x2, y2 = get_client_rect(hwnd)
    width = x2 - x1
    height = y2 - y1

    # Use mss to capture that region
    with mss.mss() as sct:
        monitor = {"top": y1, "left": x1, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)

    return img

# Example use
if __name__ == "__main__":
    img = capture_window_content("ELDEN RING NIGHTREIGN")  # Replace with your target window title
    img.show()  # Display image
    img.save("window_capture.png")  # Or save it
