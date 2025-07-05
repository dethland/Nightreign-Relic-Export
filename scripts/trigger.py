import keyboard

inject_code = None


def on_hotkey():
    # Invoke inject_code if it's set
    if inject_code is not None:
        inject_code()
    else:
        print("Error: no inject code provided")


def code_inject(callable_func):
    global inject_code
    inject_code = callable_func


def register_hotkey():
    # Register the hotkey: Ctrl + Shift + F12
    keyboard.add_hotkey('ctrl+shift+f12', on_hotkey)

