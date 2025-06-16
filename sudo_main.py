import trigger
import focused_window
import screen_shot
import keyboard


def test():
    window_name = focused_window.get_active_window_app_name()
    if window_name == "nightreign.exe":
        print("this is the game")
        screen_shot.shot_and_turn()


trigger.code_inject(test)

if __name__ == "__main__":
    trigger.register_hotkey()
    keyboard.wait('esc')