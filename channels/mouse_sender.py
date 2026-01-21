# channels/mouse_sender.py
import queue, threading
from protocol.framing import send_json_line
from protocol.mouse_codec import mouse_event_to_dict
from input_capture import InputCapture

class MouseSender:
    def __init__(self, sock, move_hz=60):
        self.sock = sock
        self.q = queue.Queue(maxsize=2000)
        self.stop_evt = threading.Event()
        self.cap = InputCapture(on_event=self._on_event, move_hz=move_hz)
        self.worker = threading.Thread(target=self._send_loop, daemon=True)

    def _on_event(self, ev):
        try:
            self.q.put_nowait(ev)
        except queue.Full:
            # אם עומס—זורקים אירועים ישנים (עדיף מאשר לתקוע הכל)
            pass

    def _send_loop(self):
        while not self.stop_evt.is_set():
            ev = self.q.get()
            send_json_line(self.sock, mouse_event_to_dict(ev))

    def start(self):
        self.cap.start()
        self.worker.start()

    def stop(self):
        self.stop_evt.set()
        self.cap.stop()
