#Server, controlled

import json
from threading import Thread
from server1 import Server
from input_controller import InputController
from pynput.mouse import Button
from input_capture import MouseEvent
from input_controller import InputController
mouse_ctl = InputController()
from pynput.mouse import Controller as PynputMouseController

def get_mouse_controller(obj):
    if hasattr(obj, "controller"):
        return obj.controller
    if hasattr(obj, "mouse"):
        return obj.mouse
    if hasattr(obj, "position") and hasattr(obj, "scroll") and hasattr(obj, "press"):
        return obj

    return PynputMouseController()
def dict_to_mouse_event(d: dict) -> MouseEvent:
    b = d.get("button")
    if b == "left":
        button = Button.left
    elif b == "right":
        button = Button.right
    elif b == "middle":
        button = Button.middle
    else:
        button = None

    return MouseEvent(
        type=d["type"],
        ts=d.get("ts", 0.0),
        x=int(d["x"]),
        y=int(d["y"]),
        button=button,
        pressed=d.get("pressed"),
        dx=d.get("dx"),
        dy=d.get("dy"),
    )
def set_pos(x, y):
    if hasattr(mouse_ctl, "controller"):
        mouse_ctl.controller.position = (x, y)
    elif hasattr(mouse_ctl, "mouse"):
        mouse_ctl.mouse.position = (x, y)
    else:
        mouse_ctl.position = (x, y)

def apply_mouse_event(ev: MouseEvent):
    ctl = get_mouse_controller(mouse_ctl)

    if ev.type == "move":
        ctl.position = (ev.x, ev.y)

    elif ev.type == "click":
        ctl.position = (ev.x, ev.y)
        if ev.button is None:
            return
        if ev.pressed:
            ctl.press(ev.button)
        else:
            ctl.release(ev.button)

    elif ev.type == "scroll":
        ctl.position = (ev.x, ev.y)
        ctl.scroll(ev.dx or 0, ev.dy or 0)

def data_to_ev(data):
    data_json = json.loads(data)
    print(data_json)
    return dict_to_mouse_event(data_json)

def handle_mouse(sock):
    buffer = ""
    while True:
        chunk = sock.recv(4096).decode("utf-8", errors="ignore")
        if not chunk:
            print("Client disconnected.")
            break
        buffer += chunk
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            try:
                data_json = json.loads(line)
            except json.JSONDecodeError as e:
                print("Bad JSON:", e, "LINE:", line[:200])
                continue
            ev = dict_to_mouse_event(data_json)
            print("EV:", ev)
            apply_mouse_event(ev)
s =Server(port=1234)
client_socket = s.accept_connection()
client_socket.send(b"Hello from server")
print(client_socket.recv(1024).decode())
t = Thread(target=handle_mouse, args=(client_socket,))
t.start()
t.join()