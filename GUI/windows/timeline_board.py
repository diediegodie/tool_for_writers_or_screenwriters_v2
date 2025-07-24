from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QApplication,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt, Signal, QMimeData, QByteArray
from PySide6.QtGui import QDrag


import uuid


class TimelineCard(QFrame):
    """
    TimelineCard represents a card in the timeline/storyboard.

    metadata fields (shared with KanbanCard):
        id (str): Unique card ID (uuid4 hex)
        title (str): Card title
        notes (str): Freeform notes for the card.
        tags (List[str]): List of tags for filtering/searching.
        color (Optional[str]): Hex color string for card background.
        links (List[str]): List of scene/chapter IDs this card is linked to for quick navigation.
    """

    def __init__(self, title_or_metadata, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumWidth(120)
        self.setMaximumWidth(200)
        self.setStyleSheet("background: #f3f4f6; border-radius: 8px; padding: 8px;")
        layout = QVBoxLayout(self)
        # Accept either a title (str) or a metadata dict
        if isinstance(title_or_metadata, dict):
            self.metadata = title_or_metadata.copy()
            self.title = self.metadata.get("title", "Untitled")
        else:
            self.title = str(title_or_metadata)
            self.metadata = {
                "id": str(uuid.uuid4()),
                "title": self.title,
                "notes": "",
                "tags": [],
                "color": None,
                "links": [],
            }
        self.label = QLabel(self.title)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setAcceptDrops(True)
        # Set color if present
        if self.metadata.get("color"):
            self.setStyleSheet(
                f"background: {self.metadata['color']}; border-radius: 8px; padding: 8px;"
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.title)
            drag.setMimeData(mime)
            drag.exec(Qt.MoveAction)


class TimelineBoardWidget(QWidget):
    def save_state(self):
        """
        Returns a list of dicts representing the current timeline board state (for storage).
        """
        return [getattr(card, "metadata", {}) for card in self.cards]

    def load_state(self, state):
        """
        Loads the timeline board state from a list of dicts.
        """
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        self.cards.clear()
        for meta in state:
            self.add_card(meta)

    def save_to_storage(self):
        """
        Save the current timeline board to persistent storage (JSON).
        """
        from GUI.storage import timeline_store

        timeline_store.save_timeline_board(self.save_state())

    def load_from_storage(self):
        """
        Load the timeline board from persistent storage (JSON).
        """
        from GUI.storage import timeline_store

        state = timeline_store.load_timeline_board()
        if state:
            self.load_state(state)

    orderChanged = Signal(list)  # Emits list of card titles in new order

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.cards = []
        self.setAcceptDrops(True)

    def add_card(self, title_or_metadata):
        card = TimelineCard(title_or_metadata)
        print(
            f"[DEBUG] TimelineBoardWidget.add_card: Adding card with id={card.metadata.get('id')}, title={card.title}"
        )
        self.cards.append(card)
        self.layout.addWidget(card)
        card.setParent(self)  # Ensure widget hierarchy
        card.show()
        self.layout.update()

    def remove_card(self, title):
        for card in self.cards:
            if card.title == title:
                self.layout.removeWidget(card)
                card.setParent(None)
                self.cards.remove(card)
                break
        self.orderChanged.emit([c.title for c in self.cards])

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        title = event.mimeData().text()
        from_idx = next((i for i, c in enumerate(self.cards) if c.title == title), None)
        if from_idx is not None:
            pos = event.position().toPoint().x()
            to_idx = 0
            for i, card in enumerate(self.cards):
                if pos < card.x() + card.width() // 2:
                    to_idx = i
                    break
                to_idx = i + 1
            if to_idx != from_idx:
                card = self.cards.pop(from_idx)
                self.cards.insert(to_idx, card)
                # Rebuild layout
                for i in reversed(range(self.layout.count())):
                    self.layout.itemAt(i).widget().setParent(None)
                for card in self.cards:
                    self.layout.addWidget(card)
                self.orderChanged.emit([c.title for c in self.cards])
        event.acceptProposedAction()
