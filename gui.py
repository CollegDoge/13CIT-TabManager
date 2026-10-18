import sys
import os
import platform

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QFont, QAction
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
    QMessageBox,
    QTabWidget,
    QGridLayout,
    QSystemTrayIcon,
    QMenu,
)

# pages
from pages.group_page import GroupWindow
from pages.calendar_page import CalendarWindow
from func.group import get_available_browsers, open_group, add_custom_browser
from func import groupstore, startup

ACC_COLOR = "#213A73"   # nice blue color
BORDER_COLOR = "#3A6BDB"   # nice blue color
ERROR_COLOR = "#e06c75" # nice red color
OK_COLOR = "#98c379"    # nice green color 

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
        titlelayout = QVBoxLayout()
        grouplayout = QHBoxLayout()
        groupaddlayout = QHBoxLayout()
        optionslayout = QVBoxLayout()
        calendarlayout = QVBoxLayout()
        bottombar = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.setSpacing(15)
        pagelayout.addLayout(titlelayout)
        pagelayout.addLayout(grouplayout)
        pagelayout.addLayout(groupaddlayout)
        pagelayout.addLayout(optionslayout)
        pagelayout.addLayout(calendarlayout)
        pagelayout.addLayout(bottombar)
        pagelayout.addLayout(self.stacklayout)

        # page layout config
        titlelayout.setAlignment(Qt.AlignLeft)
        titlelayout.setSpacing(0)

        grouplayout.setAlignment(Qt.AlignLeft)
        grouplayout.setSpacing(10)
        grouplayout.setContentsMargins(15, 0, 0, 0)

        groupaddlayout.setAlignment(Qt.AlignLeft)
        groupaddlayout.setSpacing(10)
        groupaddlayout.setContentsMargins(15, 5, 0, 10)

        optionslayout.setAlignment(Qt.AlignLeft)
        optionslayout.setSpacing(5)
        optionslayout.setContentsMargins(15, 5, 0, 0)

        calendarlayout.setAlignment(Qt.AlignLeft)
        calendarlayout.setSpacing(10)
        calendarlayout.setContentsMargins(15, 5, 0, 0)

        bottombar.setAlignment(Qt.AlignRight)
        bottombar.setSpacing(10)

        # title
        title_label = QLabel("<b>TabManager</b> - v0.1.0")
        title_label.setFont(QFont("Inter", 30))
        titlelayout.addWidget(title_label)

        subtitle_label = QLabel("  Quick Launch")
        subtitle_label.setFont(QFont("Inter", 15))
        titlelayout.addWidget(subtitle_label)

        # button
        self.quicklayout = QGridLayout()
        self.quicklayout.setSpacing(10)
        grouplayout.addLayout(self.quicklayout)

        groupadd = QPushButton("Add/Modify Tab Groups")
        groupadd.setFixedSize(QSize(200, 30))
        groupadd.setIcon(QIcon("assets/add.png"))
        groupadd.setStyleSheet(f"background-color: {ACC_COLOR};")
        groupadd.clicked.connect(self.group_page)
        groupaddlayout.addWidget(groupadd)

        opt_browser_title = QLabel("Select Browser")
        self.opt_browser = QComboBox()
        self.opt_browser.setFixedSize(QSize(200, 30))
        
        opt_browser_custom = QPushButton("")
        opt_browser_custom.setFixedSize(QSize(30, 30))
        opt_browser_custom.setIcon(QIcon("assets/folder.png"))
        opt_browser_custom.clicked.connect(self.browse_browser)

        available_browsers = get_available_browsers()
        for display_name, path in available_browsers:
            self.opt_browser.addItem(display_name, path)

        opt1 = QHBoxLayout()
        opt1.addWidget(opt_browser_title)
        opt1.addWidget(self.opt_browser)
        opt1.addWidget(opt_browser_custom)
        opt1.setSpacing(20)
        optionslayout.addLayout(opt1)

        self.opt_startup = QCheckBox("Start app with PC")
        if startup.is_supported():
            self.opt_startup.setChecked(startup.is_enabled())
            self.opt_startup.clicked.connect(self.toggle_startup)
        else:
            self.opt_startup.setEnabled(False)
            self.opt_startup.setToolTip("Only available on Windows")
        optionslayout.addWidget(self.opt_startup)

        opt_startup_warn = QLabel("Windows only, use alternative methods if using Linux")
        opt_startup_warn.setFont(QFont("Inter", 8))
        optionslayout.addWidget(opt_startup_warn)

        calendaradd = QPushButton("Manage Calendar")
        calendaradd.setFixedSize(QSize(200, 30))
        calendaradd.setIcon(QIcon("assets/calendar.png"))
        calendaradd.setStyleSheet(f"background-color: {ACC_COLOR};")
        calendaradd.clicked.connect(self.calendar_page)
        calendarlayout.addWidget(calendaradd)

        quitbtn = QPushButton("Quit App")
        quitbtn.setFixedSize(QSize(80, 30))
        quitbtn.setStyleSheet(f"background-color: {ERROR_COLOR}; color: #000")
        quitbtn.clicked.connect(self.quit_app)
        bottombar.addWidget(quitbtn)
        
        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

        self.calendar_window = None
        self.group_window = None
        self.refresh_group_buttons()
        self.setup_tray(icon_path)

    # open group page
    def group_page(self):
        if self.group_window is None:
            self.group_window = GroupWindow()
            self.group_window.back_to_main_signal.connect(self.show)
            self.group_window.groups_changed.connect(self.refresh_group_buttons)
        self.group_window.show()
        self.hide()
        
    # open calendar page
    def calendar_page(self):
        if self.calendar_window is None:
            self.calendar_window = CalendarWindow()
            self.calendar_window.back_to_main_signal.connect(self.show)
        self.calendar_window.show()
        self.hide()
    
    # refresh the quick launch buttons
    def refresh_group_buttons(self):
        while self.quicklayout.count():
            w = self.quicklayout.takeAt(0).widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        for i, group in enumerate(groupstore.load_groups()):
            btn = QPushButton(group["name"])
            btn.setFixedSize(QSize(180,90))
            btn.setStyleSheet(f"border: 2px solid {BORDER_COLOR}; background-color: {ACC_COLOR}; font-size: 14px;")
            btn.clicked.connect(lambda checked=False, g=group: self.launch_group(g))
            self.quicklayout.addWidget(btn, i // 5, i % 5)  # max 5 per row

    # launch a tab group
    def launch_group(self, group):
        open_group(group, self.opt_browser.currentData())

    # "start app with PC" checkbox (Windows only)
    def toggle_startup(self, checked):
        try:
            if checked:
                startup.enable()
            else:
                startup.disable()
        except OSError as e:
            self.opt_startup.setChecked(not checked)  # revert
            QMessageBox.warning(self, "something got cooked.. sorry", str(e))

    # tray icon: lets the app keep running (and start hidden) in the background
    def setup_tray(self, icon_path):
        self.tray = None
        self.really_quit = False
        self.tray_hint_shown = False
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray = QSystemTrayIcon(QIcon(icon_path), self)
        self.tray.setToolTip("TabManager")

        menu = QMenu(self)
        open_action = QAction("Open TabManager", menu)
        open_action.triggered.connect(self.show_main)
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(open_action)
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

        # closing windows should leave the app running in the tray
        QApplication.setQuitOnLastWindowClosed(False)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # left click
            self.show_main()

    def show_main(self):
        # if a sub-page is open, bring that forward instead of stacking windows
        for w in (self.group_window, self.calendar_window):
            if w is not None and w.isVisible():
                w.raise_()
                w.activateWindow()
                return
        self.show()
        self.raise_()
        self.activateWindow()

    # the X button hides to tray instead of quitting (if a tray exists)
    def closeEvent(self, event):
        if self.tray is not None and not self.really_quit:
            event.ignore()
            self.hide()
            if not self.tray_hint_shown:
                self.tray_hint_shown = True
                self.tray.showMessage(
                    "TabManager",
                    "Still running in the system tray. Right-click the icon to quit.",
                    QSystemTrayIcon.MessageIcon.Information,
                    4000,
                )
        else:
            event.accept()

    # add a custom browser
    def browse_browser(self):
        # platform dependent
        if platform.system() == "Windows":
            start_dir = os.environ.get("ProgramFiles", "C:/Program Files")
            file_filter = "Executables (*.exe);;All files (*)"
        else:
            start_dir = "/usr/bin"
            file_filter = "All files (*)"

        path, _ = QFileDialog.getOpenFileName(
            self, "Select browser executable", start_dir, file_filter
        )

        # error prevention
        if not path:
            return
        try:
            name, path = add_custom_browser(path)
        except ValueError as e:
            QMessageBox.warning(self, "Can't use that file", str(e))
            return

        # add to dropdown
        index = self.opt_browser.findData(path)
        if index == -1:
            self.opt_browser.addItem(name, path)
            index = self.opt_browser.count() - 1
        self.opt_browser.setCurrentIndex(index)

    # quit the app
    def quit_app(self):
        print("App Closed.")
        self.really_quit = True
        QApplication.quit()