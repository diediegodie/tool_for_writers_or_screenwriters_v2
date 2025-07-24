import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication
from GUI.windows.kanban_board import KanbanCard
from GUI.windows.timeline_board import TimelineCard


# Ensure a QApplication exists for all tests in this module
@pytest.fixture(autouse=True, scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_kanban_to_timeline_metadata_copy():
    meta = {
        "id": "abc123",
        "title": "Test Card",
        "notes": "Some notes",
        "tags": ["tag1", "tag2"],
        "color": "#ffcc00",
        "links": ["scene1", "scene2"],
    }
    kcard = KanbanCard("Test Card", metadata=meta)
    # Simulate conversion: pass metadata to TimelineCard
    tcard = TimelineCard(kcard.metadata)
    assert tcard.metadata["id"] == kcard.metadata["id"]
    assert tcard.metadata["title"] == kcard.metadata["title"]
    assert tcard.metadata["notes"] == kcard.metadata["notes"]
    assert tcard.metadata["tags"] == kcard.metadata["tags"]
    assert tcard.metadata["color"] == kcard.metadata["color"]
    assert tcard.metadata["links"] == kcard.metadata["links"]
    assert tcard.title == kcard.metadata["title"]


def test_timeline_to_kanban_metadata_copy():
    meta = {
        "id": "def456",
        "title": "Timeline Card",
        "notes": "Timeline notes",
        "tags": ["timeline"],
        "color": "#00ccff",
        "links": ["sceneX"],
    }
    tcard = TimelineCard(meta)
    kcard = KanbanCard(meta["title"], metadata=meta)
    assert kcard.metadata["id"] == tcard.metadata["id"]
    assert kcard.metadata["title"] == tcard.metadata["title"]
    assert kcard.metadata["notes"] == tcard.metadata["notes"]
    assert kcard.metadata["tags"] == tcard.metadata["tags"]
    assert kcard.metadata["color"] == tcard.metadata["color"]
    assert kcard.metadata["links"] == tcard.metadata["links"]
    assert kcard.text() == tcard.metadata["title"]


def test_kanbancard_defaults():
    kcard = KanbanCard("Untitled")
    assert isinstance(kcard.metadata["id"], str)
    assert kcard.metadata["title"] == "Untitled"
    assert kcard.metadata["notes"] == ""
    assert kcard.metadata["tags"] == []
    assert kcard.metadata["color"] is None
    assert kcard.metadata["links"] == []


def test_timelinecard_defaults():
    tcard = TimelineCard("Untitled")
    assert isinstance(tcard.metadata["id"], str)
    assert tcard.metadata["title"] == "Untitled"
    assert tcard.metadata["notes"] == ""
    assert tcard.metadata["tags"] == []
    assert tcard.metadata["color"] is None
    assert tcard.metadata["links"] == []


def test_color_roundtrip():
    kcard = KanbanCard("Color Card")
    kcard.set_color(QColor("#123456"))
    tcard = TimelineCard(kcard.metadata)
    assert tcard.metadata["color"] == "#123456"
    # TimelineCard color in stylesheet
    if tcard.metadata["color"]:
        assert tcard.styleSheet().find("#123456") != -1
