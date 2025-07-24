"""
character_panel.py
GUI panel for managing Characters: add, edit, delete, list.
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
from GUI.storage.character_store import CharacterStore, Character


class CharacterPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.store = CharacterStore()
        self.init_ui()
        self.refresh_list()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        # Add/Edit fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name")
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Description")
        self.layout.addWidget(self.name_input)
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

        # Character insertion button
        self.insert_btn = QPushButton("Insert into Scene")
        self.insert_btn.setToolTip(
            "Insert selected character reference into the current scene"
        )
        self.insert_btn.clicked.connect(self.insert_character_reference)
        self.layout.addWidget(self.insert_btn)

        self.setLayout(self.layout)
        self.add_btn.clicked.connect(self.add_character)
        self.edit_btn.clicked.connect(self.edit_character)
        self.delete_btn.clicked.connect(self.delete_character)

    def refresh_list(self):
        self.list_widget.clear()
        for c in self.store.list():
            self.list_widget.addItem(f"{c.name} ({c.id})")

    def add_character(self):
        name = self.name_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Name is required.")
            return
        char = Character(id=str(uuid.uuid4()), name=name, description=desc)
        self.store.add(char)
        self.refresh_list()
        self.name_input.clear()
        self.desc_input.clear()

    def edit_character(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Selection Error", "Select a character to edit.")
            return
        char = self.store.list()[idx]
        name = self.name_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Name is required.")
            return
        char.name = name
        char.description = desc
        self.store.update(char)
        self.refresh_list()

    def delete_character(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            QMessageBox.warning(
                self, "Selection Error", "Select a character to delete."
            )
            return
        char = self.store.list()[idx]
        self.store.delete(char.id)
        self.refresh_list()
        self.name_input.clear()
        self.desc_input.clear()

    def insert_character_reference(self):
        """Insert a reference to the selected character into the active project editor"""
        idx = self.list_widget.currentRow()
        if idx < 0:
            QMessageBox.warning(
                self, "Selection Error", "Select a character to insert."
            )
            return

        char = self.store.list()[idx]
        char_ref = f"[{char.name}]"

        # Try to find the parent project editor
        parent = self.parent()
        while parent and not hasattr(parent, "text_editor"):
            parent = parent.parent() if hasattr(parent, "parent") else None

        if parent and hasattr(parent, "text_editor"):
            # Insert character reference at cursor position
            cursor = parent.text_editor.textCursor()
            cursor.insertText(char_ref)
            parent.text_editor.setFocus()
            QMessageBox.information(
                self, "Inserted", f"Character reference '{char_ref}' inserted."
            )
            print(f"[DEBUG] Inserted character reference: {char_ref}")
        else:
            # Copy to clipboard as fallback
            from PySide6.QtWidgets import QApplication

            clipboard = QApplication.clipboard()
            clipboard.setText(char_ref)
            QMessageBox.information(
                self, "Copied", f"Character reference '{char_ref}' copied to clipboard."
            )
            print(f"[DEBUG] Copied character reference to clipboard: {char_ref}")
