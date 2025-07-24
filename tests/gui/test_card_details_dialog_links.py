import pytest
from PySide6.QtWidgets import QApplication
from GUI.windows.kanban_board import CardDetailsDialog, KanbanCard
from PySide6.QtCore import Qt


def make_links():
    return [
        {"id": "chapter:0", "type": "chapter", "title": "Chapter 1"},
        {
            "id": "chapter:0:scene:0",
            "type": "scene",
            "title": "Scene 1",
            "chapter": "Chapter 1",
        },
        {
            "id": "chapter:0:scene:1",
            "type": "scene",
            "title": "Scene 2",
            "chapter": "Chapter 1",
        },
        {"id": "chapter:1", "type": "chapter", "title": "Chapter 2"},
    ]


def test_card_details_dialog_links_normal(qtbot):
    card = KanbanCard("Test Card", metadata={"links": ["chapter:0:scene:1"]})
    links = make_links()
    dlg = CardDetailsDialog(card, None, available_links=links)
    qtbot.addWidget(dlg)
    # Check that the correct item is pre-selected
    selected = [item.data(Qt.UserRole) for item in dlg.links_list.selectedItems()]
    assert "chapter:0:scene:1" in selected
    # Simulate user selecting another link
    for i in range(dlg.links_list.count()):
        item = dlg.links_list.item(i)
        if item.data(Qt.UserRole) == "chapter:1":
            item.setSelected(True)
    details = dlg.get_details()
    assert "chapter:1" in details["links"]
    assert "chapter:0:scene:1" in details["links"]


def test_card_details_dialog_links_empty(qtbot):
    card = KanbanCard("Test Card", metadata={"links": []})
    links = make_links()
    dlg = CardDetailsDialog(card, None, available_links=links)
    qtbot.addWidget(dlg)
    # No links selected
    assert dlg.get_details()["links"] == []


def test_card_details_dialog_links_invalid(qtbot):
    card = KanbanCard("Test Card", metadata={"links": ["nonexistent"]})
    links = make_links()
    dlg = CardDetailsDialog(card, None, available_links=links)
    qtbot.addWidget(dlg)
    # Should not select any invalid link
    selected = [item.data(Qt.UserRole) for item in dlg.links_list.selectedItems()]
    assert "nonexistent" not in selected
