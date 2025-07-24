"""
KanbanBoardWidget – PySide6 widget for plot and idea organization

This is a scaffold for the Kanban board feature. Implements a basic layout with columns and cards, ready for further development.

# Reason: Modular, testable, and follows project structure for GUI widgets.
"""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QInputDialog,
    QMessageBox,
    QMenu,
    QScrollArea,
    QSizePolicy,
    QFrame,
)
from PySide6.QtCore import Qt, Signal, QTimer
from GUI.storage import kanban_store
from dataclasses import dataclass


# Optional: Card data model for extensibility


from typing import List, Dict, Any, Optional, Callable

# Import the KanbanCardLinkWidget for navigation UI

from .kanban_card_link_widget import KanbanCardLinkWidget
from .kanban_models import KanbanCard, CardDetailsDialog, Column
from .kanban_board2 import (
    convert_kanban_to_timeline,
    navigate_to_link,
    sync_all_kanban_to_timeline,
    sync_column_kanban_to_timeline,
)
from PySide6.QtWidgets import QDialog
from PySide6.QtGui import QColor


import uuid


class KanbanBoardWidget(QWidget):
    def move_card_within_column(self, column_name, from_row, to_row):
        """Move a card within a column from one row to another."""
        col = self.column_map.get(column_name)
        if not col:
            return False
        lw = col.list_widget
        if from_row < 0 or from_row >= lw.count() or to_row < 0 or to_row >= lw.count():
            return False
        self.push_undo()
        item = lw.takeItem(from_row)
        lw.insertItem(to_row, item)
        lw.setCurrentRow(to_row)
        self.trigger_autosave()
        return True

    def move_card_between_columns(self, from_column, to_column, row):
        """Move a card from one column to another."""
        col_from = self.column_map.get(from_column)
        col_to = self.column_map.get(to_column)
        if not col_from or not col_to:
            return False
        lw_from = col_from.list_widget
        lw_to = col_to.list_widget
        if row < 0 or row >= lw_from.count():
            return False
        self.push_undo()
        item = lw_from.takeItem(row)
        lw_to.addItem(item)
        lw_to.setCurrentItem(item)
        lw_to.setFocus()
        self.trigger_autosave()
        return True

    def focus_column(self, column_name):
        """Set focus to the list widget of the given column."""
        col = self.column_map.get(column_name)
        if not col:
            return False
        col.list_widget.setFocus()
        return True

    def keyPressEvent(self, event):
        """
        Keyboard shortcuts for Kanban board:
        - Ctrl+N: Add card to selected column
        - Enter/F2: Edit selected card
        - Delete: Delete selected card
        - Ctrl+Up/Down: Move card within column
        - Ctrl+Left/Right: Move card between columns
        """
        from PySide6.QtGui import QKeySequence

        key = event.key()
        modifiers = event.modifiers()
        # Find focused list widget (column)
        focused_col = None
        for col in self.columns:
            if col.list_widget.hasFocus():
                focused_col = col
                break
        if not focused_col:
            super().keyPressEvent(event)
            return
        lw = focused_col.list_widget
        current_row = lw.currentRow()
        # Ctrl+N: Add card
        if (modifiers & Qt.ControlModifier) and key == Qt.Key_N:
            self._add_card(lw, focused_col.name)
            return
        # Enter or F2: Edit card
        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_F2):
            item = lw.currentItem()
            if item:
                self._edit_card(lw, focused_col.name, item)
            return
        # Delete: Delete card
        if key == Qt.Key_Delete:
            item = lw.currentItem()
            if item:
                self._delete_card(lw, focused_col.name, item)
            return
        # Ctrl+Up/Down: Move card within column
        if (modifiers & Qt.ControlModifier) and key in (Qt.Key_Up, Qt.Key_Down):
            item = lw.currentItem()
            if item and current_row != -1:
                target_row = current_row - 1 if key == Qt.Key_Up else current_row + 1
                if 0 <= target_row < lw.count():
                    self.push_undo()
                    lw.takeItem(current_row)
                    lw.insertItem(target_row, item)
                    lw.setCurrentRow(target_row)
                    self.trigger_autosave()
            return
        # Ctrl+Left/Right: Move card between columns
        if (modifiers & Qt.ControlModifier) and key in (Qt.Key_Left, Qt.Key_Right):
            item = lw.currentItem()
            if item and current_row != -1:
                col_idx = self.columns.index(focused_col)
                target_idx = col_idx - 1 if key == Qt.Key_Left else col_idx + 1
                if 0 <= target_idx < len(self.columns):
                    self.push_undo()
                    lw.takeItem(current_row)
                    target_col = self.columns[target_idx]
                    target_col.list_widget.addItem(item)
                    target_col.list_widget.setCurrentItem(item)
                    target_col.list_widget.setFocus()
                    self.trigger_autosave()
            return
        # Tab/Shift+Tab: Move focus between columns
        if key == Qt.Key_Tab:
            col_idx = self.columns.index(focused_col)
            next_idx = (col_idx + 1) % len(self.columns)
            self.columns[next_idx].list_widget.setFocus()
            return
        if key == Qt.Key_Backtab:
            col_idx = self.columns.index(focused_col)
            prev_idx = (col_idx - 1) % len(self.columns)
            self.columns[prev_idx].list_widget.setFocus()
            return
        # Otherwise, default
        super().keyPressEvent(event)

    def __init__(self, parent=None, get_available_links=None):
        self._loading = False  # Ensure always defined, before QWidget init
        super().__init__(parent)
        self.setWindowTitle("Kanban Board – Plot & Idea Organization")
        main_vbox = QVBoxLayout()
        # Add Sync All to Timeline button
        sync_all_btn = QPushButton("Sync All to Timeline")
        sync_all_btn.setAccessibleName("Sync All Kanban Cards to Timeline")
        sync_all_btn.setAccessibleDescription(
            "Button to sync all Kanban cards to the Timeline view"
        )
        sync_all_btn.clicked.connect(self._sync_all_to_timeline)
        main_vbox.addWidget(sync_all_btn)
        self.layout = QHBoxLayout()
        main_vbox.addLayout(self.layout)
        self.setLayout(main_vbox)
        self.columns = []  # List[Column]
        self.column_map = {}  # Dict[str, Column]
        self.get_available_links = get_available_links
        self._init_columns()
        # --- Autosave/Undo/Redo ---
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.timeout.connect(self._autosave)
        self._undo_stack = []
        self._redo_stack = []
        self._autosave_delay_ms = 1000
        self.load_board()

    def _sync_all_to_timeline(self):
        """
        Sync all Kanban cards in all columns to the Timeline. Delegates to kanban_board2 helper.
        """
        sync_all_kanban_to_timeline(self)

    def _convert_kanban_to_timeline_bulk(self, kanban_card):
        """
        Bulk version: returns status string instead of showing dialogs. Delegates to kanban_board2 helper.
        """
        from .kanban_board2 import convert_kanban_to_timeline_bulk

        return convert_kanban_to_timeline_bulk(self, kanban_card)

    def _autosave(self):
        if self._loading:
            return
        state = self.save_state(full=True)
        kanban_store.save_kanban_board(state)

    def trigger_autosave(self):
        if getattr(self, "_loading", False):
            return
        timer = getattr(self, "_autosave_timer", None)
        if timer is None:
            return
        timer.start(self._autosave_delay_ms)

    def push_undo(self):
        """
        Push current state to undo stack before making changes.
        Call this BEFORE making changes to capture the previous state.
        """
        if self._loading:
            return
        state = self.save_state(full=True)
        self._undo_stack.append(state)
        # Limit stack size
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            return
        self._redo_stack.append(self.save_state(full=True))
        state = self._undo_stack.pop()
        self.load_state(state)
        self.trigger_autosave()

    def redo(self):
        if not self._redo_stack:
            return
        self._undo_stack.append(self.save_state(full=True))
        state = self._redo_stack.pop()
        self.load_state(state)
        self.trigger_autosave()

    def load_board(self):
        self._loading = True
        state = kanban_store.load_kanban_board()
        if state:
            self.load_state(state)
        self._loading = False

    def add_column(self, title: str):
        """
        Add a new column with the given title. Does nothing if column exists.
        """
        if title in self.column_map:
            return  # Column already exists
        col = self._create_column(title)
        self.layout.addLayout(col.layout)
        self.columns.append(col)
        self.column_map[title] = col

    def rename_column(self, old_title: str, new_title: str):
        """
        Rename a column. Preserves cards. Updates accessibility names.
        """
        if old_title not in self.column_map or new_title in self.column_map:
            return  # Invalid operation
        col = self.column_map[old_title]
        col.name = new_title
        # Update label and accessibility
        label = col.layout.itemAt(0).widget()
        label.setText(new_title)
        label.setAccessibleName(f"Kanban Column: {new_title}")
        label.setAccessibleDescription(f"Column for {new_title} cards")
        # Update list widget accessibility
        lw = col.list_widget
        lw.setAccessibleName(f"{new_title} Card List")
        lw.setAccessibleDescription(f"List of cards in {new_title} column")
        # Update add button accessibility
        add_btn = col.add_btn
        add_btn.setAccessibleName(f"Add Card to {new_title}")
        add_btn.setAccessibleDescription(f"Button to add a card to {new_title} column")
        # Update mapping
        self.column_map[new_title] = col
        del self.column_map[old_title]

    def delete_column(self, title: str, parent_widget=None):
        """
        Delete a column and all its cards, with confirmation dialog.
        """
        if title not in self.column_map:
            return
        col = self.column_map[title]
        # Confirm deletion
        msg = QMessageBox(parent_widget or self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Delete Column")
        msg.setText(
            f"Delete column '{title}'? All its cards will be lost. This cannot be undone."
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ret = msg.exec()
        if ret != QMessageBox.Yes:
            return
        # Remove from layout and internal lists
        self.layout.removeItem(col.layout)
        for i in reversed(range(col.layout.count())):
            item = col.layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.columns = [c for c in self.columns if c != col]
        del self.column_map[title]
        # No card archiving; cards are deleted with the column
        # Reason: Simpler UX, avoids confusion

    def safe_emit_card_added(self, *args, **kwargs):
        """
        Emit card_added signal, catching exceptions in slots to prevent crashes.
        """
        try:
            self.card_added.emit(*args, **kwargs)
        except Exception as e:
            print(f"Exception in card_added slot: {e}")

    def safe_emit_card_deleted(self, *args, **kwargs):
        try:
            self.card_deleted.emit(*args, **kwargs)
        except Exception as e:
            print(f"Exception in card_deleted slot: {e}")

    def safe_emit_card_edited(self, *args, **kwargs):
        try:
            self.card_edited.emit(*args, **kwargs)
        except Exception as e:
            print(f"Exception in card_edited slot: {e}")

    def save_state(self, full=False):
        """
        Returns a dict representing the current board state.
        If full=True, includes card metadata for versioning/restore.
        """
        state = {}
        for col in self.columns:
            state[col.name] = []
            for i in range(col.list_widget.count()):
                card = col.list_widget.item(i)
                if full and isinstance(card, KanbanCard):
                    state[col.name].append(
                        {
                            "title": card.text(),
                            "metadata": getattr(card, "metadata", {}),
                        }
                    )
                else:
                    state[col.name].append(card.text())
        return state

    def load_state(self, state):
        """
        Loads the board state from a dict (column names and card texts or dicts).
        Ensures accessibility properties are set for each card.
        Adds defensive checks for missing metadata/links fields.
        """
        for col in self.columns:
            col.list_widget.clear()
            for card_data in state.get(col.name, []):
                if isinstance(card_data, dict):
                    metadata = card_data.get("metadata", {})
                    if not isinstance(metadata, dict):
                        metadata = {}
                    if "links" not in metadata or not isinstance(
                        metadata.get("links"), list
                    ):
                        metadata["links"] = []
                    card = KanbanCard(
                        card_data.get("title", ""),
                        metadata=metadata,
                    )
                else:
                    card = KanbanCard(card_data)
                card.setData(Qt.UserRole + 1, card.text())
                card.setData(Qt.UserRole + 2, f"Kanban card: {card.text()}")
                col.list_widget.addItem(card)

    # Signals for testability and decoupling
    card_added = Signal(str, str)  # column, card_text
    card_edited = Signal(str, int, str)  # column, card_index, new_text
    card_deleted = Signal(str, int)  # column, card_index

    # Note: Use safe_emit_* methods instead of .emit() for robust error handling

    def _init_columns(self):
        # Example columns: To Do, In Progress, Done
        for col_name in ["To Do", "In Progress", "Done"]:
            col = self._create_column(col_name)
            self.layout.addLayout(col.layout)
            self.columns.append(col)
            self.column_map[col.name] = col

    def _sync_column_to_timeline(self, list_widget):
        """
        Sync all Kanban cards in a column to the Timeline. Delegates to kanban_board2 helper.
        """
        sync_column_kanban_to_timeline(self, list_widget)

    def _add_card(self, list_widget: QListWidget, column_name: str):
        text, ok = QInputDialog.getText(self, "Add Card", "Card title:")
        if ok and text.strip():
            self.push_undo()
            card = KanbanCard(text.strip())
            list_widget.addItem(card)
            self.safe_emit_card_added(column_name, text.strip())
            self.trigger_autosave()

    def _create_column(self, title) -> Column:
        vbox = QVBoxLayout()
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setAccessibleName(f"Kanban Column: {title}")
        label.setAccessibleDescription(f"Column for {title} cards")
        vbox.addWidget(label)

        list_widget = QListWidget()
        list_widget.setAccessibleName(f"{title} Card List")
        list_widget.setAccessibleDescription(f"List of cards in {title} column")
        vbox.addWidget(list_widget)

        add_btn = QPushButton("Add Card")
        add_btn.setAccessibleName(f"Add Card to {title}")
        add_btn.setAccessibleDescription(f"Button to add a card to {title} column")
        vbox.addWidget(add_btn)

        sync_col_btn = QPushButton("Sync Column to Timeline")
        sync_col_btn.setAccessibleName(f"Sync {title} Column to Timeline")
        sync_col_btn.setAccessibleDescription(
            f"Button to sync all cards in {title} column to the Timeline view"
        )
        sync_col_btn.clicked.connect(
            lambda _, lw=list_widget: self._sync_column_to_timeline(lw)
        )
        vbox.addWidget(sync_col_btn)

        edit_btn = QPushButton("Edit Card")
        edit_btn.setAccessibleName(f"Edit Card in {title}")
        edit_btn.setAccessibleDescription(
            f"Button to edit selected card in {title} column"
        )
        edit_btn.setVisible(False)
        vbox.addWidget(edit_btn)
        delete_btn = QPushButton("Delete Card")
        delete_btn.setAccessibleName(f"Delete Card in {title}")
        delete_btn.setAccessibleDescription(
            f"Button to delete selected card in {title} column"
        )
        delete_btn.setVisible(False)
        vbox.addWidget(delete_btn)

        add_btn.clicked.connect(
            lambda _, lw=list_widget, col=title: self._add_card(lw, col)
        )

        list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        list_widget.customContextMenuRequested.connect(
            lambda pos, lw=list_widget, col=title: self._show_card_context_menu(
                lw, col, pos
            )
        )

        # Install double-click handler
        self._install_double_click(list_widget, title)

        # Add a card details panel below the list widget for navigation UI
        # Only add if not already present (avoid duplicate widgets)
        from PySide6.QtWidgets import QVBoxLayout as QVBoxLayout2, QWidget

        details_panel = QWidget()
        details_panel.setLayout(QVBoxLayout2())
        details_panel.setVisible(False)
        vbox.addWidget(details_panel)

        return Column(name=title, layout=vbox, list_widget=list_widget, add_btn=add_btn)

    def _edit_card(
        self, list_widget: QListWidget, column_name: str, item: QListWidgetItem
    ):
        if not isinstance(item, KanbanCard):
            return
        self.push_undo()
        # Pass available links to CardDetailsDialog
        available_links = self.get_available_links() if self.get_available_links else []
        dlg = CardDetailsDialog(item, self, available_links=available_links)
        if dlg.exec() == QDialog.Accepted:
            details = dlg.get_details()
            item.setText(details["title"])
            item.set_notes(details["notes"])
            item.set_tags(details["tags"])
            item.set_links(details["links"])
            if details["color"]:
                item.set_color(QColor(details["color"]))
            self.safe_emit_card_edited(
                column_name, list_widget.row(item), details["title"]
            )
            self.trigger_autosave()

    def _delete_card(
        self, list_widget: QListWidget, column_name: str, item: QListWidgetItem
    ):
        if not item:
            return
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Delete Card")
        msg.setText(f"Delete card '{item.text()}'? This cannot be undone.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ret = msg.exec()
        if ret == QMessageBox.Yes:
            self.push_undo()
            row = list_widget.row(item)
            list_widget.takeItem(row)
            self.safe_emit_card_deleted(column_name, row)
            self.trigger_autosave()

    def _show_card_context_menu(self, list_widget: QListWidget, column_name: str, pos):
        import os

        # In test/headless mode, or if pos is None, directly call conversion logic
        TEST_MODE = os.environ.get("TEST_MODE", "0") == "1"
        if pos is None or TEST_MODE:
            # For test: pick the first item if pos is None, else item at pos
            item = list_widget.item(0) if pos is None else list_widget.itemAt(pos)
            if not item:
                return
            # If test requests conversion, call it directly
            self._convert_kanban_to_timeline(item)
            return
        item = list_widget.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        edit_action = menu.addAction("Edit Details...")
        delete_action = menu.addAction("Delete Card")
        convert_action = menu.addAction("Convert to Timeline Card")
        action = menu.exec(list_widget.mapToGlobal(pos))
        if action == edit_action:
            self._edit_card(list_widget, column_name, item)
        elif action == delete_action:
            self._delete_card(list_widget, column_name, item)
        elif action == convert_action:
            self._convert_kanban_to_timeline(item)

    def _convert_kanban_to_timeline(self, kanban_card):
        return convert_kanban_to_timeline(self, kanban_card)

    # Double-click to open details dialog
    def _install_double_click(self, list_widget: QListWidget, column_name: str):
        def handler(item):
            # If card has a quick navigation link, navigate; else, open edit dialog
            if isinstance(item, KanbanCard):
                links = item.metadata.get("links", [])
                if links:
                    self._navigate_to_link(links[0])
                    return
            self._edit_card(list_widget, column_name, item)

        list_widget.itemDoubleClicked.connect(handler)

    def _create_column(self, title) -> Column:
        vbox = QVBoxLayout()
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setAccessibleName(f"Kanban Column: {title}")
        label.setAccessibleDescription(f"Column for {title} cards")
        vbox.addWidget(label)

        list_widget = QListWidget()
        list_widget.setAccessibleName(f"{title} Card List")
        list_widget.setAccessibleDescription(f"List of cards in {title} column")
        vbox.addWidget(list_widget)

        add_btn = QPushButton("Add Card")
        add_btn.setAccessibleName(f"Add Card to {title}")
        add_btn.setAccessibleDescription(f"Button to add a card to {title} column")
        vbox.addWidget(add_btn)

        sync_col_btn = QPushButton("Sync Column to Timeline")
        sync_col_btn.setAccessibleName(f"Sync {title} Column to Timeline")
        sync_col_btn.setAccessibleDescription(
            f"Button to sync all cards in {title} column to the Timeline view"
        )
        sync_col_btn.clicked.connect(
            lambda _, lw=list_widget: self._sync_column_to_timeline(lw)
        )
        vbox.addWidget(sync_col_btn)

        edit_btn = QPushButton("Edit Card")
        edit_btn.setAccessibleName(f"Edit Card in {title}")
        edit_btn.setAccessibleDescription(
            f"Button to edit selected card in {title} column"
        )
        edit_btn.setVisible(False)
        vbox.addWidget(edit_btn)
        delete_btn = QPushButton("Delete Card")
        delete_btn.setAccessibleName(f"Delete Card in {title}")
        delete_btn.setAccessibleDescription(
            f"Button to delete selected card in {title} column"
        )
        delete_btn.setVisible(False)
        vbox.addWidget(delete_btn)

        add_btn.clicked.connect(
            lambda _, lw=list_widget, col=title: self._add_card(lw, col)
        )

        list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        list_widget.customContextMenuRequested.connect(
            lambda pos, lw=list_widget, col=title: self._show_card_context_menu(
                lw, col, pos
            )
        )

        # Install double-click handler
        self._install_double_click(list_widget, title)

        # Add a card details panel below the list widget for navigation UI
        # Only add if not already present (avoid duplicate widgets)
        from PySide6.QtWidgets import QVBoxLayout as QVBoxLayout2, QWidget

        details_panel = QWidget()
        details_panel.setLayout(QVBoxLayout2())
        details_panel.setVisible(False)
        vbox.addWidget(details_panel)

        return Column(name=title, layout=vbox, list_widget=list_widget, add_btn=add_btn)
