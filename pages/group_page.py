import os

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from func import groupstore

ACC_COLOR = "#213A73"   # nice blue color
ERROR_COLOR = "#e06c75" # nice red color
OK_COLOR = "#98c379"    # nice green color 

class GroupCard(QFrame):
    edit_requested = pyqtSignal(str)    # group id
    delete_requested = pyqtSignal(str)  # group id

    def __init__(self, group):
        # window defaults
        super().__init__()
        self.group_id = group["id"]
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed) # ensured that boxes remained the same size. bug fix.

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        header = QHBoxLayout()
        name = QLabel(group["name"])
        name.setTextFormat(Qt.TextFormat.PlainText)  # names are user input
        name_font = name.font()
        name_font.setBold(True)
        name_font.setPointSize(12)
        name.setFont(name_font)

        # count (how many tabs)
        count = len(group["urls"])
        count_label = QLabel(f"{count} tab{'s' if count != 1 else ''}")
        count_label.setFont(QFont("Inter", 8))

        # header
        header.addWidget(name)
        header.addStretch()
        header.addWidget(count_label)
        layout.addLayout(header)

        # long lists scroll inside the card
        urls = QListWidget()
        urls.addItems(group["urls"])
        urls.setMaximumHeight(90)
        urls.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        urls.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(urls)

        buttons = QHBoxLayout()
        buttons.addStretch()
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.group_id))
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.group_id))
        buttons.addWidget(edit_btn)
        buttons.addWidget(delete_btn)
        layout.addLayout(buttons)


