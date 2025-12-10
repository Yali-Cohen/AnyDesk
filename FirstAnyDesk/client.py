import pickle
import socket
import time
import pyautogui

HEADER = 64
SERVER = "10.0.0.33"
PORT = 8080
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
pyautogui.FAILSAFE = False
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

# פונקציה לשליחת הודעה לשרת
def send(msg):
    message = msg.encode(FORMAT)
    # msg_length = len(message)
    # send_length = str(msg_length).encode(FORMAT)
    # send_length += b' ' * (HEADER - len(send_length))
    # client.send(send_length)
    client.send(message)

# פונקציה לקבלת מיקום העכבר מהשרת
def recv_mouse_position():
    data = client.recv(1024)
    position = pickle.loads(data)
    return position

# שליחת הודעה ראשונית לשרת
send("hi")

while True:
    position = recv_mouse_position()
    print(f"Mouse position received: ({position.x}, {position.y})")
    if position.x == 0 and position.y == 0:
        print("Mouse position is (0, 0). Stopping client.")
        break
    pyautogui.moveTo(position.x, position.y) 
    time.sleep(0.01) 