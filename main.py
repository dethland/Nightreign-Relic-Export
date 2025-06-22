import trigger
import focused_window
import screenshot
import keyboard
import relic
import image_process
# from pydirectinput import press
import pydirectinput
import csv

pydirectinput.PAUSE = 0.05


def after_confirm():
    window_name = focused_window.get_active_window_app_name()
    image_process_server = image_process.ImageProcessor(thread_flag=True)
    if window_name == "nightreign.exe":
        print("this is the game")
        relic_array = []
        index = 0
        loop_flag = True
        progress_bar_screenshot = screenshot.screenshot_progress_bar

        while loop_flag:
            relic_screenshot = screenshot.screenshot_relic_info()
            # relic_screenshot = relic_screenshot.resize(
            #     (relic_screenshot.width // 2, relic_screenshot.height // 2)
            # )
            image_process_server.add_screenshot(relic_screenshot)
            #simulate key press
            pydirectinput.keyDown("right")
            pydirectinput.keyUp("right")
            #keep track relic index
            index += 1
            # if index == 10:
            #     break
            #print screen shot time 
            #check if get all screen shot
            loop_flag = should_continue()
        #recover result and terminate server
        image_process_server.stop()
        result = image_process_server.get_result()

        with open("result.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            max_len = max(len(item) for item in result)
            for item in result:
                row = list(item) + [""] * (max_len - len(item))
                writer.writerow(row)
        print("CSV export complete.")
        print(result)


def should_continue() -> bool:
    # we take screen shot of progress_bar, then push it into image_process using progress bar extract
    # thte progress bar extract will return us margin value 0-1, compare the value with threshold to know if the 
    progress_bar_screenshot = screenshot.screenshot_progress_bar()
    processor = image_process.ImageProcessor(thread_flag=False)
    margin = processor.extract_progress_bar(progress_bar_screenshot)
    return not margin >= 0.9980
    

  

if __name__ == "__main__":
    trigger.code_inject(after_confirm)
    trigger.register_hotkey()
    keyboard.wait('esc')