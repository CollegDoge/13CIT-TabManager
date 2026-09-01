import sys
import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDial,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QSlider,
    QSpinBox,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
)

from ics import interpret

class MainWindow(QMainWindow):
    def __init__(self):
        # window defaults
        super().__init__()
        self.setWindowTitle("TabManager")
        self.setGeometry(100, 100, 600, 900)
        self.setFixedSize(QSize(600, 900))

        pagelayout = QVBoxLayout()
        buttonlayout = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        # title
        titleWidget = QLabel("TabManager")

        font = titleWidget.font()
        font.setPointSize(30)
        font.setBold(True)
        
        titleWidget.setFont(font)
        titleWidget.setAlignment(
            Qt.AlignmentFlag.AlignHCenter
        )
        # buttons
        button1 = QPushButton("Upload")
        button1.setStyleSheet("background-color: red")
        button1.clicked.connect(self.on_click1)
        buttonlayout.addWidget(button1)

        button2 = QPushButton("Quit App")
        button2.setStyleSheet("background-color: blue")
        button2.clicked.connect(self.on_click2)
        buttonlayout.addWidget(button2)

        # widgets
        pagelayout.addWidget(titleWidget)
        pagelayout.addLayout(buttonlayout)
        pagelayout.addLayout(self.stacklayout)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)
    
    def on_click1(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "/", "ICS Files (*.ics)"
        )
        if file_path:
            print("Selected file:", file_path)
            interpret(file_path)

    def on_click2(self):
        print("App Closed.")
        self.close()