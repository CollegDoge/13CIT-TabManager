from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TabManager")
        self.setGeometry(100, 100, 800, 600)
        self.button = QPushButton("test button", self)
        self.button.move(50, 50)
        self.button.clicked.connect(self.on_click)
        self.show()

    def on_click(self):
        print("Clicked!")
        self.close()