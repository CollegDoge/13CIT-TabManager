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

from ics import interpret

class CalendarWindow(QMainWindow):
    def __init__(self, MainWindow):
        # window defaults
        super().__init__()
        self.main_window = MainWindow
        self.setWindowTitle("Calendar")
        self.setFixedSize(QSize(200, 200))

        buttonlayout = QVBoxLayout()

        # buttons
        icsImportBtn = QPushButton("Import ICS")
        icsImportBtn.clicked.connect(self.ics_import)
        buttonlayout.addWidget(icsImportBtn)

        backBtn = QPushButton("Back")
        backBtn.clicked.connect(self.go_back)
        buttonlayout.addWidget(backBtn)

        # widgets
        widget = QWidget()
        widget.setLayout(buttonlayout)
        self.setCentralWidget(widget)

    def ics_import(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "/", "ICS Files (*.ics)"
        )
        if file_path:
            print("Selected file:", file_path)
            interpret(file_path)

    def go_back(self):
        self.hide()
        self.main_window.show()