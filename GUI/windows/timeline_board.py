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


class TimelineCard(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumWidth(120)
        self.setMaximumWidth(200)
        self.setStyleSheet("background: #f3f4f6; border-radius: 8px; padding: 8px;")
        layout = QVBoxLayout(self)
        self.label = QLabel(title)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setAcceptDrops(True)
        self.title = title

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.title)
            drag.setMimeData(mime)
            drag.exec(Qt.MoveAction)


class TimelineBoardWidget(QWidget):
    orderChanged = Signal(list)  # Emits list of card titles in new order

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.cards = []
        self.setAcceptDrops(True)

    def add_card(self, title):
        card = TimelineCard(title)
        self.cards.append(card)
        self.layout.addWidget(card)
        card.show()

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
