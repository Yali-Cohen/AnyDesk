#gui.py
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
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QWidget,QRadioButton, QVBoxLayout, QGridLayout,QLineEdit, QMessageBox, QSizePolicy, QHBoxLayout, QGroupBox
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
            self.client.connect("10.136.41.21", 9090)
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
        self.build_remote_connect_gui()
        self.remote_box.hide()
    def handle_server_message(self, msg:dict):
        action = msg.get("action")
        data = msg.get("data", {})
        if action == "incoming_connection":
            from_username = data.get("from_username", "Unknown")
            from_address = data.get("from_address", "Unknown")
            request_id = data.get("request_id")
            
            ans = QMessageBox.question(
                self,
                "Incoming Connection",
                f"{from_username} wants to connect. Accept?",
                QMessageBox.Yes | QMessageBox.No
            )            
            accepted = (ans == QMessageBox.Yes)
            response_payload = {
                "action": "incoming_response",
                "data": {
                    "request_id": request_id,
                    "accepted": accepted
                }
            }
            self.client.send_json(response_payload)
        elif action == "connect_result":
            accepted = data.get("accepted", False)
            QMessageBox.information(
                self, "Result", "Accepted!" if accepted else "Declined."
            )
    def update_gui(self):
        if self.is_authenticated and self.current_user:
            self.show_authenticated_gui()
            self.remote_box.show()
            
    def show_authenticated_gui(self):
        # אם כבר יצרת פעם – לא ליצור שוב
        if hasattr(self, "address_row"):
            self.address_label.setText(self.current_user.get("address", "Unknown"))
            self.address_row.show()
            return

        # שורה אופקית נפרדת
        self.address_row = QWidget()
        row = QHBoxLayout(self.address_row)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(20)  # אם אתה רוצה ממש צמוד: שים 0

        self.key_label = QLabel("Your Address")
        self.key_label.setFont(QFont("Arial", 32))
        self.key_label.setStyleSheet("color: black;")

        address = self.current_user.get("address", "Unknown")
        self.address_label = QLabel(address)
        self.address_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.address_label.setStyleSheet("color: #ff4a3d;")

        # כדי שלא “יתמתחו” וידחפו את הטקסט למרכז/רחוק
        self.key_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.address_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # יישור בתוך השורה
        row.addWidget(self.key_label, 0, Qt.AlignVCenter)
        row.addWidget(self.address_label, 0, Qt.AlignVCenter)
        # אם אתה רוצה שכל השורה תהיה באמצע המסך:
        self.layout.addWidget(self.address_row, alignment=Qt.AlignHCenter)
        
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
        if self.socket_listener:
            self.socket_listener.stop()
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
    def normalize_address(self, text):
        return "".join(ch for ch in text if ch.isdigit())

    def validate_address(self, address):
        return address.isdigit() and 6 <= len(address) <= 15
    def on_remote_input_changed(self, text):
        addr = self.normalize_address(text)
        is_valid = self.validate_address(addr)
        self.connect_btn.setEnabled(is_valid)
    def connect_to_remote(self):
        remote_address = self.normalize_address(self.remote_input.text())
        if not self.validate_address(remote_address):
            QMessageBox.warning(self, "Invalid Address", "Please enter a valid remote address (6-15 digits).")
            return
        QMessageBox.information(self, "Connecting", f"Attempting to connect to {remote_address}...")
        from_address = self.current_user.get("address", "")
        email = self.current_user.get("email", "")
        username = self.current_user.get("username", "")
        connect_data = {
            "from_email": email,
            "from_username": username,
            "from_address": from_address,
            "target_address": remote_address
        }
        payload = {
            "action": "connect_request",
            "data": connect_data
        }
        print("Connecting with payload:", payload)
        self.client.send_json(payload)
        
    def build_remote_connect_gui(self):
        self.remote_box = QGroupBox("Connect to Remote Address")
        box_layout = QHBoxLayout(self.remote_box)
        box_layout.setContentsMargins(12, 10, 12, 10)
        box_layout.setSpacing(10)
        
        self.remote_input = QLineEdit()
        self.remote_input.setPlaceholderText("Enter Remote Address")
        self.remote_input.setClearButtonEnabled(True)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setEnabled(False)
        self.remote_input.textChanged.connect(self.on_remote_input_changed)
        self.connect_btn.clicked.connect(self.connect_to_remote)
        
                
        box_layout.addWidget(self.remote_input)
        box_layout.addWidget(self.connect_btn) 
        
        self.layout.addWidget(self.remote_box, alignment=Qt.AlignHCenter)
    def start_listener_once(self):
        if not hasattr(self, "socket_listener"):
            self.socket_listener = SocketListener(self.client)
            self.socket_listener.message_received.connect(self.handle_server_message)
            self.socket_listener.start()
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
                self.main_window.start_listener_once()
 
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
                self.main_window.start_listener_once()
            else:
                QMessageBox.warning(self, "Login failed", message or "Login error.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send data: {e}")