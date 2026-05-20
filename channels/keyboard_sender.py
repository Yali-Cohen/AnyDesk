# בס"ד
import threading
from pynput import keyboard
import socket
import json    

class KeyboardSender:
    def __init__(self, target_ip, target_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((target_ip,target_port))
        self.stop_event = threading.Event()
        self.thread = None
    def start(self):
        if self.thread is not None and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
    def run(self):
        with keyboard.Listener(
        on_press=self.on_press,
        on_release=self.on_release) as listener:
            listener.join()
    def on_press(self, key):
        try:
            print(f'Alphanumeric key {key.char!r} pressed')
            data ={
                "type": "key_press",
                "key": key.char
            }
        except AttributeError:
            # Handle special keys (e.g., space, ctrl, alt) which don't have a .char attribute
            print(f'Special key {key} pressed')
            data ={
                "type": "key_press",
                "key": str(key)
            }
        finally:
            self.sock.send(json.dumps(data).encode())

    def on_release(self,key):
        print(f'{key} released')
        if key == keyboard.Key.esc:
            # Stop listener by returning False
            return False
        try:
            data ={
                "type": "key_release",
                "key": key.char
            }
        except AttributeError:
            data ={
                "type": "key_release",
                "key": str(key)
            }
        finally:        
            self.sock.send(json.dumps(data).encode() + b"\n")  # Add newline as a delimiter
