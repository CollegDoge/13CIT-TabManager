import sys
import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
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
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QTabWidget,
)

# pages
from pages.group_page import GroupWindow
from pages.calendar_page import CalendarWindow
from pages.settings_page import SettingsWindow

class MainWindow(QMainWindow):
    def __init__(self):
        # window defaults
        super().__init__()
        self.setWindowTitle("TabManager")
        self.setFixedSize(QSize(400, 500))

        icon_path = os.path.join(os.path.dirname(__file__), "/assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))

        buttonlayout = QVBoxLayout()
        buttonlayout.setSpacing(0)

        self.stacklayout = QStackedLayout()
        
        # buttons
        button1 = QPushButton("Add Tab Groups")
        button1.clicked.connect(self.group_page)
        buttonlayout.addWidget(button1)

        button2 = QPushButton("Manage Calendar")
        button2.clicked.connect(self.calendar_page)
        buttonlayout.addWidget(button2)

        button3 = QPushButton("Open Settings");
        button3.clicked.connect(self.settings_page)
        buttonlayout.addWidget(button3)

        button4 = QPushButton("Quit App")
        button4.clicked.connect(self.quit_app)
        buttonlayout.addWidget(button4)

        # widgets
        widget = QWidget()
        widget.setLayout(buttonlayout)
        self.setCentralWidget(widget)

    def group_page(self):
        self.group = GroupWindow(self)
        self.group.show()
        self.hide()
        
    def calendar_page(self):
        self.calendar = CalendarWindow(self)
        self.calendar.show()
        self.hide()
    
    def settings_page(self):
        self.settings = SettingsWindow(self)
        self.settings.show()
        self.hide()

    def quit_app(self):
        print("App Closed.")
        self.close()