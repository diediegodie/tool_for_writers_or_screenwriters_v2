import pytest
from GUI.windows.kanban_board import KanbanBoardWidget, KanbanCard
from GUI.storage import kanban_store
import os
import shutil
import tempfile


def test_kanban_autosave_and_version(tmp_path, qtbot):
    # Patch kanban_store to use a temp dir BEFORE creating the widget
    orig_file = kanban_store.KANBAN_FILE
    orig_hist = kanban_store.KANBAN_HISTORY_DIR
    kanban_store.KANBAN_FILE = str(tmp_path / "kanban_board.json")
    kanban_store.KANBAN_HISTORY_DIR = str(tmp_path / "kanban_history")

    try:
        widget = KanbanBoardWidget()
        qtbot.addWidget(widget)

        # Wait for widget to be fully constructed and exposed
        qtbot.waitExposed(widget)
        qtbot.wait(50)  # Additional time for Qt event loop processing

        # Ensure all attributes are properly initialized
        assert hasattr(
            widget, "_autosave_timer"
        ), "Widget should have _autosave_timer attribute"
        assert hasattr(widget, "_loading"), "Widget should have _loading attribute"

        # Add a card and trigger autosave
        col = widget.column_map["To Do"]
        card = KanbanCard("Autosave Test")
        col.list_widget.addItem(card)

        # Trigger autosave and wait for debounce
        widget.trigger_autosave()
        qtbot.wait(1200)  # Wait for debounce + some extra time

        # Check file exists
        assert os.path.exists(
            kanban_store.KANBAN_FILE
        ), "Kanban board file should be created"
        data = kanban_store.load_kanban_board()
        found = any(card.get("title") == "Autosave Test" for card in data["To Do"])
        assert found, "Autosave Test card should be found in saved data"

        # Check version history file created
        versions = kanban_store.list_kanban_versions()
        assert versions, "Version history should exist after autosave"

    finally:
        kanban_store.KANBAN_FILE = orig_file
        kanban_store.KANBAN_HISTORY_DIR = orig_hist
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_kanban_undo_redo(qtbot):
    widget = KanbanBoardWidget()
    qtbot.addWidget(widget)

    # Wait for widget to be fully constructed
    qtbot.waitExposed(widget)
    qtbot.wait(50)  # Additional time for Qt event loop processing

    # Ensure all attributes are properly initialized
    assert hasattr(widget, "_undo_stack"), "Widget should have _undo_stack attribute"
    assert hasattr(widget, "_redo_stack"), "Widget should have _redo_stack attribute"

    col = widget.column_map["To Do"]

    # Push initial state (empty column) to undo stack
    widget.push_undo()

    # Add first card
    card1 = KanbanCard("Undo 1")
    col.list_widget.addItem(card1)

    # Push state before adding second card (column with card1)
    widget.push_undo()

    # Add second card
    card2 = KanbanCard("Undo 2")
    col.list_widget.addItem(card2)

    # Verify both cards are present
    titles = [col.list_widget.item(i).text() for i in range(col.list_widget.count())]
    assert (
        "Undo 1" in titles and "Undo 2" in titles
    ), "Both cards should be present initially"

    # Undo should remove card2 (go back to state with only card1)
    widget.undo()
    titles = [col.list_widget.item(i).text() for i in range(col.list_widget.count())]
    assert "Undo 2" not in titles, "Card2 should be removed after undo"
    assert "Undo 1" in titles, "Card1 should still be present after undo"

    # Redo should bring card2 back
    widget.redo()
    titles = [col.list_widget.item(i).text() for i in range(col.list_widget.count())]
    assert "Undo 2" in titles, "Card2 should be restored after redo"
    assert "Undo 1" in titles, "Card1 should still be present after redo"
