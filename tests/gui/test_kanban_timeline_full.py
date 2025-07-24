"""
test_kanban_timeline_full.py – Full coverage: unit, edge, integration, and UI trigger (headless)
"""

import pytest
from PySide6.QtWidgets import QListWidget
from GUI.windows.kanban_models import (
    KanbanCard,
    kanban_card_to_timeline_card,
    Column,
    sync_kanban_cards_to_timeline_widget,
)


# --- Unit test: Convert a Kanban card and verify all fields are copied ---
def test_kanban_card_conversion_all_fields():
    meta = {
        "id": "id1",
        "title": "Test",
        "notes": "desc",
        "tags": ["t1", "t2"],
        "color": "#abc",
        "links": ["l1"],
    }
    card = KanbanCard("Test", metadata=meta)
    result = kanban_card_to_timeline_card(card)
    assert result["id"] == "id1"
    assert result["title"] == "Test"
    assert result["description"] == "desc"
    assert result["tags"] == ["t1", "t2"]
    assert result["color"] == "#abc"
    assert result["links"] == ["l1"]


# --- Edge test: Convert a card with missing/extra fields ---
def test_kanban_card_conversion_missing_extra_fields():
    meta = {"id": "id2", "title": "Edge"}  # missing notes, tags, color, links
    card = KanbanCard("Edge", metadata=meta)
    result = kanban_card_to_timeline_card(card)
    assert result["description"] == ""
    assert result["tags"] == []
    assert result["color"] is None
    assert result["links"] == []
    # Extra field
    meta2 = {"id": "id3", "title": "X", "notes": "n", "foo": 123}
    card2 = KanbanCard("X", metadata=meta2)
    result2 = kanban_card_to_timeline_card(card2)
    assert result2["id"] == "id3"
    assert result2["description"] == "n"
    assert "foo" not in result2


# --- Integration test: Sync, edit, and delete cards; verify both views update as expected ---
class DummyTimelineCard:
    def __init__(self, meta):
        self.metadata = meta.copy()
        self.title = meta.get("title", "Untitled")
        self.label = type("lbl", (), {"setText": lambda self, t: None})()
        self._parent = None

    def setParent(self, p):
        self._parent = p


class DummyTimelineWidget:
    def __init__(self):
        self.cards = []
        self.layout = type("layout", (), {"removeWidget": lambda self, w: None})()

    def add_card(self, meta):
        card = DummyTimelineCard(meta)
        self.cards.append(card)


def test_integration_sync_edit_delete():
    k1 = KanbanCard("A", metadata={"id": "id1", "title": "A"})
    k2 = KanbanCard("B", metadata={"id": "id2", "title": "B"})
    tw = DummyTimelineWidget()
    # Sync both
    sync_kanban_cards_to_timeline_widget([k1, k2], tw)
    assert len(tw.cards) == 2
    # Edit k1
    k1_renamed = KanbanCard("A2", metadata={"id": "id1", "title": "A2"})
    sync_kanban_cards_to_timeline_widget([k1_renamed, k2], tw)
    assert any(c.metadata["title"] == "A2" for c in tw.cards)
    # Delete k2
    sync_kanban_cards_to_timeline_widget([k1_renamed], tw)
    assert len(tw.cards) == 1
    assert tw.cards[0].metadata["id"] == "id1"


# --- UI test: User can trigger conversion from the UI and see the result in the timeline ---
def test_ui_trigger_conversion(qtbot):
    # Simulate Kanban column and Timeline widget
    lw = QListWidget()
    card = KanbanCard("UI", metadata={"id": "idUI", "title": "UI", "notes": "desc"})
    lw.addItem(card)
    col = Column(name="Col", layout=None, list_widget=lw, add_btn=None)

    class DummyTimelineCard:
        def __init__(self, meta):
            self.metadata = meta.copy()
            self.title = meta.get("title", "Untitled")
            self.label = type("lbl", (), {"setText": lambda self, t: None})()
            self._parent = None

        def setParent(self, p):
            self._parent = p

    class DummyTimelineWidget:
        def __init__(self):
            self.cards = []
            self.layout = type("layout", (), {"removeWidget": lambda self, w: None})()

        def add_card(self, meta):
            card = DummyTimelineCard(meta)
            self.cards.append(card)

    tw = DummyTimelineWidget()
    # User selects card and triggers sync
    card.setSelected(True)
    selected = [item for item in col.get_selected_cards()]
    sync_kanban_cards_to_timeline_widget(selected, tw)
    assert any(c.metadata["id"] == "idUI" for c in tw.cards)
    assert any(c.metadata["title"] == "UI" for c in tw.cards)
