# protocol/mouse_codec.py
from pynput.mouse import Button
from input_capture import MouseEvent

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

    if ev.button is None:
        d["button"] = None
    elif ev.button == Button.left:
        d["button"] = "left"
    elif ev.button == Button.right:
        d["button"] = "right"
    elif ev.button == Button.middle:
        d["button"] = "middle"
    else:
        d["button"] = str(ev.button)

    return d


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
