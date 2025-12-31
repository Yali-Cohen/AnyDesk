import socket
class Server:
    def __init__(self, host="0.0.0.0", port=8080):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
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
    def close(self):
        self.server_socket.close()
