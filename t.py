from server1 import Server
import socket
server = Server(host="0.0.0.0", port=8080)
print(server.server_socket.getsockname())
print(socket.gethostbyname(socket.gethostname()))