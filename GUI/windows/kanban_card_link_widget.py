from PySide6.QtWidgets import QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


class KanbanCardLinkWidget(QPushButton):
    """
    A button widget to display and navigate to the primary linked scene/chapter for a Kanban card.
    """

    def __init__(self, link_title: str, link_id: str, on_navigate, parent=None):
        super().__init__(parent)
        self.link_id = link_id
        self.setText(link_title)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(f"Go to: {link_title}")
        self.clicked.connect(lambda: on_navigate(self.link_id))
        # Optionally set an icon for navigation
        # self.setIcon(QIcon.fromTheme("go-jump"))
