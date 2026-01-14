#gui.py
import json
import os
import random
import sys,ctypes
from client1 import Client
from register import Register
from login import Login
from server1 import Server
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
            print("Connecting to server...")
            self.client.connect("192.168.2.16", 8080)
            print("Connected to server.")
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
    def send(self, data: bytes, client_socket):
        client_socket.sendall(data)

    def receive(self, buffer_size=4096):
        return self.client_socket.recv(buffer_size)

    def send_json(self, obj: dict, client_socket):
        data = json.dumps(obj).encode('utf-8')
        self.send(data,client_socket)

    def send_ports_to_full_connection(self, client_socket):
        server_mouse_connection = Server(host="0.0.0.0", port=0)
        mouse_port = server_mouse_connection.port
        server_keyboard_connection = Server(host="0.0.0.0", port=0)
        keyboard_port = server_keyboard_connection.port
        server_screen_connection = Server(host="0.0.0.0", port=0)
        screen_port = server_screen_connection.port
        ports = (mouse_port, keyboard_port, screen_port)
        ports_payload = {
            "IP": self.ip,
            "ports": ports
        }
        print(f"Sending to client payload: {ports_payload}")
        self.send_json(ports_payload, client_socket)
        client_mouse_socket = server_mouse_connection.accept_connection()
        client_keyboard_socket = server_keyboard_connection.accept_connection()
        client_screen_socket = server_screen_connection.accept_connection()
    def connect_to_server_sockets(self):
        payload = self.client_connection.receive().decode()
        ip = payload["IP"]
        ports = payload["ports"]
        mouse_port = ports[0]
        keyboard_port = ports[1]
        screen_port = ports[2]
        print(mouse_port, keyboard_port, screen_port)
        print(ip)
        print(payload)
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
                f"{from_username} wants to connect from {from_address}. Accept?",
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
        elif action == "connection_established":#Controlled side, Server
            print("Connection established, setting up server...")
            session_id = data.get("session_id")
            self.server_connection = Server(host="0.0.0.0", port=9080)
            self.ip, port = self.server_connection.getsockname()
            print(f"ip sent to sholet {self.ip}")
            self.client.send_json({
                "action": "connection_details",
                "data": {
                    "session_id": session_id,
                    "ip": self.ip,
                    "port": port
                }
            })
            client_socket = self.server_connection.accept_connection()
            print(f"Listening for incoming connections on {self.ip}:{port}")
            data = client_socket.recv(4096)
            print("Received from client:", data)
            client_socket.send(b"Hello from sholet!")
            print("Sent greeting to client.")
            self.send_ports_to_full_connection(client_socket)

        elif action == "connection_details":#Controller side
            print("Received connection details from server.")
            ip = data.get("ip")
            port = data.get("port")
            QMessageBox.information(
                self, "Connection Details", f"Connect to IP: {ip}, Port: {port}"
            )
            print(f"Connection to {ip}, {port}")
            self.client_connection = Client()
            self.client_connection.connect(ip, port)
            self.client_connection.send(b"Hello from client!")
            data = self.client_connection.receive()
            print("Received from sholet:", data.decode('utf-8'))
            print("Connection established successfully.")
            self.connect_to_server_sockets()
    def update_gui(self):
        if self.is_authenticated and self.current_user:
            self.show_authenticated_gui()
            self.remote_box.show()
            
    def show_authenticated_gui(self):
        if hasattr(self, "address_row"):
            self.address_label.setText(self.current_user.get("address", "Unknown"))
            self.address_row.show()
            return

        self.address_row = QWidget()
        row = QHBoxLayout(self.address_row)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(20) 

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
