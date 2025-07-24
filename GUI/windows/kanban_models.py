"""
kanban_models.py – Data models and dialogs for Kanban board (split from kanban_board2.py)

Contains KanbanCard, CardDetailsDialog, Column dataclass.
"""

from PySide6.QtWidgets import (
    QListWidgetItem,
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QTextEdit,
    QColorDialog,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QListWidget,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from dataclasses import dataclass
import uuid
from typing import List, Dict, Any, Optional


class KanbanCard(QListWidgetItem):
    """
    KanbanCard represents a card in the Kanban board.
    metadata fields (shared with TimelineCard):
        id (str): Unique card ID (uuid4 hex)
        title (str): Card title
        notes (str): Freeform notes for the card.
        tags (List[str]): List of tags for filtering/searching.
        color (Optional[str]): Hex color string for card background.
        links (List[str]): List of scene/chapter IDs this card is linked to for quick navigation.
    """

    def _get_card_size_hint(self):
        from PySide6.QtCore import QSize

        return QSize(200, 70)

    def _set_card_style(self):
        self.setData(
            Qt.UserRole + 3,
            "border: 1px solid #bbb; border-radius: 6px; margin: 6px 0; padding: 8px 6px; background: #fff;",
        )

    def __init__(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        super().__init__(text)
        default_metadata = {
            "id": str(uuid.uuid4()),
            "title": text,
            "notes": "",
            "tags": [],
            "color": None,
            "links": [],
        }
        if metadata:
            merged = metadata.copy()
            for k, v in default_metadata.items():
                if k not in merged:
                    merged[k] = v
            self.metadata = merged
        else:
            self.metadata = default_metadata
        self.setData(Qt.UserRole + 1, self.metadata["title"])
        self.setData(Qt.UserRole + 2, f"Kanban card: {self.metadata['title']}")
        self.setData(Qt.AccessibleTextRole, f"Kanban Card: {self.metadata['title']}")
        self.setData(
            Qt.AccessibleDescriptionRole,
            f"Card for plot/idea: {self.metadata['title']}",
        )
        self.setSizeHint(self._get_card_size_hint())
        self._set_card_style()
        if self.metadata.get("color"):
            self.setBackground(QColor(self.metadata["color"]))

    def set_color(self, color: "QColor") -> None:
        self.metadata["color"] = color.name()
        self.setBackground(color)

    def set_notes(self, notes: str) -> None:
        self.metadata["notes"] = notes

    def set_tags(self, tags: List[str]) -> None:
        self.metadata["tags"] = tags

    def set_links(self, links: List[str]) -> None:
        self.metadata["links"] = links


class CardDetailsDialog(QDialog):
    def __init__(self, card: KanbanCard, parent=None, available_links=None):
        super().__init__(parent)
        self.setWindowTitle("Card Details")
        self.setAccessibleName("Card Details Dialog")
        self.setAccessibleDescription(
            "Dialog for editing Kanban card details, notes, tags, and links."
        )
        self.card = card
        layout = QVBoxLayout(self)
        self.text_edit = QLineEdit(card.text())
        layout.addWidget(QLabel("Title:"))
        layout.addWidget(self.text_edit)
        self.notes_edit = QTextEdit(card.metadata.get("notes", ""))
        layout.addWidget(QLabel("Notes:"))
        layout.addWidget(self.notes_edit)
        self.tags_edit = QLineEdit(", ".join(card.metadata.get("tags", [])))
        layout.addWidget(QLabel("Tags (comma separated):"))
        layout.addWidget(self.tags_edit)
        layout.addWidget(QLabel("Quick Navigation Link (Scene/Chapter):"))
        self.quick_nav_list = QListWidget()
        self.quick_nav_list.setSelectionMode(QListWidget.SingleSelection)
        self._quick_nav_id_map = {}
        links = available_links or []
        for link in links:
            if link["type"] == "chapter":
                display = f"[Chapter] {link['title']}"
            else:
                display = f"[Scene] {link['title']} (in {link['chapter']})"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, link["id"])
            self.quick_nav_list.addItem(item)
            self._quick_nav_id_map[link["id"]] = item
        layout.addWidget(self.quick_nav_list)
        layout.addWidget(QLabel("Other Linked Scenes/Chapters (for reference):"))
        self.links_list = QListWidget()
        self.links_list.setSelectionMode(QListWidget.MultiSelection)
        self._link_id_map = {}
        for link in links:
            if link["type"] == "chapter":
                display = f"[Chapter] {link['title']}"
            else:
                display = f"[Scene] {link['title']} (in {link['chapter']})"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, link["id"])
            self.links_list.addItem(item)
            self._link_id_map[link["id"]] = item
        layout.addWidget(self.links_list)
        links_meta = card.metadata.get("links")
        quick_nav_id = None
        if isinstance(links_meta, list) and links_meta:
            quick_nav_id = links_meta[0]
        if quick_nav_id:
            if quick_nav_id in self._quick_nav_id_map:
                self._quick_nav_id_map[quick_nav_id].setSelected(True)
        if isinstance(links_meta, list):
            for link_id in links_meta:
                if link_id in self._link_id_map:
                    self._link_id_map[link_id].setSelected(True)
        color_btn = QPushButton("Set Color")
        color_btn.clicked.connect(self.choose_color)
        layout.addWidget(color_btn)
        self.selected_color = card.metadata.get("color")
        btns = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()

    def get_details(self):
        quick_nav_items = self.quick_nav_list.selectedItems()
        quick_nav_id = quick_nav_items[0].data(Qt.UserRole) if quick_nav_items else None
        additional_links = [
            item.data(Qt.UserRole) for item in self.links_list.selectedItems()
        ]
        links = []
        if quick_nav_id:
            links.append(quick_nav_id)
        for link_id in additional_links:
            if link_id and link_id not in links:
                links.append(link_id)
        return {
            "title": self.text_edit.text(),
            "notes": self.notes_edit.toPlainText(),
            "tags": [t.strip() for t in self.tags_edit.text().split(",") if t.strip()],
            "links": links,
            "color": self.selected_color,
        }


@dataclass
class Column:
    name: str
    layout: QVBoxLayout
    list_widget: QListWidget
    add_btn: QPushButton
