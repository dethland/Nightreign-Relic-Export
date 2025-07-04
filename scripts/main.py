import trigger
import screenshot
import imageproc
import keyboard  # key detection
import pydirectinput  # simulate input
import csv
import win32gui
import os


# TODO move the trigger functions into main

previous_progress = None
progress_bar_delta = 0.0

elden_ring_window_name = "ELDEN RING NIGHTREIGN"

pydirectinput.PAUSE = 0.05


def get_active_window_app_name():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)


def after_confirm():
    if get_active_window_app_name() != elden_ring_window_name:
        return

    processor = imageproc.ImageProcessor(thread_flag=True)
    try:
        while should_continue():
            processor.add_screenshot(screenshot.screenshot_relic_info())
            pydirectinput.press("right")
    finally:
        processor.stop()
        write_to_csv(processor.get_result())
        print("\n" + "="*40)
        print("🎉 Export complete! Your relic data has been saved to result.csv.")
        print("="*40 + "\n")


def write_to_csv(result, filename="result.csv"):
    """
    Writes the result (a list of lists) to a CSV file.
    Each inner list represents a row. Rows are padded to the length of the longest row.
    The CSV is always saved in the 'export' folder at the same level as this script.
    """
    if not result:
        print("No results to write to CSV.")
        return

    # Get the directory where this script is located
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


if __name__ == "__main__":
    trigger.code_inject(after_confirm)
    trigger.register_hotkey()
    keyboard.wait('esc')
