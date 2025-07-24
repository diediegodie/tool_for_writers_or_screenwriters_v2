"""
Test for KanbanBoardWidget integration in ProjectEditorWindow

Covers: normal, edge, and failure cases for widget instantiation and tab presence.
"""

import pytest
from PySide6.QtWidgets import QApplication
from GUI.windows.project_editor_window import ProjectEditorWindow


@pytest.fixture(scope="module")
def app():
    import sys

    app = QApplication.instance() or QApplication(sys.argv)
    yield app


def test_kanban_tab_present(app):
    window = ProjectEditorWindow()
    tab_widget = window.tab_widget
    tab_titles = [tab_widget.tabText(i) for i in range(tab_widget.count())]
    assert any("Kanban" in t for t in tab_titles), "Kanban Board tab should be present"


def test_kanban_widget_instantiation(app):
    window = ProjectEditorWindow()
    tab_widget = window.tab_widget
    idx = None
    for i in range(tab_widget.count()):
        if "Kanban" in tab_widget.tabText(i):
            idx = i
            break
    assert idx is not None, "Kanban Board tab index should be found"
    tab_widget.setCurrentIndex(idx)
    # Should not raise
    widget = tab_widget.widget(idx)
    assert widget is not None


def test_kanban_widget_edge_case(app):
    window = ProjectEditorWindow()
    tab_widget = window.tab_widget
    # Remove all tabs except Kanban, should not crash
    for i in reversed(range(tab_widget.count())):
        if "Kanban" not in tab_widget.tabText(i):
            tab_widget.removeTab(i)
    assert tab_widget.count() == 1
    assert "Kanban" in tab_widget.tabText(0)


def test_kanban_widget_failure_case(app):
    window = ProjectEditorWindow()
    tab_widget = window.tab_widget
    # Try to access a non-existent tab; should return None, not raise
    assert tab_widget.widget(999) is None
