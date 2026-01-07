# input_capture.py
from pynput import mouse
import time
from dataclasses import dataclass
from typing import Callable, Optional, Any


@dataclass
class MouseEvent:
    type: str                  # "move" | "click" | "scroll"
    ts: float                  # time.monotonic()
    x: int
    y: int
    button: Optional[Any] = None
    pressed: Optional[bool] = None
    dx: Optional[int] = None
    dy: Optional[int] = None

#מפעיל Listener וממיר Callbacks לאירועים של MouseEvent
class InputCapture:
    """
    Mouse input capture using pynput.

    - call start() to begin listening (non-blocking)
    - call stop() to stop listening
    - you can pass on_event callback to receive MouseEvent objects
    """

    def __init__(
        self,
        on_event: Optional[Callable[[MouseEvent], None]] = None,
        move_hz: int = 60,              # how often to emit move events (max)
        stop_on_release: bool = False,  # set True if you want to stop on mouse release
        debug_print: bool = False
    ):
        self.on_event = on_event
        self.move_interval = 1.0 / max(1, move_hz)
        self.stop_on_release = stop_on_release
        self.debug_print = debug_print

        self._listener: Optional[mouse.Listener] = None
        self._last_move_ts: float = 0.0

    def start(self) -> None:
        if self._listener is not None:
            return  # already started

        self._listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        self._listener.start()

        if self.debug_print:
            print("[InputCapture] started")

    def stop(self) -> None:
        if self._listener is None:
            return

        self._listener.stop()
        self._listener.join()
        self._listener = None

        if self.debug_print:
            print("[InputCapture] stopped")

    def is_running(self) -> bool:
        return self._listener is not None

    # ---- internal callbacks ----
    def _emit(self, ev: MouseEvent) -> None:
        if self.on_event:
            self.on_event(ev)
        elif self.debug_print:
            print(ev)

    def _on_move(self, x: int, y: int) -> None:
        now = time.monotonic()
        if now - self._last_move_ts < self.move_interval:
            return
        self._last_move_ts = now

        self._emit(MouseEvent(type="move", ts=now, x=x, y=y))

    def _on_click(self, x: int, y: int, button, pressed: bool):
        now = time.monotonic()
        self._emit(MouseEvent(type="click", ts=now, x=x, y=y, button=button, pressed=pressed))

        # stop only if you explicitly want that behavior
        if self.stop_on_release and (pressed is False):
            return False  # tells pynput to stop listener

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        now = time.monotonic()
        self._emit(MouseEvent(type="scroll", ts=now, x=x, y=y, dx=dx, dy=dy))


if __name__ == "__main__":
    # Demo usage (local): print events, non-blocking listener, keep app alive
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
