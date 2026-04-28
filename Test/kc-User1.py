import socket
from pynput.keyboard import Key, Controller

keyboard = Controller()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = socket.gethostbyname(socket.gethostname())
sock.connect(("10.0.0.30", 9999))
while True:
    data = sock.recv(1024).decode()
    print("Received:", data)
    if data:
        try:
            data = eval(data)
            if data["type"] == "key_press":
                key = data["key"]
                if len(key) == 1:
                    keyboard.press(key)
                else:
                    keyboard.press(getattr(Key, key.replace("Key.", "")))
            elif data["type"] == "key_release":
                key = data["key"]
                if len(key) == 1:
                    keyboard.release(key)
                else:
                    keyboard.release(getattr(Key, key.replace("Key.", "")))
        except Exception as e:
            print("Error processing data:", e)
sock.close()
    