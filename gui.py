import json
import os
import random
import sys,ctypes
from client1 import Client
myappid = u"com.yourname.remotesupport"   # מחרוזת ייחודית משלך
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon,QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QWidget,QRadioButton, QVBoxLayout, QGridLayout,QLineEdit, QMessageBox
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# בונה נתיב יחסי לתיקיית Images
ICON_PATH = os.path.join(BASE_DIR, "Images", "anydesk_icon.png")
ARROW_PATH = os.path.join(BASE_DIR, "Images", "down-arrow.png")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = Client()
        self.client_socket = self.client.get_socket()
        self.is_authenticated = False
        self.current_user = {}
        try:
            self.client.connect("10.0.0.7", 9090)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot connect to server: {e}")
        self.register_window = None
        self.login_window = None
        self.setWindowTitle("AnyDesk")
        icon = QIcon(ICON_PATH)
        self.setWindowIcon(icon)
# ==================================================================
        container = QWidget()
        self.setCentralWidget(container)
        self.layout = QVBoxLayout(container)
        label = QLabel("Welcome to AnyDesk")
        label.setAlignment(Qt.AlignCenter)
        primary_screen = QGuiApplication.primaryScreen()
        screen_size = primary_screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        self.setFixedSize(QSize(screen_width,screen_height))
        menubar = self.menuBar()
        arrow_icon = QIcon(ARROW_PATH)
        register_login_logout_menu = menubar.addMenu(arrow_icon, "down")
        register_menu = register_login_logout_menu.addAction("Register")
        register_menu.triggered.connect(self.register_action)
        login_menu = register_login_logout_menu.addAction("Login")
        login_menu.triggered.connect(self.login_action)
        log_out_menu = register_login_logout_menu.addAction("Log Out")
        log_out_menu.triggered.connect(self.logout_action)
        self.layout.addWidget(label)
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

    def update_gui(self):
        if self.is_authenticated and self.current_user:
            self.show_authenticated_gui()
            
    def show_authenticated_gui(self):
        self.key_label = QLabel("Your AnyDesk Address:")
        self.key_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.key_label)
        
        address =  self.current_user.get("Address", "Unknown")
        self.address_label = QLabel(address)
        self.address_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.address_label)

    def update_status_label(self):
        print("STATUS:", self.is_authenticated, self.current_user)
        if not self.is_authenticated or not self.current_user:
            self.status_label.setText("Please register or login to continue.")
            return
        username = self.current_user.get("username", "User")
        self.status_label.setText(f"Welcome, {username}!")
        return
# ==================================================================
    def logout_action(self):
        self.send_logout_data(self.current_user)
        self.is_authenticated = False
        self.current_user = {}
        self.update_status_label()
        if hasattr(self, "key_label"):
            self.key_label.deleteLater()
        if hasattr(self, "address_label"):
            self.address_label.deleteLater()
    def send_logout_data(self, logout_data):
        payload = {
                "action": "logout",
                "data": logout_data
            }
        self.client.send_json(payload)
    def register_action(self):
        self.register_window = Register(self.client, self)
        self.register_window.show()

    def login_action(self):
        self.login_window = Login(self.client, self)
        self.login_window.show()



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
        
        register_button = QPushButton("Register")
        self.layout.addWidget(register_button, 5, 1)
        register_button.clicked.connect(self.register_user)
        
        cancel_button = QPushButton("Cancel")
        self.layout.addWidget(cancel_button, 5, 0)
        cancel_button.clicked.connect(self.close)
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

            else:
                QMessageBox.warning(self, "Register failed", response.get("message", "Error in registration."))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send data: {e}")
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
        
        login_button = QPushButton("Login")
        self.layout.addWidget(login_button, 3, 1)
        login_button.clicked.connect(self.login_user)
        
        cancel_button = QPushButton("Cancel")
        self.layout.addWidget(cancel_button, 3, 0)
        cancel_button.clicked.connect(self.close)
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

            else:
                QMessageBox.warning(self, "Login failed", message or "Login error.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send data: {e}")