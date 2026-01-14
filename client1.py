# client1.py

import socket
import json

class Client:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self, host, port):
        if self.connected:
            return
        self.client_socket.connect((host, port))
        self.connected = True
        print("Connected")
    def get_socket(self):
        return self.client_socket
    def send(self, data: bytes):
        self.client_socket.sendall(data)

    def receive(self, buffer_size=4096):
        return self.client_socket.recv(buffer_size)

    def send_json(self, obj: dict):
        data = json.dumps(obj).encode('utf-8')
        self.send(data)

    def receive_json(self):
        data = self.receive()
        if not data:
            return None
        return json.loads(data.decode('utf-8'))

    def close(self):
        self.client_socket.close()
        self.connected = False
