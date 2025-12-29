from PySide6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import sys

app = QApplication(sys.argv)

w = QWidget()

label_left = QLabel("Your Address")
label_right = QLabel("1 514 471 532")

# פונט (אפשר לשנות איך שבא לך)
label_left.setFont(QFont("Arial", 32))
label_right.setFont(QFont("Arial", 48, QFont.Bold))

# צבע טקסט (הכי פשוט)
label_left.setStyleSheet("color: black;")
label_right.setStyleSheet("color: #ff4a3d;")  # אדום-כתמתם כמו בתמונה

layout = QHBoxLayout(w)

# הכי חשוב בשביל "צמודים":
layout.setContentsMargins(0, 0, 0, 0)  # בלי שוליים
layout.setSpacing(0)                   # בלי רווח בין הווידג'טים

layout.addWidget(label_left)
layout.addWidget(label_right)

# (לא חובה) יישור לגובה/אמצע
layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

w.show()
sys.exit(app.exec())
