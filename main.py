from gui import *

import sys
import qdarkstyle

os.environ['QT_API'] = 'pyqt5'

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()