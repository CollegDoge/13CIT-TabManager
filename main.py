from gui import *

os.environ['QT_API'] = 'pyqt6'

import sys
import qdarkstyle


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()