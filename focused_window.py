import time
import win32gui
import win32process
import psutil

UPDATE_INTERVAL = 1  # seconds

def get_active_window_app_name():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == 0:
        return None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        process = psutil.Process(pid)
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

if __name__ == "__main__":
    last_app = None
    while True:
        app_name = get_active_window_app_name()
        if app_name != last_app and app_name is not None:
            print(f"Focused application: {app_name}")
            last_app = app_name
        time.sleep(UPDATE_INTERVAL)