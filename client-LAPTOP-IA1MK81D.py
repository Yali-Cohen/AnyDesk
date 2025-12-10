import socket
import threading
import pyautogui

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 8080
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(ADDR)
def handle_client_mouse(conn, addr):
    data = recv_mouse_position()
    move_mouse_position(data)
def start_mouse():
    while True:
        conn, addr = client.accept()
        thread = threading.Thread(target=handle_client_mouse, args=(conn, addr))
        thread.start()
def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
def recv_mouse_position(conn):
    data = conn.recv(1024)
    return data.decode(FORMAT)
def move_mouse_position(position):
    pyautogui.moveTo(position.x, position.y)

send("hi")