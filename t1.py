#client, controlled

from threading import Thread
from server1 import Server
from input_controller import InputController
def handle_mouse():
    inputController = InputController()
s = Server(port=1234)
client_socket = s.accept_connection()
client_socket.send(b"Hello from server")
print(client_socket.recv(1024).decode())
t = Thread(target=handle_mouse())
