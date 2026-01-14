import json
import socket
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
    def send_data(self, data:bytes):
        self.server_socket.sendall(data)
    def receive(self, buffer_size=1024):
        return self.server_socket.recv(buffer_size)
    def receive_data(self, client_socket, buffer_size=1024):
        return client_socket.recv(buffer_size)
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
    
    def send_json(self, obj: dict):
        data = json.dumps(obj).encode('utf-8')
        self.send_data(data)

    def receive_json(self):
        data = self.receive_data()
        if not data:
            return None
        return json.loads(data.decode('utf-8'))

    def close(self):
        self.server_socket.close()
