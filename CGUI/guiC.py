import sys, ctypes, socket, json
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QDialog,
    QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QMenuBar
)

if sys.platform.startswith("win"):
    myappid = u"com.yourname.remotesupport"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

HOST, PORT = "127.0.0.1", 5000

def send(cmd, data, timeout=3.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((HOST, PORT))
    s.sendall((json.dumps({"cmd": cmd, "data": data}, ensure_ascii=False) + "\n").encode("utf-8"))
    buf = b""
    while True:
        bch = s.recv(1)
        if not bch or bch == b"\n":
            break
        buf += bch
    s.close()
    try:
        return json.loads(buf.decode("utf-8"))
    except:
        return {"ok": False, "msg": "No response"}

class Register(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register")
        self.setWindowIcon(QIcon("anydesk_icon.png"))
        self.u = QLineEdit()
        self.e = QLineEdit()
        self.p1 = QLineEdit(); self.p1.setEchoMode(QLineEdit.Password)
        self.p2 = QLineEdit(); self.p2.setEchoMode(QLineEdit.Password)
        f = QFormLayout()
        f.addRow("Username:", self.u)
        f.addRow("Email:", self.e)
        f.addRow("Password:", self.p1)
        f.addRow("Confirm Password:", self.p2)
        br = QPushButton("Create Account")
        bc = QPushButton("Cancel")
        h = QHBoxLayout(); h.addWidget(br); h.addWidget(bc)
        v = QVBoxLayout(self); v.addLayout(f); v.addLayout(h)
        br.clicked.connect(self.ok)
        bc.clicked.connect(self.reject)
        self.setFixedWidth(360)

    def ok(self):
        if not self.u.text().strip() or not self.e.text().strip() or not self.p1.text() or not self.p2.text():
            QMessageBox.warning(self, "חסר", "נא למלא את כל השדות."); return
        if "@" not in self.e.text() or "." not in self.e.text():
            QMessageBox.warning(self, "אימייל", "כתובת אימייל לא תקינה."); return
        if len(self.p1.text()) < 6:
            QMessageBox.warning(self, "סיסמה", "סיסמה חייבת להיות 6 תווים לפחות."); return
        if self.p1.text() != self.p2.text():
            QMessageBox.warning(self, "סיסמה", "הסיסמאות אינן תואמות."); return
        r = send("REGISTER", {"username": self.u.text().strip(), "email": self.e.text().strip(), "password": self.p1.text()})
        if r.get("ok"):
            QMessageBox.information(self, "הצלחה", r.get("msg","OK")); self.accept()
        else:
            QMessageBox.critical(self, "שגיאה", r.get("msg","Error"))

class Login(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon("anydesk_icon.png"))
        self.u = QLineEdit()
        self.p = QLineEdit(); self.p.setEchoMode(QLineEdit.Password)
        f = QFormLayout()
        f.addRow("Username / Email:", self.u)
        f.addRow("Password:", self.p)
        bl = QPushButton("Login")
        bc = QPushButton("Cancel")
        h = QHBoxLayout(); h.addWidget(bl); h.addWidget(bc)
        v = QVBoxLayout(self); v.addLayout(f); v.addLayout(h)
        bl.clicked.connect(self.ok)
        bc.clicked.connect(self.reject)
        self.setFixedWidth(360)

    def ok(self):
        if not self.u.text().strip() or not self.p.text():
            QMessageBox.warning(self, "חסר", "נא למלא שם משתמש/אימייל וסיסמה."); return
        r = send("LOGIN", {"user_or_email": self.u.text().strip(), "password": self.p.text()})
        if r.get("ok"):
            QMessageBox.information(self, "הצלחה", r.get("msg","OK")); self.accept()
        else:
            QMessageBox.critical(self, "שגיאה", r.get("msg","Error"))

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AnyDesk")
        self.setWindowIcon(QIcon("anydesk_icon.png"))
        c = QWidget(); self.setCentralWidget(c)
        v = QVBoxLayout(c)
        self.label = QLabel("Welcome to AnyDesk"); self.label.setAlignment(Qt.AlignCenter)
        s = QGuiApplication.primaryScreen().size()
        self.setFixedSize(QSize(s.width(), s.height()))
        v.addWidget(self.label)
        m: QMenuBar = self.menuBar()
        menu = m.addMenu(QIcon("down-arrow.png"), "")
        a1 = menu.addAction("Register")
        a2 = menu.addAction("Login")
        a1.triggered.connect(self.do_register)
        a2.triggered.connect(self.do_login)
        h = QHBoxLayout()
        b1 = QPushButton("Register"); b2 = QPushButton("Login")
        b1.clicked.connect(self.do_register); b2.clicked.connect(self.do_login)
        v.addLayout(h); h.addWidget(b1); h.addWidget(b2)
        self.current_user = None

    def do_register(self):
        d = Register(self)
        if d.exec():
            self.statusBar().showMessage("נרשמת. אפשר להתחבר.", 3000)

    def do_login(self):
        d = Login(self)
        if d.exec():
            self.current_user = d.u.text().strip()
            self.label.setText(f"Hello {self.current_user}! You are logged in.")
            self.statusBar().showMessage("Login success", 3000)

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("anydesk_icon.png"))
    w = Main(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
