import sys
import os

from PyQt6.QtCore import QSize, Qt, pyqtSignal
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

class GroupWindow(QMainWindow):
    back_to_main_signal = pyqtSignal()

    def __init__(self):
        # window defaults
        super().__init__()
        self.setWindowTitle("TabManager - Manage Groups")
        self.setFixedSize(QSize(1000, 700))
        icon_path = os.path.join(os.path.dirname(__file__), "assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))

        buttonlayout = QVBoxLayout()

        # buttons
        backBtn = QPushButton("Back")
        backBtn.clicked.connect(self.go_back)
        buttonlayout.addWidget(backBtn)


        # add both buttons and titles to widget
        widget = QWidget()
        widget.setLayout(buttonlayout)
        self.setCentralWidget(widget)

    def go_back(self):
        self.back_to_main_signal.emit()
        self.hide()