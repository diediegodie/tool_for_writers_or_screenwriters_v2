"""
test_kanban_timeline_sync_edge.py – Edge case tests for Kanban <-> Timeline sync
Covers: duplicate prevention, deletion/rename handling
"""

import pytest
from PySide6.QtWidgets import QListWidget
from GUI.windows.kanban_models import (
    KanbanCard,
    Column,
    sync_kanban_cards_to_timeline_widget,
)


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


# --- Duplicate Prevention ---
def test_no_duplicate_timeline_cards():
    k1 = KanbanCard("A", metadata={"id": "id1", "title": "A"})
    k2 = KanbanCard("A", metadata={"id": "id1", "title": "A"})  # Same id
    tw = DummyTimelineWidget()
    sync_kanban_cards_to_timeline_widget([k1, k2], tw)
    assert len(tw.cards) == 1
    # Add a new card with a different id
    k3 = KanbanCard("B", metadata={"id": "id2", "title": "B"})
    sync_kanban_cards_to_timeline_widget([k1, k3], tw)
    assert len(tw.cards) == 2


# --- Deletion/Rename Handling ---
def test_deleted_kanban_card_removes_timeline_card():
    k1 = KanbanCard("A", metadata={"id": "id1", "title": "A"})
    k2 = KanbanCard("B", metadata={"id": "id2", "title": "B"})
    tw = DummyTimelineWidget()
    sync_kanban_cards_to_timeline_widget([k1, k2], tw)
    assert len(tw.cards) == 2
    # Remove k2 from Kanban, sync again
    sync_kanban_cards_to_timeline_widget([k1], tw)
    assert len(tw.cards) == 1
    assert tw.cards[0].metadata["id"] == "id1"


def test_renamed_kanban_card_updates_timeline_card():
    k1 = KanbanCard("A", metadata={"id": "id1", "title": "A"})
    tw = DummyTimelineWidget()
    sync_kanban_cards_to_timeline_widget([k1], tw)
    assert tw.cards[0].metadata["title"] == "A"
    # Rename in Kanban
    k1_renamed = KanbanCard("A2", metadata={"id": "id1", "title": "A2"})
    sync_kanban_cards_to_timeline_widget([k1_renamed], tw)
    assert tw.cards[0].metadata["title"] == "A2"
