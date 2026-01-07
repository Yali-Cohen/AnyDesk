from pynput.mouse import Controller, Listener, Button
import time

mouse = Controller()

def on_move(x, y):
    # אירוע תנועה
    print("move:", x, y)

def on_click(x, y, button, pressed):
    if pressed:
        print("click:", button, x, y)

# מאזין ברקע
listener = Listener(on_move=on_move, on_click=on_click)
listener.start()

# שליטה מקומית (דוגמה): להזיז יחסית כל 0.02 שניות
for _ in range(100):
    mouse.move(2, 0)  # ימינה
    time.sleep(0.02)

listener.stop()
