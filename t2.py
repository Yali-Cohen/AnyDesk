#server.py
import time
from server1 import Server
from input_capture import InputCapture, MouseEvent
from threading import Thread
def handle_mouse_server():
    inputCapture = InputCapture()
    def handle_event(ev: MouseEvent):
        print(ev)

    cap = InputCapture(on_event=handle_event, move_hz=60, debug_print=False)
    cap.start()
    print("Input capture started. Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        cap.stop()
        print("Bye.")
s = Server(port=0)
client_socket = s.accept_connection()
client_socket.send(b"Hello from server")
print(client_socket.recv(1024).decode())
t = Thread(target=handle_mouse_server)