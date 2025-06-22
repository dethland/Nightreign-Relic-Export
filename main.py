import trigger
import focused_window
import screenshot
import image_process
import keyboard
import pydirectinput
import csv

pydirectinput.PAUSE = 0.05


def after_confirm():
    window_name = focused_window.get_active_window_app_name()
    if window_name != "nightreign.exe":
        return

    image_process_server = image_process.ImageProcessor(thread_flag=True)
    loop_flag = True

    while loop_flag:
        # get screenshot and put into processor
        relic_screenshot = screenshot.screenshot_relic_info()
        image_process_server.add_screenshot(relic_screenshot)
        # simulate key press
        pydirectinput.keyDown("right")
        pydirectinput.keyUp("right")
        # check continue
        loop_flag = should_continue()

    # recover result and terminate server
    image_process_server.stop()
    result = image_process_server.get_result()

    # export into csv
    write_to_csv(result)


def write_to_csv(result):
    # result is expected to be a list of lists, where each inner list has 2 to 4 elements.
    # Each inner list represents a row to be written to the CSV file.
    with open("result.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if result:
            max_len = max(len(item) for item in result)
            for item in result:
                row = list(item) + [""] * (max_len - len(item))
                writer.writerow(row)
        else:
            print("No results to write to CSV.")


def should_continue() -> bool:
    # we take screen shot of progress_bar, then push it into image_process using progress bar extract
    # thte progress bar extract will return us margin value 0-1, compare the value with threshold to know if the
    # FIXME need update to iterate through relic that are at the bottom 2 row
    progress_bar_screenshot = screenshot.screenshot_progress_bar()
    processor = image_process.ImageProcessor(thread_flag=False)
    margin = processor.extract_progress_bar(progress_bar_screenshot)
    return not margin >= 0.9980


if __name__ == "__main__":
    trigger.code_inject(after_confirm)
    trigger.register_hotkey()
    keyboard.wait('esc')
