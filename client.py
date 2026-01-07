import pickle
import socket
import time

import pyautogui
from client1 import Client 
HOST = "10.247.254.196"
print(f"Client IP Address: {HOST}")
PORT = 8080
print(f"Connecting to server at {HOST}:{PORT}")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Connected")
def recv_mouse_position():
    data = s.recv(1024)
    position = pickle.loads(data)
    return position


while True:
    position = recv_mouse_position()
    print(f"Mouse position received: ({position.x}, {position.y})")
    if position.x == 0 and position.y == 0:
        print("Mouse position is (0, 0). Stopping client.")
        break
    pyautogui.moveTo(position.x, position.y) 
    time.sleep(0.01) 