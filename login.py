#login.py
import json
import os
import random
import sys,ctypes
from client1 import Client
from socket_listener import SocketListener
myappid = u"com.yourname.remotesupport"   # מחרוזת ייחודית משלך
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

from PySide6.QtCore import QSize, Qt, QRegularExpression
from PySide6.QtGui import QIcon,QGuiApplication, QFont, QRegularExpressionValidator
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QWidget,QRadioButton, QVBoxLayout, QGridLayout,QLineEdit, QMessageBox, QSizePolicy, QHBoxLayout, QGroupBox, QWidgetAction
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# בונה נתיב יחסי לתיקיית Images
ICON_PATH = os.path.join(BASE_DIR, "Images", "anydesk_icon.png")
ARROW_PATH = os.path.join(BASE_DIR, "Images", "down-arrow.png")

class Login(QWidget):
    def __init__(self, client, main_window=None):
        super().__init__()
        self.client = client
        self.main_window = main_window
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        title = QLabel("Login Form")
        self.layout.addWidget(title, 0, 1)
        
        user_email = QLabel("Email:")
        self.layout.addWidget(user_email, 1, 0)
        
        password = QLabel("Password:")
        self.layout.addWidget(password, 2, 0)
        
        self.input_user_email = QLineEdit()
        self.layout.addWidget(self.input_user_email, 1, 1)
        
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.input_password, 2, 1)
        
        self.visible_hidden = QPushButton("Visible/Hidden")
        self.layout.addWidget(self.visible_hidden, 3, 0)
        self.visible_hidden.clicked.connect(self.visible_hidden_func)

        login_button = QPushButton("Login")
        self.layout.addWidget(login_button, 4, 1)
        login_button.clicked.connect(self.login_user)
        
        cancel_button = QPushButton("Cancel")
        self.layout.addWidget(cancel_button, 4, 0)
        cancel_button.clicked.connect(self.close)

    def visible_hidden_func(self):
        if self.input_password.echoMode() == QLineEdit.Normal:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            self.input_password.setEchoMode(QLineEdit.EchoMode.Normal)

    def input_validity_tests(self):
        if not self.input_user_email.text().strip() or not self.input_password.text():
            QMessageBox.warning(self, "Missing", "Please fill all the fields!"); return True
        if "@" not in self.input_user_email.text() or "." not in self.input_user_email.text():
            QMessageBox.warning(self, "Email", "Email address isn't correct."); return True
        if len(self.input_password.text()) < 6:
            QMessageBox.warning(self, "Password", "Password must be 6 characters length!"); return True
        return False
    def login_user(self):
        if self.input_validity_tests():
            return
        login_data = {
            "email": self.input_user_email.text().strip(),
            "password": self.input_password.text()
        }
        self.send_login_data(login_data)
    def send_login_data(self, login_data):
        try:
            payload = {
                "action": "login",
                "data": login_data
            }
            self.client.send_json(payload)

            response = self.client.receive_json()
            if not response:
                QMessageBox.critical(self, "Error", "No response from server.")
                return

            status = response.get("status")
            message = response.get("message", "")
            username = response.get("Username", "")
            if status == "success":
                QMessageBox.information(self, "Success", message or "Login successful.")
                self.close()
                self.main_window.is_authenticated = True
                address = response.get("Address", "")                                                   
                self.main_window.current_user = {
                    "email": login_data["email"]
                    , "username": username
                    , "address": address
                }
                self.main_window.update_status_label()
                self.main_window.update_gui()
                self.main_window.start_listener_once()
            else:
                QMessageBox.warning(self, "Login failed", message or "Login error.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send data: {e}")