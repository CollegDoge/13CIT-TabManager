import sys
import os

from PyQt6.QtCore import QSize, Qt
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

# pages
from pages.group_page import GroupWindow
from pages.calendar_page import CalendarWindow
from func.group import get_available_browsers, grouptest

class MainWindow(QMainWindow):
    def __init__(self):
        # window defaults
        super().__init__()
        self.setWindowTitle("TabManager")
        self.setFixedSize(QSize(1000, 700))
        icon_path = os.path.join(os.path.dirname(__file__), "assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))

        # page layouts
        pagelayout = QVBoxLayout()
        titlelayout = QHBoxLayout()
        grouplayout = QHBoxLayout()
        optionslayout = QVBoxLayout()
        calendarlayout = QVBoxLayout()
        bottombar = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.setSpacing(15)
        pagelayout.addLayout(titlelayout)
        pagelayout.addLayout(grouplayout)
        pagelayout.addLayout(optionslayout)
        pagelayout.addLayout(calendarlayout)
        pagelayout.addLayout(bottombar)
        pagelayout.addLayout(self.stacklayout)

        # page layout config
        titlelayout.setAlignment(Qt.AlignLeft)

        grouplayout.setAlignment(Qt.AlignLeft)
        grouplayout.setSpacing(10)
        grouplayout.setContentsMargins(10, 5, 0, 0)

        optionslayout.setAlignment(Qt.AlignLeft)
        optionslayout.setSpacing(5)
        optionslayout.setContentsMargins(10, 5, 0, 0)

        calendarlayout.setAlignment(Qt.AlignLeft)
        calendarlayout.setSpacing(10)
        calendarlayout.setContentsMargins(10, 5, 0, 0)

        bottombar.setAlignment(Qt.AlignRight)
        bottombar.setSpacing(10)
        bottombar.setContentsMargins(10, 5, 0, 0)

        # title
        title_label = QLabel("<b>TabManager</b> - v0.1.0")
        title_label.setFont(QFont("Inter", 30))
        titlelayout.addWidget(title_label)

        # button
        testgroup1 = QPushButton("Test Group 1")
        testgroup1.clicked.connect(self.launch)
        grouplayout.addWidget(testgroup1)

        testgroup2 = QPushButton("Test Group 2")
        testgroup2.clicked.connect(self.launch)
        grouplayout.addWidget(testgroup2)

        testgroup3 = QPushButton("Test Group 3")
        testgroup3.clicked.connect(self.launch)
        grouplayout.addWidget(testgroup3)

        groupadd = QPushButton("Add Tab Groups")
        groupadd.clicked.connect(self.group_page)
        grouplayout.addWidget(groupadd)

        opt_browser_title = QLabel("Select Browser")
        self.opt_browser = QComboBox()
        opt_browser_custom = QPushButton("Custom") # LATER

        available_browsers = get_available_browsers()
        for display_name, path in available_browsers:
            self.opt_browser.addItem(display_name, path)

        opt1 = QHBoxLayout()
        opt1.addWidget(opt_browser_title)
        opt1.addWidget(self.opt_browser)
        opt1.addWidget(opt_browser_custom)
        opt1.setSpacing(20)
        optionslayout.addLayout(opt1)

        # WILL DO LATER
        opt_profile_title = QLabel("Select Profile")
        opt_profile = QComboBox()

        opt2 = QHBoxLayout()
        opt2.addWidget(opt_profile_title)
        opt2.addWidget(opt_profile)
        opt2.setSpacing(20)
        optionslayout.addLayout(opt2)

        opt_startup = QCheckBox("Start app with PC")
        opt_startup.setChecked(False)
        optionslayout.addWidget(opt_startup)

        opt_startup_warn = QLabel("Windows only, use alternative methods if using Linux/MacOS)")
        opt_startup_warn.setFont(QFont("Inter", 8))
        optionslayout.addWidget(opt_startup_warn)

        opt_destructive = QCheckBox("Destructive Mode")
        opt_destructive.setChecked(False)
        optionslayout.addWidget(opt_destructive)

        opt_destructive_warn = QLabel("Closes all other tabs on launch. Be careful.")
        opt_destructive_warn.setFont(QFont("Inter", 8))
        optionslayout.addWidget(opt_destructive_warn)

        calendaradd = QPushButton("Manage Calendar")
        calendaradd.clicked.connect(self.calendar_page)
        calendarlayout.addWidget(calendaradd)

        quitbtn = QPushButton("Quit App")
        quitbtn.clicked.connect(self.quit_app)
        bottombar.addWidget(quitbtn)
        
        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

        self.calendar_window = None
        self.group_window = None

    def group_page(self):
        if self.group_window is None:
            self.group_window = GroupWindow()
            self.group_window.back_to_main_signal.connect(self.show)
        self.group_window.show()
        self.hide()
        
    def calendar_page(self):
        if self.calendar_window is None:
            self.calendar_window = CalendarWindow()
            self.calendar_window.back_to_main_signal.connect(self.show)
        self.calendar_window.show()
        self.hide()
    
    def launch(self):
        selected_path = self.opt_browser.currentData()
        grouptest(selected_path)

    def quit_app(self):
        print("App Closed.")
        self.close()