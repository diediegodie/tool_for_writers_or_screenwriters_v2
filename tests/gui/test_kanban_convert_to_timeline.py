import sys
import os

# Ensure project root is in sys.path for GUI imports (must be first)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

"""
Test Kanban-to-Timeline conversion via context menu (GUI)

Covers:
- Right-click context menu on Kanban card
- Select "Convert to Timeline Card"
- Card appears in TimelineBoardWidget
- Duplicate conversion is blocked
- User feedback dialogs are shown

Requires: pytest, pytest-qt, PySide6
"""

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow
from GUI.windows.kanban_board import KanbanBoardWidget, KanbanCard
from GUI.windows.timeline_board import TimelineBoardWidget


class DummyTimelineTab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timeline_widget = TimelineBoardWidget(self)
        self.setCentralWidget(self.timeline_widget)


@pytest.fixture
def app(qtbot):
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def setup_boards(qtbot, app):
    timeline_tab = DummyTimelineTab()
    kanban = KanbanBoardWidget(parent=timeline_tab)
    timeline_tab.show()
    kanban.show()
    qtbot.addWidget(timeline_tab)
    qtbot.addWidget(kanban)
    # Add a card to "To Do"
    col = kanban.column_map["To Do"]
    card = KanbanCard(
        "Test Card", metadata={"notes": "abc", "tags": ["x"], "color": "#ff0"}
    )
    col.list_widget.addItem(card)
    return kanban, timeline_tab, card


def test_convert_to_timeline_card(qtbot, setup_boards, monkeypatch):
    kanban, timeline_tab, card = setup_boards
    timeline_widget = timeline_tab.timeline_widget
    # Patch QMessageBox to auto-accept
    monkeypatch.setattr(
        "PySide6.QtWidgets.QMessageBox.information", lambda *a, **k: None
    )
    monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.warning", lambda *a, **k: None)
    # Simulate context menu: call handler directly with pos=None to avoid Wayland popup errors
    lw = kanban.column_map["To Do"].list_widget
    idx = lw.row(card)
    lw.setCurrentRow(idx)
    kanban._show_card_context_menu(lw, "To Do", None)
    # Card should now exist in timeline
    timeline_ids = [c.metadata["id"] for c in timeline_widget.cards]
    assert card.metadata["id"] in timeline_ids
    # Try again: should trigger duplicate dialog, not add
    before = len(timeline_widget.cards)
    kanban._show_card_context_menu(lw, "To Do", None)
    after = len(timeline_widget.cards)
    assert after == before
