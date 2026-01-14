#server.py
from server1 import Server
s = Server(port=0)
client_socket = s.accept_connection()
client_socket.send(b"Hello from server")
print(client_socket.recv(1024).decode())
