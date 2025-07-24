"""
event_panel.py
GUI panel for managing Events: add, edit, delete, list.
Follows the structure of kanban_board.py, with UI/event logic separated from models/helpers.
"""

import uuid
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QLineEdit,
    QTextEdit,
    QHBoxLayout,
    QMessageBox,
)
from GUI.storage.event_store import EventStore, Event


class EventPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.store = EventStore()
        self.init_ui()
        self.refresh_list()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        # Add/Edit fields
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title")
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Description")
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(self.desc_input)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(btn_layout)

        self.setLayout(self.layout)
        self.add_btn.clicked.connect(self.add_event)
        self.edit_btn.clicked.connect(self.edit_event)
        self.delete_btn.clicked.connect(self.delete_event)

    def refresh_list(self):
        self.list_widget.clear()
        for e in self.store.list():
            self.list_widget.addItem(f"{e.title} ({e.id})")

    def add_event(self):
        title = self.title_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        if not title:
            QMessageBox.warning(self, "Input Error", "Title is required.")
            return
        event = Event(id=str(uuid.uuid4()), title=title, description=desc)
        self.store.add(event)
        self.refresh_list()
        self.title_input.clear()
        self.desc_input.clear()

    def edit_event(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Selection Error", "Select an event to edit.")
            return
        event = self.store.list()[idx]
        title = self.title_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        if not title:
            QMessageBox.warning(self, "Input Error", "Title is required.")
            return
        event.title = title
        event.description = desc
        self.store.update(event)
        self.refresh_list()

    def delete_event(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Selection Error", "Select an event to delete.")
            return
        event = self.store.list()[idx]
        self.store.delete(event.id)
        self.refresh_list()
        self.title_input.clear()
        self.desc_input.clear()
