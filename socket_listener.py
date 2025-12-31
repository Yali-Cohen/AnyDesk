# socket_listener.py
from PySide6.QtCore import QThread, Signal

class SocketListener(QThread):
    message_received = Signal(dict)

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.running = True

    def run(self):
        while self.running:
            msg = self.client.receive_json()
            if msg:
                self.message_received.emit(msg)

    def stop(self):
        self.running = False