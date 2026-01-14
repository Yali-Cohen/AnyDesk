#client.py, controller
import time
from client1 import Client

from server1 import Server
from input_capture import InputCapture, MouseEvent
from threading import Thread
c = Client()
c.connect("192.168.1.228", 1234)
print(c.receive())
c.send("Hello from client".encode())

def handle_mouse():
    inputCapture = InputCapture()
    def handle_event(ev: MouseEvent):
        print(ev)

    cap = InputCapture(on_event=handle_event, move_hz=60, debug_print=False)
    cap.start()
    print("Input capture started. Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        cap.stop()
        print("Bye.")
t = Thread(target=handle_mouse)
t.start()