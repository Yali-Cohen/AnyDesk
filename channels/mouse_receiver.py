# channels/mouse_receiver.py
import threading
from protocol.framing import iter_json_lines
from protocol.mouse_codec import dict_to_mouse_event
from apply_mouse_event import apply_mouse_event  # פונקציה אחת שמיישמת

class MouseReceiver:
    def __init__(self, sock):
        self.sock = sock
        self.stop_evt = threading.Event()
        self.worker = threading.Thread(target=self._recv_loop, daemon=True)

    def _recv_loop(self):
        for obj in iter_json_lines(self.sock):
            if self.stop_evt.is_set():
                break
            ev = dict_to_mouse_event(obj)
            apply_mouse_event(ev)

    def start(self):
        self.worker.start()

    def stop(self):
        self.stop_evt.set()