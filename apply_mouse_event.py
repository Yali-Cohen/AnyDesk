# mouse_apply.py
from input_controller import InputController
from input_capture import MouseEvent
from pynput.mouse import Controller as PynputMouseController

mouse_ctl = InputController()

def _set_pos(x, y):
    if hasattr(mouse_ctl, "controller"):
        mouse_ctl.controller.position = (x, y)
    elif hasattr(mouse_ctl, "mouse"):
        mouse_ctl.mouse.position = (x, y)
    else:
        mouse_ctl.position = (x, y)
def get_mouse_controller(obj):
    if hasattr(obj, "controller"):
        return obj.controller
    if hasattr(obj, "mouse"):
        return obj.mouse

    if hasattr(obj, "position") and hasattr(obj, "scroll") and hasattr(obj, "press"):
        return obj

    return PynputMouseController()
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