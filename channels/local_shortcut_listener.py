# בס"ד
import threading
from pynput import keyboard


class LocalShortcutListener:
    def __init__(self, close_session_callback=None):
        self.stop_event = threading.Event()
        self.thread = None
        self.pressed_keys = set()
        self.close_session_callback = close_session_callback
        self.listener = None

    def start(self):
        if self.thread is not None and self.thread.is_alive():
            return

        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        ) as listener:
            self.listener = listener
            listener.join()

    def key_id(self, key):
        if isinstance(key, keyboard.Key):
            return key.name

        if hasattr(key, "vk") and key.vk is not None:
            return f"vk_{key.vk}"

        if hasattr(key, "char") and key.char is not None:
            return key.char.lower()

        return str(key)

    def on_press(self, key):
        if self.stop_event.is_set():
            return False

        key_identifier = self.key_id(key)
        self.pressed_keys.add(key_identifier)

        if self.is_close_combination():
            print("Local close shortcut detected.")

            if self.close_session_callback is not None:
                self.close_session_callback()

            return False

    def on_release(self, key):
        key_identifier = self.key_id(key)

        if key_identifier in self.pressed_keys:
            self.pressed_keys.remove(key_identifier)

    def is_close_combination(self):
        ctrl_pressed = (
            "ctrl_l" in self.pressed_keys or
            "ctrl_r" in self.pressed_keys
        )

        shift_pressed = (
            "shift" in self.pressed_keys or
            "shift_l" in self.pressed_keys or
            "shift_r" in self.pressed_keys
        )

        x_pressed = "vk_88" in self.pressed_keys

        return ctrl_pressed and shift_pressed and x_pressed

    def stop(self):
        self.stop_event.set()

        if self.listener is not None:
            self.listener.stop()

        if self.thread is not None and self.thread is not threading.current_thread():
            self.thread.join(timeout=1)