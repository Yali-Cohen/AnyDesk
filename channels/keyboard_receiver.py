#Receiver
import socket
from pynput.keyboard import Key, Controller
import json
import threading

class KeyboardReceiver:
    def __init__(self,sock:socket.socket):
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
        while not self.stop_event.is_set():
            data = self.sock.recv(1024).decode()
            print("Received:", data)
            if data:
                try:
                    data = json.loads(data)
                    if data["type"] == "key_press":
                        key = data["key"]
                        if len(key) == 1:
                            self.keyboard.press(key)
                        else:
                            self.keyboard.press(getattr(Key, key.replace("Key.", "")))
                    elif data["type"] == "key_release":
                        key = data["key"]
                        if len(key) == 1:
                            self.keyboard.release(key)
                        else:
                            self.keyboard.release(getattr(Key, key.replace("Key.", "")))
                except Exception as e:
                    print("Error processing data:", e)
    def stop(self):
        self.stop_event.set()
        self.sock.close()
        if self.thread is not None:
            self.thread.join(timeout=1)