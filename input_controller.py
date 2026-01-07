from pynput.mouse import Button, Controller

class InputController:
    def __init__(self):
        self.mouse = Controller()

    # Read pointer position
    def get_pointer_position(self):
        print(f"Getting pointer position. {self.mouse.position}")
        return self.mouse.position

    # Set pointer position
    def set_pointer_position(self, x, y):
        self.mouse.position = (x, y)
        print(f"Pointer moved to position: ({x}, {y})")

    # Move pointer relative to current position
    def move_pointer(self, dx, dy):
        self.mouse.move(dx, dy)
        print(f"Pointer moved by: ({dx}, {dy})")

    # Press and release
    def click_pointer(self):
        self.mouse.press(Button.left)
        self.mouse.release(Button.left)

    # Double click; this is different from pressing and releasing
    # twice on Mac OSX
    def double_click_pointer(self):
        self.mouse.click(Button.left, 2)

    # Scroll two steps down
    def scroll_pointer(self, dx, dy):
        self.mouse.scroll(dx, dy)
input_controller = InputController()
print("InputController initialized.")
