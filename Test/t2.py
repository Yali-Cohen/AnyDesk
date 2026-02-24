#client.py, controller
import json
import time
from client1 import Client
from pynput.mouse import Button
from input_capture import InputCapture, MouseEvent
from threading import Thread
c = Client()
c.connect("192.168.1.228", 1234)
print(c.receive())
c.send("Hello from client".encode())

def mouse_event_to_dict(ev: MouseEvent) -> dict:
    d = {
        "type": ev.type,
        "ts": ev.ts,
        "x": ev.x,
        "y": ev.y,
        "pressed": ev.pressed,
        "dx": ev.dx,
        "dy": ev.dy,
    }
    if ev.button is not None:
        if ev.button == Button.left:
            d["button"] = "left"
        elif ev.button == Button.right:
            d["button"] = "right"
        elif ev.button == Button.middle:
            d["button"] = "middle"
        else:
            d["button"] = str(ev.button)
    else:
        d["button"] = None
    return d
def handle_mouse(client_socket):
    def handle_event(ev: MouseEvent):
        dic = mouse_event_to_dict(ev)
        msg = json.dumps(dic) + "\n"
        client_socket.send(msg.encode("utf-8"))


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
t = Thread(target=handle_mouse, args=(c,))
t.start()