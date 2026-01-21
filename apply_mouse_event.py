# mouse_apply.py
from input_controller import InputController
from input_capture import MouseEvent

mouse_ctl = InputController()

def _set_pos(x, y):
    if hasattr(mouse_ctl, "controller"):
        mouse_ctl.controller.position = (x, y)
    elif hasattr(mouse_ctl, "mouse"):
        mouse_ctl.mouse.position = (x, y)
    else:
        mouse_ctl.position = (x, y)

def apply_mouse_event(ev: MouseEvent):
    if ev.type == "move":
        _set_pos(ev.x, ev.y)

    elif ev.type == "click":
        _set_pos(ev.x, ev.y)
        if ev.button is None:
            return

        if hasattr(mouse_ctl, "press"):
            if ev.pressed:
                mouse_ctl.press(ev.button)
            else:
                mouse_ctl.release(ev.button)
        else:
            if ev.pressed:
                mouse_ctl.controller.press(ev.button)
            else:
                mouse_ctl.controller.release(ev.button)

    elif ev.type == "scroll":
        _set_pos(ev.x, ev.y)
        dx = ev.dx or 0
        dy = ev.dy or 0

        if hasattr(mouse_ctl, "scroll"):
            mouse_ctl.scroll(dx, dy)
        else:
            mouse_ctl.controller.scroll(dx, dy)
