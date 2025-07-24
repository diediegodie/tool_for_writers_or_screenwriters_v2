"""
Test user-resizable columns in KanbanBoardWidget using QSplitter.
Covers: normal, edge, and failure cases for resizing columns.
"""

import pytest
from PySide6.QtWidgets import QApplication
from GUI.windows.kanban_board import KanbanBoardWidget


@pytest.fixture(scope="module")
def app():
    import sys

    app = QApplication.instance() or QApplication(sys.argv)
    yield app


def test_splitter_resizable_columns_normal(app):
    widget = KanbanBoardWidget()
    splitter = widget.splitter
    assert splitter.count() >= 3  # Default columns
    # Try resizing columns
    sizes = splitter.sizes()
    new_sizes = [max(1, s + 50) for s in sizes]
    splitter.setSizes(new_sizes)
    # Qt may not set exact sizes, but at least one should change
    assert splitter.sizes() != sizes


def test_splitter_resizable_columns_edge(app):
    widget = KanbanBoardWidget()
    splitter = widget.splitter
    # Set one column to minimum width
    sizes = splitter.sizes()
    if sizes:
        new_sizes = sizes[:]
        new_sizes[0] = 1
        splitter.setSizes(new_sizes)
        # Qt may not set to exactly 1, but sizes should change
        assert splitter.sizes() != sizes


def test_splitter_resizable_columns_failure(app):
    widget = KanbanBoardWidget()
    splitter = widget.splitter
    # Try setting invalid sizes (negative)
    sizes = splitter.sizes()
    if sizes:
        bad_sizes = [-10 for _ in sizes]
        splitter.setSizes(bad_sizes)
        # Qt will clamp to minimum, not raise
        assert all(s >= 0 for s in splitter.sizes())
