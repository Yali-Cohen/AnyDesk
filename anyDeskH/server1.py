import socket
class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", 9090))
        self.server_socket.listen(5)
        self.connections = 0
    def accept_connection(self):    
        client_socket, addr = self.server_socket.accept()
        print(f"Connection from {addr} has been established!")
        return client_socket
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
