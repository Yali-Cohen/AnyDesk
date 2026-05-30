# socket_listener.py
from PySide6.QtCore import QThread, Signal

from client1 import Client

class SocketListener(QThread):
    message_received = Signal(dict)

    def __init__(self, client:Client):
        super().__init__()
        self.client = client
        self.running = True

    def run(self):
        while self.running:
            msg = self.client.receive_json()
            if msg:
                self.message_received.emit(msg) # emit the received message to be handled by the main thread (GUI)

    def stop(self):
        self.running = False