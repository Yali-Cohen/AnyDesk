import pickle
import socket
import threading
import time
#keyboard
import pyautogui
HEADER = 64
PORT_MOUSE = 8080
PORT_KEYBOARD = 8081
SERVER = socket.gethostbyname(socket.gethostname())
ADDR_MOUSE = (SERVER, PORT_MOUSE)
ADDR_KEYBOARD = (SERVER, PORT_KEYBOARD)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server_mouse = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_mouse.bind(ADDR_MOUSE)

server_keyboard = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_keyboard.bind(ADDR_KEYBOARD)

def handle_server_mouse(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        try:
            # Continuously get and send mouse position
            mouse_position = get_mouse_position()
            print(f"Current mouse position: ({mouse_position.x}, {mouse_position.y})")

            # Send the position
            sent_mouse_position(conn, mouse_position)

            # Termination check
            if mouse_position.x == 0 and mouse_position.y == 0:
                connected = False
                print("Mouse reached (0, 0). Closing connection.")

        except Exception as e:
            print(f"Error: {e}")
            connected = False  # Exit loop on error

    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

def start_mouse():
    server_mouse.listen()
    print(f"[LISTENING] Server is listening on {SERVER}:{PORT_MOUSE}")
    while True:
        conn, addr = server_mouse.accept()
        thread = threading.Thread(target=handle_server_mouse, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] Server is starting...")
#mouse
def get_mouse_position():
    mouse_position = pyautogui.position()
    return(mouse_position)
def sent_mouse_position(conn, mouse_position):
    conn.send(pickle.dumps(mouse_position))
    time.sleep(0.01)

start_mouse()

#keyboard
def handle_server_screen(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected. KEYBOARD")
    connected = True
    while connected:
        msg_length = 1024
        if msg_length:
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {msg}")

            #code here

    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.")
def start_screen():
    server_keyboard.listen()
    print(f"[LISTENING] Server is listening on {SERVER}:{PORT_KEYBOARD}")
    while True:
        conn, addr = server_keyboard.accept()
        thread = threading.Thread(target=handle_server_screen, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

def get_screen_shot():
    pass
