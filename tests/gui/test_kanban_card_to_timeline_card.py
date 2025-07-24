"""
test_kanban_card_to_timeline_card.py – Tests for kanban_card_to_timeline_card conversion function
Covers: normal, edge, and failure cases; integration with multi-selection helpers
"""

import pytest
from GUI.windows.kanban_models import (
    KanbanCard,
    kanban_card_to_timeline_card,
    enable_multi_selection_for_all_columns,
    get_all_selected_kanban_cards,
    Column,
)
from PySide6.QtWidgets import QListWidget


def make_card(title, notes=None, tags=None, color=None, links=None, id_=None):
    meta = {
        "id": id_ or "testid-123",
        "title": title,
        "notes": notes or "",
        "tags": tags or [],
        "color": color,
        "links": links or [],
    }
    return KanbanCard(title, metadata=meta)


def test_kanban_card_to_timeline_card_normal():
    card = make_card(
        "Test Title", notes="Desc", tags=["a"], color="#fff", links=["l1"], id_="id42"
    )
    result = kanban_card_to_timeline_card(card)
    assert result["id"] == "id42"
    assert result["title"] == "Test Title"
    assert result["description"] == "Desc"
    assert result["tags"] == ["a"]
    assert result["color"] == "#fff"
    assert result["links"] == ["l1"]


def test_kanban_card_to_timeline_card_edge_empty_fields():
    card = make_card("Edge")
    result = kanban_card_to_timeline_card(card)
    assert result["title"] == "Edge"
    assert result["description"] == ""
    assert result["tags"] == []
    assert result["color"] is None
    assert result["links"] == []


def test_kanban_card_to_timeline_card_failure():
    class Dummy:
        pass

    with pytest.raises(ValueError):
        kanban_card_to_timeline_card(Dummy())


def test_integration_with_multi_selection_helpers(qtbot):
    lw = QListWidget()
    card1 = make_card("A", notes="n1", tags=["t1"], color="#111", links=["x"])
    card2 = make_card("B", notes="n2", tags=["t2"], color="#222", links=["y"])
    lw.addItem(card1)
    lw.addItem(card2)
    col = Column(name="Col", layout=None, list_widget=lw, add_btn=None)
    enable_multi_selection_for_all_columns([col])
    card1.setSelected(True)
    card2.setSelected(False)
    selected = get_all_selected_kanban_cards([col])
    assert selected == [card1]
    timeline_data = [kanban_card_to_timeline_card(c) for c in selected]
    assert timeline_data[0]["title"] == "A"
    assert timeline_data[0]["description"] == "n1"
    assert timeline_data[0]["tags"] == ["t1"]
    assert timeline_data[0]["color"] == "#111"
    assert timeline_data[0]["links"] == ["x"]
