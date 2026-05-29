# בס"ד
import threading
import socket
import json
import time
import keyboard as system_keyboard
class KeyboardSender:
    def __init__(self, target_ip, target_port, close_session_callback=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((target_ip, target_port))
        self.stop_event = threading.Event()
        self.thread = None
        self.pressed_keys = set()
        self.close_session_callback = close_session_callback
    def start(self):
        if self.thread is not None and self.thread.is_alive():
            return

        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        system_keyboard.hook(self.on_keyboard_event, suppress=True)

        while not self.stop_event.is_set():
            time.sleep(0.05)
    def on_keyboard_event(self, event):
        original_key = event.name
        key_for_logic = original_key.lower()
        event_type = event.event_type

        print("KEY EVENT:", original_key, event_type)

        if event_type == "down":
            self.pressed_keys.add(key_for_logic)

        elif event_type == "up":
            self.pressed_keys.discard(key_for_logic)

        if self.is_close_combination():
            self.on_close_combination()
            return

        data = {
            "type": "key_press" if event_type == "down" else "key_release",
            "key_type": "name",
            "key": key_for_logic
        }

        print("SENDING KEY:", data)
        self.send_key_event(data)
        
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
        x_pressed = "x" in self.pressed_keys
        return ctrl_pressed and shift_pressed and x_pressed
    def on_close_combination(self):
        print("Close combination pressed. Stopping keyboard sender.")
        if self.close_session_callback is not None:
            self.close_session_callback()