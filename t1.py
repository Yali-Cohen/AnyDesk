#client, controlled
from client1 import Client
from input_controller import InputController
def handle_mouse():
    inputController = InputController()
c = Client()
c.connect("192.168.1.228", 1234)
print(c.receive())
c.send("Hello from client".encode())
handle_mouse()
