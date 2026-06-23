import socket
from protocol.framing import send_json_line, recv_json_line

class Server:
    def __init__(self, host="0.0.0.0", port=8080):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.port = self.server_socket.getsockname()[1]
        self.server_socket.listen(5)
        self.connections = 0

    def accept_connection(self):
        client_socket, addr = self.server_socket.accept()
        print(f"Connection from {addr} has been established!")
        return client_socket

    def send_json(self, client_socket: socket.socket, obj: dict):
        send_json_line(client_socket, obj)

    def receive_data(self, client_socket: socket.socket):
        return recv_json_line(client_socket)

    def get_number_of_connections(self):
        return self.connections

    def increment_connections(self):
        self.connections += 1

    def decrement_connections(self):
        if self.connections > 0:
            self.connections -= 1

    def getsockname(self):
        print(f"Server is listening on port: {self.port}")
        print(f"Server is listening on IP: {self.ip}")
        return (self.ip, self.port)

    def close(self):
        self.server_socket.close()