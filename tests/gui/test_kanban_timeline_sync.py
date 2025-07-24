"""
test_kanban_timeline_sync.py – Tests for sync_kanban_cards_to_timeline_widget and sync_timeline_cards_to_kanban_columns
Covers: normal, update, add, and edge/failure cases
"""

import pytest
from PySide6.QtWidgets import QListWidget
from GUI.windows.kanban_models import (
    KanbanCard,
    Column,
    sync_kanban_cards_to_timeline_widget,
    sync_timeline_cards_to_kanban_columns,
)


class DummyTimelineCard:
    def __init__(self, meta):
        self.metadata = meta.copy()
        self.title = meta.get("title", "Untitled")
        self.label = type("lbl", (), {"setText": lambda self, t: None})()
    def setParent(self, parent):
        pass  # Dummy method for test compatibility


class DummyTimelineWidget:
    def __init__(self):
        self.cards = []
        self.added = []

    def add_card(self, meta):
        card = DummyTimelineCard(meta)
        self.cards.append(card)
        self.added.append(card)


# --- Kanban to Timeline ---
def test_sync_kanban_cards_to_timeline_widget_add_and_update():
    # Add new
    k1 = KanbanCard("A", metadata={"id": "id1", "title": "A", "notes": "n1"})
    k2 = KanbanCard("B", metadata={"id": "id2", "title": "B", "notes": "n2"})
    tw = DummyTimelineWidget()
    sync_kanban_cards_to_timeline_widget([k1, k2], tw)
    assert len(tw.cards) == 2
    assert tw.cards[0].metadata["title"] == "A"
    # Update existing
    k1b = KanbanCard("A2", metadata={"id": "id1", "title": "A2", "notes": "n1b"})
    sync_kanban_cards_to_timeline_widget([k1b], tw)
    assert tw.cards[0].metadata["title"] == "A2"
    assert tw.cards[0].metadata["notes"] == "n1b"


def test_sync_kanban_cards_to_timeline_widget_empty():
    tw = DummyTimelineWidget()
    sync_kanban_cards_to_timeline_widget([], tw)
    assert tw.cards == []


# --- Timeline to Kanban ---
def make_column_with_cards(card_metas):
    lw = QListWidget()
    cards = [KanbanCard(m["title"], metadata=m) for m in card_metas]
    for c in cards:
        lw.addItem(c)
    return Column(name="Col", layout=None, list_widget=lw, add_btn=None), cards


def test_sync_timeline_cards_to_kanban_columns_add_and_update(qtbot):
    cmeta1 = {"id": "id1", "title": "A", "notes": "n1"}
    cmeta2 = {"id": "id2", "title": "B", "notes": "n2"}
    col, cards = make_column_with_cards([cmeta1])
    tcard2 = DummyTimelineCard(cmeta2)
    # Add new timeline card to Kanban
    sync_timeline_cards_to_kanban_columns([tcard2], [col])
    found = False
    for i in range(col.list_widget.count()):
        if col.list_widget.item(i).metadata["id"] == "id2":
            found = True
    assert found
    # Update existing
    tcard1b = DummyTimelineCard({"id": "id1", "title": "A2", "notes": "n1b"})
    sync_timeline_cards_to_kanban_columns([tcard1b], [col])
    for i in range(col.list_widget.count()):
        if col.list_widget.item(i).metadata["id"] == "id1":
            assert col.list_widget.item(i).metadata["title"] == "A2"
            assert col.list_widget.item(i).metadata["notes"] == "n1b"


def test_sync_timeline_cards_to_kanban_columns_empty(qtbot):
    col, cards = make_column_with_cards([])
    sync_timeline_cards_to_kanban_columns([], [col])
    assert col.list_widget.count() == 0
