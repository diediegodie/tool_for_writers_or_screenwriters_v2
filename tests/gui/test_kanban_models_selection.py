"""
test_kanban_models_selection.py – Tests for Kanban multi-selection helpers
Covers: set_selection_mode, get_selected_cards, enable_multi_selection_for_all_columns, get_all_selected_kanban_cards
"""

import pytest
from PySide6.QtWidgets import QApplication, QListWidget
from GUI.windows.kanban_models import (
    KanbanCard,
    Column,
    enable_multi_selection_for_all_columns,
    get_all_selected_kanban_cards,
)


def make_column(name, card_titles):
    lw = QListWidget()
    cards = [KanbanCard(title) for title in card_titles]
    for c in cards:
        lw.addItem(c)
    # Default: single selection, test will change
    col = Column(name=name, layout=None, list_widget=lw, add_btn=None)
    return col, cards


def test_set_selection_mode_and_get_selected_cards(qtbot):
    col, cards = make_column("TestCol", ["A", "B", "C"])
    col.set_selection_mode()  # Should set to MultiSelection
    cards[0].setSelected(True)
    cards[2].setSelected(True)
    selected = col.get_selected_cards()
    assert cards[0] in selected and cards[2] in selected and len(selected) == 2


def test_enable_multi_selection_for_all_columns(qtbot):
    col1, cards1 = make_column("Col1", ["A", "B"])
    col2, cards2 = make_column("Col2", ["X", "Y"])
    enable_multi_selection_for_all_columns([col1, col2])
    # Both should now be MultiSelection
    from PySide6.QtWidgets import QAbstractItemView

    assert col1.list_widget.selectionMode() == QAbstractItemView.MultiSelection
    assert col2.list_widget.selectionMode() == QAbstractItemView.MultiSelection


def test_get_all_selected_kanban_cards(qtbot):
    col1, cards1 = make_column("Col1", ["A", "B"])
    col2, cards2 = make_column("Col2", ["X", "Y"])
    enable_multi_selection_for_all_columns([col1, col2])
    cards1[1].setSelected(True)
    cards2[0].setSelected(True)
    selected = get_all_selected_kanban_cards([col1, col2])
    assert cards1[1] in selected and cards2[0] in selected and len(selected) == 2


def test_get_selected_cards_empty(qtbot):
    col, cards = make_column("TestCol", ["A", "B"])
    col.set_selection_mode()
    assert col.get_selected_cards() == []


def test_get_all_selected_kanban_cards_empty(qtbot):
    col1, cards1 = make_column("Col1", ["A"])
    col2, cards2 = make_column("Col2", ["B"])
    enable_multi_selection_for_all_columns([col1, col2])
    assert get_all_selected_kanban_cards([col1, col2]) == []
