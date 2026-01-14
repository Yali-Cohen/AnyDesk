#client, controlled

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
def handle_mouse():
    inputController = InputController()
    apply_mouse_event(ev)
s = Server(port=1234)
client_socket = s.accept_connection()
client_socket.send(b"Hello from server")
print(client_socket.recv(1024).decode())
t = Thread(target=handle_mouse())
