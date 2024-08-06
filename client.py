import pyautogui
import socket

HOST = '10.0.0.44'  # כתובת ה-IP של השרת
PORT = 8080
pyautogui.FAILSAFE = False
def create_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            try:
                data = s.recv(1024).decode()
                print(f'Received data: {data}')  # הדפסת הנתונים שהתקבלו
                if not data or data == "exit":
                    print("Exit command received or no data")
                    break
                elif data.startswith("MOUSE_POS:"):
                    x, y = recv_mouse_position(data)
                    move_mouse_position(x, y)
                elif data.startswith("Left_Click") or data.startswith("Right_Click"):
                    click = recv_mouse_click(data)
                    click_mouse_position(click)
                elif data.startswith("Key_"):
                    key = recv_key(data)
                    press_key(key)
            except Exception as e:
                print(f"Something went wrong: {e}")
                break 
        s.close()

def recv_mouse_position(data):
    try:
        mouse_pos = data.split(":")[1]
        x, y = map(int, mouse_pos.split(','))
        return x, y
    except Exception as e:
        print(f"Error parsing mouse position: {e}")
        return 0, 0  # מחזיר ערכים ברירת מחדל במקרה של שגיאה


def move_mouse_position(x, y):
    pyautogui.moveTo(x, y)

def recv_mouse_click(data):
    click = data.split(":")[0]
    click_pos = data.split(":")[1]
    x, y = map(int, click_pos.split(','))
    return click, x, y

def click_mouse_position(click_data):
    click, x, y = click_data
    print(f'Executing {click} at ({x}, {y})')  # הדפסת הקורדינטות של הלחיצה
    if click == "Right_Click":
        pyautogui.click(x, y, button='right')
    elif click == "Left_Click":
        pyautogui.click(x, y, button='left')

def recv_key(data):
    key = data[4:]
    print(f"The key that received: {key}")  # הדפסת המפתח שהתקבל
    return key

def press_key(key):
    pyautogui.press(key)
    print("The key pressed")

if __name__ == "__main__":
    create_client()