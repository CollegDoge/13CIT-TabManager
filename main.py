import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

from gui import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()