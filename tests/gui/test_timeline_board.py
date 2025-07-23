import sys
import pytest
from PySide6.QtWidgets import QApplication
from GUI.windows.timeline_board import TimelineBoardWidget


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


# Normal case: add, reorder, and remove cards
def test_timeline_add_and_reorder(app):
    widget = TimelineBoardWidget()
    widget.add_card("Scene 1")
    widget.add_card("Scene 2")
    widget.add_card("Scene 3")
    assert [c.title for c in widget.cards] == ["Scene 1", "Scene 2", "Scene 3"]
    # Simulate reorder: move Scene 3 to front
    widget.cards.insert(0, widget.cards.pop(2))
    for i in reversed(range(widget.layout.count())):
        widget.layout.itemAt(i).widget().setParent(None)
    for card in widget.cards:
        widget.layout.addWidget(card)
    assert [c.title for c in widget.cards] == ["Scene 3", "Scene 1", "Scene 2"]
    widget.remove_card("Scene 1")
    assert [c.title for c in widget.cards] == ["Scene 3", "Scene 2"]


# Edge case: remove non-existent card
def test_timeline_remove_nonexistent(app):
    widget = TimelineBoardWidget()
    widget.add_card("A")
    widget.remove_card("B")  # Should not raise
    assert [c.title for c in widget.cards] == ["A"]


# Failure case: add duplicate card titles
def test_timeline_duplicate_titles(app):
    widget = TimelineBoardWidget()
    widget.add_card("X")
    widget.add_card("X")  # Allow duplicate titles
    assert len(widget.cards) == 2
    widget.remove_card("X")
    # Only first instance removed
    assert len(widget.cards) == 1
    assert widget.cards[0].title == "X"
