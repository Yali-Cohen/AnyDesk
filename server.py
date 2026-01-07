import pickle
import socket
import threading
import time

import pyautogui
from server1 import Server
HOST = '0.0.0.0'
PORT = 8080
def handle_server_mouse(server_obj, server_mouse_socket):
    # print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        try:
            # Continuously get and send mouse position
            mouse_position = get_mouse_position()
            print(f"Current mouse position: ({mouse_position.x}, {mouse_position.y})")

            # Send the position
            sent_mouse_position(server_mouse_socket, mouse_position)

            # Termination check
            if mouse_position.x == 0 and mouse_position.y == 0:
                connected = False
                print("Mouse reached (0, 0). Closing connection.")

        except Exception as e:
            print(f"Error: {e}")
            connected = False  # Exit loop on error

    server_mouse_socket.close()



#mouse
def get_mouse_position():
    mouse_position = pyautogui.position()
    return(mouse_position)
def sent_mouse_position(conn, mouse_position):
    conn.send(pickle.dumps(mouse_position))
    time.sleep(0.02)

def main():
    server = Server()
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        server_mouse_socket = server.accept_connection()
        t = threading.Thread(target=handle_server_mouse, args=(server, server_mouse_socket), daemon=True)
        t.start()
if __name__ == "__main__":
    main()



