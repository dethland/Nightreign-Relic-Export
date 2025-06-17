import trigger
import focused_window
import screen_shot
import keyboard
import relic
import image_process
# from pydirectinput import press
import pydirectinput
import time
import csv

pydirectinput.PAUSE = 0.05

# image_process_server = image_process.ImageProcessor(thread_flag=True)


def test():
    window_name = focused_window.get_active_window_app_name()
    image_process_server = image_process.ImageProcessor(thread_flag=True)
    if window_name == "nightreign.exe":
        print("this is the game")
        relic_array = []
        index = 0
        while True:
            start_time = time.time()
            relic_screenshot = screen_shot.screenshot_relic_description()
            image_process_server.add_screenshot(relic_screenshot)
            # press('right')  # Reduce the duration to make the press shorter
            pydirectinput.keyDown("right")
            # time.sleep(0.1)
            pydirectinput.keyUp("right")
            index += 1
            elapsed = time.time() - start_time
            print(f"Loop {index} took {elapsed:.4f} seconds")
            if index == 20:
                break
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


trigger.code_inject(test)

if __name__ == "__main__":
    trigger.code_inject(test)
    trigger.register_hotkey()
    keyboard.wait('esc')