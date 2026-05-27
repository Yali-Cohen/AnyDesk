# Receiver
import socket
from pynput.keyboard import Key, KeyCode, Controller
import json
import threading


class KeyboardReceiver:
    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.stop_event = threading.Event()
        self.thread = None
        self.keyboard = Controller()

    def start(self):
        if self.thread is not None and self.thread.is_alive():
            return

        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        buffer = ""

        while not self.stop_event.is_set():
            try:
                chunk = self.sock.recv(1024)
            except OSError:
                break

            if not chunk:
                break

            buffer += chunk.decode("utf-8")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                if not line.strip():
                    continue

                try:
                    data = json.loads(line)
                    print("RECEIVED:", data)
                    self.handle_key_event(data)

                except Exception as e:
                    print("Error processing keyboard message:", e)

    def deserialize_key(self, data):
        """
        הפונקציה הזאת מקבלת מידע שהגיע מהרשת
        ומחזירה אובייקט מקש ש-pynput יודע ללחוץ עליו.
        """

        key_type = data.get("key_type")
        key = data.get("key")

        # מקשים מיוחדים: ctrl, alt, tab, enter וכו'
        if key_type == "special":
            return getattr(Key, key)

        # מקשים רגילים לפי Virtual Key Code
        if key_type == "vk":
            return KeyCode.from_vk(key)

        # גיבוי למקשים רגילים לפי תו
        if key_type == "char":
            return key

        return None

    def handle_key_event(self, data):
        real_key = self.deserialize_key(data)

        if real_key is None:
            return

        if data["type"] == "key_press":
            self.keyboard.press(real_key)

        elif data["type"] == "key_release":
            self.keyboard.release(real_key)

    def stop(self):
        self.stop_event.set()

        try:
            self.sock.close()
        except OSError:
            pass

        if self.thread is not None:
            self.thread.join(timeout=1)