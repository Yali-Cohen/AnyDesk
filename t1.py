#Server, controlled

import json
from threading import Thread
from server1 import Server
from input_controller import InputController
from pynput.mouse import Button
from input_capture import MouseEvent
from input_controller import InputController
mouse_ctl = InputController()

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
    # אם InputController שלך הוא wrapper עם controller בפנים
    if hasattr(mouse_ctl, "controller"):
        mouse_ctl.controller.position = (x, y)
    elif hasattr(mouse_ctl, "mouse"):
        mouse_ctl.mouse.position = (x, y)
    else:
        # אם הוא ממש pynput Controller עצמו
        mouse_ctl.position = (x, y)

def apply_mouse_event(ev: MouseEvent):
    if ev.type == "move":
        set_pos(ev.x, ev.y)

    elif ev.type == "click":
        set_pos(ev.x, ev.y)
        if ev.button is None:
            return
        if ev.pressed:
            mouse_ctl.press(ev.button) if hasattr(mouse_ctl, "press") else mouse_ctl.controller.press(ev.button)
        else:
            mouse_ctl.release(ev.button) if hasattr(mouse_ctl, "release") else mouse_ctl.controller.release(ev.button)

    elif ev.type == "scroll":
        set_pos(ev.x, ev.y)
        dx = ev.dx or 0
        dy = ev.dy or 0
        if hasattr(mouse_ctl, "scroll"):
            mouse_ctl.scroll(dx, dy)
        else:
            mouse_ctl.controller.scroll(dx, dy)

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