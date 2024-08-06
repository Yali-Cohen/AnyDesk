import pyautogui
import socket
import threading
import time
from pynput import mouse
import keyboard

HOST = '0.0.0.0'  # כתובת ה-IP של השרת
PORT = 8080
pyautogui.FAILSAFE = False

lock = threading.Lock()  # נעילת חוטים

def create_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            try:
                conn, addr = s.accept()
                print(f"Connected by {addr}")
                threadMouse = threading.Thread(target=send_mouse_positions, args=(conn,))
                threadClick = threading.Thread(target=send_click, args=(conn,))
                threadKeyboard = threading.Thread(target=send_key, args=(conn,))
                threadMouse.start()
                threadClick.start()
                threadKeyboard.start()
                threadMouse.join()
                threadClick.join()
                threadKeyboard.join()
            except Exception as e:
                print("Server Error:", e)
            finally:
                if conn:
                    conn.close()
                print("Server closed")

def send_mouse_positions(conn):
    try:
        while True:
            x, y = get_mouse_position()
            send_mouse_position(x, y, conn)
            time.sleep(0.3)  # שלח מיקום כל 300 מילישניות
    except Exception as e:
        print("Error sending mouse positions:", e)
    finally:
        conn.close()

def send_mouse_position(x, y, conn):
    with lock:
        try:
            position = f'MOUSE_POS:{x},{y}'
            conn.send(position.encode())
        except Exception as e:
            print(f"Failed to send mouse position: {e}")
            raise  # כדי שהשגיאה תתפוס גם בפונקציה הקוראת

def get_mouse_position():
    position = pyautogui.position()
    x, y = position.x, position.y
    return x, y

def send_click(conn):
    def on_click(x, y, button, pressed):
        if button == mouse.Button.left:
            click_type = 'Left_Click'
        else:
            click_type = 'Right_Click'

        if pressed:
            message = f'{click_type}:{x},{y}'
            print(f'Sending message: {message}')  # הדפסת ההודעה שנשלחת
            with lock:
                try:
                    conn.send(message.encode())
                except Exception as e:
                    print(f"Failed to send click: {e}")

    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()

def send_key(conn):
    def on_key_event(event):
        if event.event_type == keyboard.KEY_DOWN:
            key = f"Key_{event.name}"
            print(f"Sending key: {key}")  # הדפסת המפתח שנשלח
            with lock:
                try:
                    conn.send(key.encode())
                except Exception as e:
                    print(f"Failed to send key: {e}")

    keyboard.hook(on_key_event)
    keyboard.wait('esc')
if __name__ == "__main__":
    create_server()