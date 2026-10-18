from gui import *

os.environ['QT_API'] = 'pyqt6'

import sys
import qdarkstyle
from func import startup

os.chdir(os.path.dirname(os.path.abspath(__file__))) 

def main():
    background = "--background" in sys.argv
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    startup.sync()
    window = MainWindow()
    if not background or window.tray is None:
        window.show()
    app.exec()

if __name__ == "__main__":
    main()