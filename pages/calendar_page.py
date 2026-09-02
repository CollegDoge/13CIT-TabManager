import sys
import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap
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
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QTabWidget,
)

class CalendarWindow(QMainWindow):
    def __init__(self, MainWindow):
        # window defaults
        super().__init__()
        self.main_window = MainWindow
        self.setWindowTitle("Calendar")
        self.setFixedSize(QSize(200, 200))

        buttonlayout = QVBoxLayout()

        # buttons
        backBtn = QPushButton("Back")
        backBtn.clicked.connect(self.go_back)
        buttonlayout.addWidget(backBtn)

        # widgets
        widget = QWidget()
        widget.setLayout(buttonlayout)
        self.setCentralWidget(widget)

    def go_back(self):
        self.hide()
        self.main_window.show()