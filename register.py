#register.py
import os
import sys,ctypes
from client1 import Client
from socket_listener import SocketListener
myappid = u"com.yourname.remotesupport"   # מחרוזת ייחודית משלך
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

from PySide6.QtCore import QSize, Qt, QRegularExpression
from PySide6.QtGui import QIcon,QGuiApplication, QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QWidget,QRadioButton, QVBoxLayout, QGridLayout,QLineEdit, QMessageBox, QSizePolicy, QHBoxLayout, QGroupBox
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# בונה נתיב יחסי לתיקיית Images
ICON_PATH = os.path.join(BASE_DIR, "Images", "anydesk_icon.png")
ARROW_PATH = os.path.join(BASE_DIR, "Images", "down-arrow.png")

class Register(QWidget):
    def __init__(self, client, main_window=None):
        super().__init__()
        self.client = client
        self.main_window = main_window
        self.setWindowTitle("Register")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        title = QLabel("Register Form")
        self.layout.addWidget(title, 0, 1)
        
        user = QLabel("Username:")
        self.layout.addWidget(user, 1, 0)
        
        email = QLabel("Email:")
        self.layout.addWidget(email, 2, 0)
        
        password = QLabel("Password:")
        self.layout.addWidget(password, 3, 0)
        
        confirm_password = QLabel("Confirm Password:")
        self.layout.addWidget(confirm_password, 4, 0)
        
        self.input_username = QLineEdit()
        self.layout.addWidget(self.input_username, 1, 1)
        
        self.input_email = QLineEdit()
        self.layout.addWidget(self.input_email, 2, 1)
        
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.input_password, 3, 1)
        
        self.confirmed_password = QLineEdit()
        self.confirmed_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.confirmed_password, 4, 1)
        
        self.visible_hidden_password = QPushButton("Visible/Hidden")
        self.layout.addWidget(self.visible_hidden_password, 5, 0)
        self.visible_hidden_password.clicked.connect(self.visible_hidden_func)
        
        self.visible_hidden_confirmed_password = QPushButton("Visible/Hidden")
        self.layout.addWidget(self.visible_hidden_confirmed_password, 6, 0)
        self.visible_hidden_confirmed_password.clicked.connect(self.visible_hidden_confirmed_func)

        register_button = QPushButton("Register")
        self.layout.addWidget(register_button, 7, 1)
        register_button.clicked.connect(self.register_user)
        
        cancel_button = QPushButton("Cancel")
        self.layout.addWidget(cancel_button, 7, 0)
        cancel_button.clicked.connect(self.close)
    def visible_hidden_func(self):
        if self.input_password.echoMode() == QLineEdit.Normal:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Normal)
    def visible_hidden_confirmed_func(self):
        if self.confirmed_password.echoMode() == QLineEdit.Normal:
            self.confirmed_password.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            self.confirmed_password.setEchoMode(QLineEdit.EchoMode.Normal)
    def input_validity_tests(self):
        if not self.input_username.text().strip() or not self.input_email.text().strip() or not self.input_password.text() or not self.confirmed_password.text():
            QMessageBox.warning(self, "Missing", "Please fill all the fields!"); return True
        if "@" not in self.input_email.text() or "." not in self.input_email.text():
            QMessageBox.warning(self, "Email", "Email address isn't correct."); return True
        if len(self.input_password.text()) < 6:
            QMessageBox.warning(self, "Password", "Password must be 6 characters length!"); return True
        if self.input_password.text() != self.confirmed_password.text():
            QMessageBox.warning(self, "Password", "Passwords doesn't match."); return True
        return False
        
    def register_user(self):
        if self.input_validity_tests():
            return
        register_data = {
            "username": self.input_username.text().strip(),
            "email": self.input_email.text().strip(),
            "password": self.input_password.text()
        }
        self.send_register_data(register_data)
    def send_register_data(self, register_data):
        try:
            payload = {
                "action": "register",
                "data": register_data
            }
            self.client.send_json(payload)

            response = self.client.receive_json()
            if not response:
                QMessageBox.critical(self, "Error", "No response from server.")
                return

            if response.get("status") == "success":
                QMessageBox.information(self, "Success", response.get("message", "Registration successful."))
                self.close()
                self.main_window.is_authenticated = True
                address = response.get("Address", "")
                self.main_window.current_user = {
                    "email": register_data["email"],
                    "username": register_data["username"],
                    "address": address
                }
                self.main_window.update_status_label()
                self.main_window.update_gui()
                self.main_window.start_listener_once()
 
            else:
                QMessageBox.warning(self, "Register failed", response.get("message", "Error in registration."))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send data: {e}")
