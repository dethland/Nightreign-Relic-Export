import os
import time
import csv
import keyboard
import pydirectinput
import win32gui

import trigger
import screenshot
import imageproc

setting = {}

ELDEN_RING_WINDOW_NAME = "ELDEN RING NIGHTREIGN"
pydirectinput.PAUSE = 0
previous_progress = None
progress_bar_delta = 0.0


def read_setting_file():
    """Reads the setting.txt file from the parent directory and returns its contents as a string."""
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    setting_path = os.path.join(parent_dir, "setting.txt")
    raw = None
    setting = {}
    with open(setting_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # Convert setting.txt content (pure text) into SETTINGS dict
    for line in raw.split("\n"):
        if line.count("=") == 1 and line.count("#") == 0:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            # Try to convert value to int or float if possible
            if value.isdigit():
                value = int(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass
            setting[key] = value
    return setting


def get_active_window_app_name():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)


def write_to_csv(result, filename="result.csv"):
    """
    Writes the result (a list of lists) to a CSV file.
    Each inner list represents a row. Rows are padded to the length of the longest row.
    The CSV is always saved in the 'export' folder at the same level as this script.
    """
    if not result:
        print("No results to write to CSV.")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(script_dir, "export")
    os.makedirs(export_dir, exist_ok=True)
    export_path = os.path.join(export_dir, filename)

    max_len = max(len(row) for row in result)
    with open(export_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for row in result:
            writer.writerow(list(row) + [""] * (max_len - len(row)))


def should_continue() -> bool:
    """
    Takes a screenshot of the progress bar, extracts the progress margin,
    and determines whether to continue based on the change in progress.
    Returns True to continue, False to stop.
    """
    if get_active_window_app_name() != ELDEN_RING_WINDOW_NAME:
        return False

    global previous_progress, progress_bar_delta

    progress_bar_screenshot = screenshot.screenshot_progress_bar()
    processor = imageproc.ImageProcessor(thread_flag=False)
    margin = processor.extract_progress_bar(progress_bar_screenshot)

    if previous_progress is None:
        previous_progress = margin
        return True

    progress_bar_delta = margin - previous_progress
    previous_progress = margin

    return progress_bar_delta >= 0


def after_confirm():
    if get_active_window_app_name() != ELDEN_RING_WINDOW_NAME:
        return

    processor = imageproc.ImageProcessor(thread_flag=True, ocr_path=setting["ocr_exe_filepath"], num_threads=setting["thread_number"])
    try:
        while should_continue():
            processor.add_screenshot(screenshot.screenshot_relic_info())
            pydirectinput.keyDown("right")
            time.sleep(setting["key_press_duration"])
            pydirectinput.keyUp("right")
            time.sleep(setting["key_press_delay"])
            if keyboard.is_pressed("ctrl+shift+f12"):
                print("\n----break key pressed----\nprocessing remaining images")
                break
    finally:
        processor.stop()
        write_to_csv(processor.get_result())
        print("\n" + "=" * 40)
        print("🎉 Export complete! Your relic data has been saved to result.csv.")
        print("=" * 40 + "\n")


def main():
    print("=" * 40)
    print("✨ Nightreign Relic Export is running! ✨")
    print("Press the 'ctrl + shift + f12' in-game to start export.")
    print("Press hotkeys again to break the loop ")
    print("Press ESC to exit.")
    print("=" * 40)
    trigger.code_inject(after_confirm)
    trigger.register_hotkey()
    keyboard.wait('esc')


if __name__ == "__main__":
    setting = read_setting_file()
    main()
