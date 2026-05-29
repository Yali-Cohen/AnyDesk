# בס"ד
import threading
import keyboard as system_keyboard


stop_event = threading.Event()
pressed_keys = set()


def on_keyboard_event(event):
    key = event.name.lower()
    event_type = event.event_type

    print("KEY EVENT:", key, event_type)

    if event_type == "down":
        pressed_keys.add(key)

    elif event_type == "up":
        pressed_keys.discard(key)

    print("PRESSED NOW:", pressed_keys)

    ctrl_pressed = "ctrl" in pressed_keys
    shift_pressed = "shift" in pressed_keys
    x_pressed = "x" in pressed_keys

    print(f"CTRL: {ctrl_pressed}, SHIFT: {shift_pressed}, X: {x_pressed}")

    if ctrl_pressed and shift_pressed and x_pressed:
        print("Exit detected")
        system_keyboard.unhook_all()
        stop_event.set()
system_keyboard.hook(on_keyboard_event, suppress=True)

print("Test started")
print("Press keys. Press Ctrl+Shift+X to exit.")

while not stop_event.is_set():
    system_keyboard.wait("esc")