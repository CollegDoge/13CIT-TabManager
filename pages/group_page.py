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

class GroupWindow(QMainWindow):
    def __init__(self, MainWindow):
        super().__init__()
        self.main_window = MainWindow
        self.setWindowTitle("Add Groups")
        self.setGeometry(100, 100, 200, 200)
        self.setFixedSize(QSize(200, 200))

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
        self.hide()
        self.main_window.show()