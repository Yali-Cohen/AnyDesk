# בס"ד
import threading
from pynput import keyboard
import socket
import json


class KeyboardSender:
    def __init__(self, target_ip, target_port, close_session_callback=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((target_ip, target_port))
        self.stop_event = threading.Event()
        self.thread = None
        self.pressed_keys = set()
        self.close_session_callback = self.close_session_callback
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
            listener.join()

    def serialize_key(self, key):
        """
        הפונקציה הזאת הופכת מקש למבנה שאפשר לשלוח ברשת.
        מקש מיוחד כמו Ctrl / Alt / Tab נשלח לפי שם.
        מקש רגיל כמו A / C / V נשלח לפי vk.
        """

        # מקשים מיוחדים: ctrl, alt, tab, enter, shift וכו'
        if isinstance(key, keyboard.Key):
            return {
                "key_type": "special",
                "key": key.name
            }

        # מקשים רגילים: אותיות, מספרים וכו'
        if hasattr(key, "vk") and key.vk is not None:
            return {
                "key_type": "vk",
                "key": key.vk
            }

        # גיבוי למקרה חריג
        if hasattr(key, "char") and key.char is not None:
            return {
                "key_type": "char",
                "key": key.char
            }

        return None
    def key_id(self, key):
        # מקשים מיוחדים כמו ctrl, shift, alt, tab
        if isinstance(key, keyboard.Key):
            return key.name

        # מקשים רגילים כמו A, C, V, X
        if hasattr(key, "vk") and key.vk is not None:
            return f"vk_{key.vk}"

        # גיבוי לפי תו
        if hasattr(key, "char") and key.char is not None:
            return key.char.lower()

        return str(key)
    def on_press(self, key):
        key_identifier = self.key_id(key)
        self.pressed_keys.add(key_identifier)
        
        if self.is_close_combination():
            self.on_close_combination()
            return
        key_data = self.serialize_key(key)

        if key_data is None:
            return

        data = {
            "type": "key_press",
            **key_data
        }

        print("SENDING PRESS:", data)
        self.send_key_event(data)

    def on_release(self, key):
        key_identifier = self.key_id(key)
        
        if key_identifier in self.pressed_keys:
            self.pressed_keys.remove(key_identifier)
        key_data = self.serialize_key(key)

        if key_data is None:
            return

        data = {
            "type": "key_release",
            **key_data
        }

        print("SENDING RELEASE:", data)
        self.send_key_event(data)

        # כרגע לא עוצרים על ESC, כי אולי נרצה לשלוח ESC למחשב הנשלט

    def send_key_event(self, data):
        message = json.dumps(data) + "\n"
        self.sock.sendall(message.encode("utf-8"))

    def stop(self):
        self.stop_event.set()

        try:
            self.sock.close()
        except OSError:
            pass

        if self.thread is not None:
            self.thread.join(timeout=1)
    def is_close_combination(self):
        ctrl_pressed = "ctrl_l" in self.pressed_keys or "ctrl_r" in self.pressed_keys
        shift_pressed = "shift" in self.pressed_keys or "shift_r" in self.pressed_keys or "shift_l" in self.pressed_keys
        x_pressed = "vk_88" in self.pressed_keys  # vk_88 הוא הקוד של X
        return ctrl_pressed and shift_pressed and x_pressed
    def on_close_combination(self):
        print("Close combination pressed. Stopping keyboard sender.")
        if self.close_session_callback is not None:
            self.close_session_callback()