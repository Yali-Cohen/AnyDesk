#server.py
from server1 import Server
from input_capture import InputCapture
def handle_mouse_server():
    inputCapture = InputCapture()
s = Server(port=0)
client_socket = s.accept_connection()
client_socket.send(b"Hello from server")
print(client_socket.recv(1024).decode())
handle_mouse_server()
