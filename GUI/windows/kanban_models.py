# --- Timeline to Kanban Integration Utility ---
def sync_timeline_cards_to_kanban_columns(timeline_cards, kanban_columns):
    """
    Sync a list of timeline card objects (with .metadata or dict) to Kanban columns.
    Updates existing Kanban cards by id, or adds new ones to the first column if not present.

    Args:
        timeline_cards: List of TimelineCard objects or dicts (must have 'id').
        kanban_columns: List of Column objects (each with a QListWidget of KanbanCards).

    This function ensures that for every timeline card, there is a corresponding Kanban card.
    If a timeline card's id matches a Kanban card, the Kanban card is updated.
    If not, a new Kanban card is added to the first column.
    """
    # Build id->(col, card) mapping for Kanban
    kanban_cards_by_id = {}
    for col in kanban_columns:
        for i in range(col.list_widget.count()):
            item = col.list_widget.item(i)
            meta = getattr(item, "metadata", None)
            if meta and meta.get("id"):
                kanban_cards_by_id[meta["id"]] = (col, item)
    for tcard in timeline_cards:
        meta = getattr(tcard, "metadata", tcard)  # Accept TimelineCard or dict
        tid = meta.get("id")
        if tid in kanban_cards_by_id:
            col, kcard = kanban_cards_by_id[tid]
            kcard.metadata.update(meta)
            kcard.setText(meta.get("title", kcard.text()))
            # Optionally update color, tags, etc.
        else:
            # Add to first column by default
            if kanban_columns:
                from .kanban_models import KanbanCard

                new_card = KanbanCard(meta.get("title", "Untitled"), metadata=meta)
                kanban_columns[0].list_widget.addItem(new_card)


# --- Timeline/Storyboard Integration Utilities ---
def sync_kanban_cards_to_timeline_widget(kanban_cards, timeline_widget):
    """
    Sync a list of KanbanCard objects to a TimelineBoardWidget.
    Updates existing timeline cards by id, or adds new ones if not present.

    Args:
        kanban_cards: List of KanbanCard objects.
        timeline_widget: TimelineBoardWidget (or compatible) instance.

    This function ensures that for every Kanban card, there is a corresponding timeline card.
    - If a Kanban card's id matches a timeline card, the timeline card is updated.
    - If not, a new timeline card is added.
    - Prevents duplicate timeline cards for the same Kanban card.
    - Removes timeline cards whose id is not present in Kanban (handles delete/rename).
    """
    # Build id->card mapping for timeline
    timeline_cards_by_id = {
        getattr(c, "metadata", {}).get("id"): c
        for c in getattr(timeline_widget, "cards", [])
    }
    seen_ids = set()
    for kcard in kanban_cards:
        tdata = kanban_card_to_timeline_card(kcard)
        tid = tdata["id"]
        if tid in seen_ids:
            continue  # Prevent duplicate timeline cards for same Kanban card
        seen_ids.add(tid)
        if tid in timeline_cards_by_id:
            tcard = timeline_cards_by_id[tid]
            # Map 'description' to 'notes' for timeline card compatibility
            tdata_for_update = tdata.copy()
            if "description" in tdata_for_update:
                tdata_for_update["notes"] = tdata_for_update.pop("description")
            tcard.metadata.update(tdata_for_update)
            tcard.title = tdata_for_update["title"]
            if hasattr(tcard, "label"):
                tcard.label.setText(tdata_for_update["title"])
            # Optionally update color, tags, etc.
        else:
            timeline_widget.add_card(tdata)

    # Handle deleted/renamed Kanban cards: remove timeline cards whose id is not in Kanban
    kanban_ids = {kanban_card_to_timeline_card(k)["id"] for k in kanban_cards}
    to_remove = [
        c
        for c in getattr(timeline_widget, "cards", [])
        if getattr(c, "metadata", {}).get("id") not in kanban_ids
    ]
    for c in to_remove:
        if hasattr(timeline_widget, "layout"):
            timeline_widget.layout.removeWidget(c)
        c.setParent(None)
        timeline_widget.cards.remove(c)


# --- Kanban to Timeline/Storyboard Conversion ---
def kanban_card_to_timeline_card(kanban_card):
    """
    Convert a KanbanCard to a timeline/storyboard card dict.
    Copies all relevant fields: id, title, notes (as description), tags, color, links.

    Args:
        kanban_card: KanbanCard instance.
    Returns:
        dict: Timeline card data with keys: id, title, description, tags, color, links.
    Raises:
        ValueError: If input is not a KanbanCard or missing metadata.
    """
    meta = getattr(kanban_card, "metadata", None)
    if not meta:
        raise ValueError("Input is not a KanbanCard or missing metadata")
    # Map 'notes' to 'description' for timeline compatibility
    return {
        "id": meta.get("id"),
        "title": meta.get("title"),
        "description": meta.get("notes"),
        "tags": list(meta.get("tags", [])),
        "color": meta.get("color"),
        "links": list(meta.get("links", [])),
    }


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
from typing import List, Dict, Any, Optional, Callable


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

    def set_selection_mode(self, mode=None):
        """
        Set the selection mode for the column's QListWidget.
        Default is MultiSelection for multi-card selection.
        """
        from PySide6.QtWidgets import QAbstractItemView

        if mode is None:
            mode = QAbstractItemView.MultiSelection
        self.list_widget.setSelectionMode(mode)

    def get_selected_cards(self) -> List[KanbanCard]:
        """
        Return all selected KanbanCard items in this column.
        """
        return [
            item
            for item in self.list_widget.selectedItems()
            if isinstance(item, KanbanCard)
        ]


# --- Kanban Board Multi-Selection Utilities ---
def enable_multi_selection_for_all_columns(columns: List[Column]):
    """
    Enable multi-selection mode for all columns' QListWidget.
    """
    for col in columns:
        col.set_selection_mode()


def get_all_selected_kanban_cards(columns: List[Column]) -> List[KanbanCard]:
    """
    Return all selected KanbanCard items across all columns.
    """
    selected = []
    for col in columns:
        selected.extend(col.get_selected_cards())
    return selected
