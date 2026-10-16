import sys
import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QSlider,
    QPushButton,
    QStackedLayout,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QTabWidget,
)

# pages
from pages.group_page import GroupWindow
from pages.calendar_page import CalendarWindow

class MainWindow(QMainWindow):
    def __init__(self):
        # window defaults
        super().__init__()
        self.setWindowTitle("TabManager")
        self.setFixedSize(QSize(1000, 700))
        icon_path = os.path.join(os.path.dirname(__file__), "/assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))

        # page layout
        pagelayout = QVBoxLayout()
        titlelayout = QHBoxLayout()
        buttonlayout = QVBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.addLayout(titlelayout)
        pagelayout.addLayout(buttonlayout)
        pagelayout.addLayout(self.stacklayout)

        titlelayout.setAlignment(Qt.AlignLeft)
        buttonlayout.setAlignment(Qt.AlignLeft)
        buttonlayout.setSpacing(10)
        buttonlayout.setContentsMargins(10, 0, 0, 0)

        # title
        title = QLabel("TabManager")
        title.setFont(QFont("JetBrainsMono Nerd Font", 30))
        titlelayout.addWidget(title)

        # button
        button1 = QPushButton("Add Tab Groups")
        button1.clicked.connect(self.group_page)
        buttonlayout.addWidget(button1)

        button2 = QPushButton("Manage Calendar")
        button2.clicked.connect(self.calendar_page)
        buttonlayout.addWidget(button2)

        button3 = QPushButton("Test Launch Website")
        button3.clicked.connect(self.test_launch)
        buttonlayout.addWidget(button3)

        button4 = QPushButton("Quit App")
        button4.clicked.connect(self.quit_app)
        buttonlayout.addWidget(button4)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def group_page(self):
        self.group = GroupWindow(self)
        self.group.show()
        self.hide()
        
    def calendar_page(self):
        self.calendar = CalendarWindow(self)
        self.calendar.show()
        self.hide()

    def test_launch(self):
        print("Launching Website")
        os.system("firefox https://www.google.com")

    def quit_app(self):
        print("App Closed.")
        self.close()