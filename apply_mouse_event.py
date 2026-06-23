# mouse_apply.py, applies a MouseEvent to the local machine using pynput. This is used by the server to apply mouse events received from the controller to the target machine.
from input_controller import InputController
from input_capture import MouseEvent

mouse_ctl = InputController()

def apply_mouse_event(ev: MouseEvent):
    ctl = mouse_ctl.mouse

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