class GroupWindow(QMainWindow):
    back_to_main_signal = pyqtSignal()
    groups_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TabManager - Manage Groups")
        self.setFixedSize(QSize(1000, 700))
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))

        self.editing_id = None  # None = creating a new group

        pagelayout = QVBoxLayout()
        pagelayout.setSpacing(15)

        # title
        title_label = QLabel("<b>Tab Groups</b>")
        title_label.setFont(QFont("Inter", 24))
        pagelayout.addWidget(title_label)

        # left/right split pefectly 50/50
        body = QHBoxLayout()
        body.setSpacing(20)
        body.setContentsMargins(10, 0, 10, 0)
        body.addLayout(self._build_editor(), 1)
        body.addLayout(self._build_group_list(), 1)

        pagelayout.addLayout(body, 1)

        # bottom bar
        bottombar = QHBoxLayout()
        bottombar.setAlignment(Qt.AlignmentFlag.AlignRight)
        bottombar.setSpacing(10)
        bottombar.setContentsMargins(10, 5, 0, 0)
        backBtn = QPushButton("Back")
        backBtn.setFixedSize(QSize(80, 30))
        backBtn.setStyleSheet(f"background-color: {ACC_COLOR};")
        backBtn.clicked.connect(self.go_back)
        bottombar.addWidget(backBtn)
        pagelayout.addLayout(bottombar)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

        self.refresh_cards()
        self.reset_editor()

    # RIGHT SIDE
    def _build_group_list(self):
        curgrouplayout = QVBoxLayout()

        # title
        curgrouplayout.addWidget(QLabel("<b>Saved groups</b>"))

        # boxes
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(10)

        # scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.cards_container)
        curgrouplayout.addWidget(scroll)
        return curgrouplayout

    # LEFT SIDE
    def _build_editor(self):
        newgrouplayout = QVBoxLayout()
        newgrouplayout.setSpacing(8)

        # title
        self.editor_title = QLabel()
        newgrouplayout.addWidget(self.editor_title)

        # group name
        newgrouplayout.addWidget(QLabel("Group name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g Stats Work Frfr")
        self.name_input.setMaxLength(24)
        newgrouplayout.addWidget(self.name_input)

        # URLs
        newgrouplayout.addWidget(QLabel("Add a URL (or pop several in with spaces between each)"))
        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("e.g. google.com")
        self.url_input.returnPressed.connect(self.add_url)
        add_btn = QPushButton("Add")
        add_btn.setFixedSize(QSize(50, 25))
        add_btn.clicked.connect(self.add_url)
        url_row.addWidget(self.url_input)
        url_row.addWidget(add_btn)
        newgrouplayout.addLayout(url_row)

        # URL box
        self.url_list = QListWidget()
        self.url_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.url_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        newgrouplayout.addWidget(self.url_list, 1)

        hint = QLabel("hint: you can drag to reorder, and delete selected URLs")
        hint.setFont(QFont("Inter", 8))
        newgrouplayout.addWidget(hint)

        # remove button (selected URL)
        remove_btn = QPushButton("Remove selected")
        remove_btn.clicked.connect(self.remove_selected_urls)
        newgrouplayout.addWidget(remove_btn)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        newgrouplayout.addWidget(self.status_label)

        # action row (cancel/save)
        action_row = QHBoxLayout()
        action_row.addStretch()
        self.cancel_btn = QPushButton("Cancel edit")
        self.cancel_btn.setFixedSize(QSize(80, 30))
        self.cancel_btn.clicked.connect(self.reset_editor)
        self.save_btn = QPushButton("Create group")
        self.save_btn.setFixedSize(QSize(80, 30))
        self.save_btn.clicked.connect(self.save_group)
        action_row.addWidget(self.cancel_btn)
        action_row.addWidget(self.save_btn)
        newgrouplayout.addLayout(action_row)
        return newgrouplayout

    # keybinds as well as clicking buttons
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete and self.url_list.hasFocus():
            self.remove_selected_urls()
        else:
            super().keyPressEvent(event)

    # if anything gets cooked
    def show_error(self, text):
        self.status_label.setStyleSheet(f"color: {ERROR_COLOR};")
        self.status_label.setText(text)

    # if everything is working (hopefully)
    def show_ok(self, text):
        self.status_label.setStyleSheet(f"color: {OK_COLOR};")
        self.status_label.setText(text)

    # refresh the list of cards (tab groups)
    def refresh_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        # if none exist, show message
        groups = groupstore.load_groups()
        if not groups:
            empty = QLabel("No tab groups yet! Create one on the right :)")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_layout.addWidget(empty)
            return

        # add cards (fixed size now)
        for group in groups:
            card = GroupCard(group)
            card.edit_requested.connect(self.start_edit)
            card.delete_requested.connect(self.confirm_delete)
            self.cards_layout.addWidget(card)
            self.cards_layout.addStretch()

    # start editing a group (right column)
    def start_edit(self, group_id):
        group = groupstore.get_group(group_id)
        if group is None:
            self.refresh_cards()
            return
        self.editing_id = group_id
        self.editor_title.setText(f"<b>Editing:</b> {group['name']}")
        self.name_input.setText(group["name"])
        self.url_list.clear()
        self.url_list.addItems(group["urls"])
        self.url_input.clear()
        self.status_label.clear()
        self.save_btn.setText("Save changes")
        self.cancel_btn.setVisible(True)

    # delete confirm popup
    def confirm_delete(self, group_id):
        group = groupstore.get_group(group_id)
        if group is None:
            return
        answer = QMessageBox.question(
            self,
            "Delete group",
            f"Delete '{group['name']}'? Thats permenant... A long time..",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        groupstore.delete_group(group_id)
        if self.editing_id == group_id:
            self.reset_editor()
        self.refresh_cards()
        self.groups_changed.emit()

    # reset editor
    def reset_editor(self):
        self.editing_id = None
        self.editor_title.setText("<b>New group</b>")
        self.name_input.clear()
        self.url_input.clear()
        self.url_list.clear()
        self.status_label.clear()
        self.save_btn.setText("Create group")
        self.save_btn.setStyleSheet(f"background-color: {OK_COLOR}; color: #000")
        self.cancel_btn.setVisible(False)

    # get all URLs in the list
    def current_urls(self):
        return [self.url_list.item(i).text() for i in range(self.url_list.count())]

    # add a URL to the list
    def add_url(self):
        raw = self.url_input.text()
        if not raw.strip():
            return

        # check for problems with the URL
        existing = self.current_urls()
        problems = []
        for piece in raw.split():
            try:
                url = groupstore.normalize_url(piece)
            except groupstore.InvalidURL as e:
                problems.append(str(e))
                continue
            if url not in existing:
                self.url_list.addItem(url)
                existing.append(url)

        # notify user of errors
        if problems:
            self.show_error(" ".join(problems))
        else:
            self.status_label.clear()
            self.url_input.clear()
        self.url_input.setFocus()

    # remove selected URLs from the list
    def remove_selected_urls(self):
        for item in self.url_list.selectedItems():
            self.url_list.takeItem(self.url_list.row(item))

    # save the group
    def save_group(self):
        name = self.name_input.text()
        urls = self.current_urls()
        try:
            if self.editing_id:
                groupstore.update_group(self.editing_id, name, urls)
                message = "Saved ur changes :)"
            else:
                groupstore.add_group(name, urls)
                message = "Group created successfully :D"

        # error prevention, LLM recommends this
        except (ValueError, KeyError) as e:
            self.show_error(str(e))
            return
        except OSError as e:
            self.show_error(f"Something got cooked - {e}")
            return

        self.reset_editor()
        self.show_ok(message)
        self.refresh_cards()
        self.groups_changed.emit()

    # back to main window
    def go_back(self):
        self.back_to_main_signal.emit()
        self.hide()