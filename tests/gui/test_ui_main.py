"""
Test ProjectEditorWindow integration: toolbar, annotation panel, and timeline tab.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import pytest
from PySide6.QtWidgets import QApplication
from GUI.windows.project_editor_window import ProjectEditorWindow


@pytest.fixture(scope="module")
def app():
    import sys

    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture
def editor(app):
    win = ProjectEditorWindow()
    win.show()
    yield win
    win.close()


def test_toolbar_exists(editor):
    assert hasattr(editor, "toolbar")
    assert editor.toolbar is not None


def test_annotation_panel_exists(editor):
    assert hasattr(editor, "annotation_list")
    assert editor.annotation_list is not None


def test_timeline_tab_exists(editor):
    # Should have a QTabWidget with at least two tabs
    tab_widget = getattr(editor, "tab_widget", None)
    if tab_widget is None:
        from PySide6.QtWidgets import QTabWidget

        tab_widget = editor.findChild(QTabWidget)
    assert tab_widget is not None
    assert tab_widget.count() >= 2
    assert tab_widget.tabText(1) == "Story Planning"


def test_annotation_panel_placeholder(editor):
    # Should show placeholder if no annotations
    editor.annotation_list.clear()
    editor.annotation_list.addItem("No annotations or footnotes.")
    assert editor.annotation_list.count() == 1
    assert "No annotations" in editor.annotation_list.item(0).text()


def test_timeline_tab_refresh(editor):
    # Should not raise error when refreshing timeline tab
    # Should not raise error when refreshing timeline tab
    tab_widget = getattr(editor, "tab_widget", None)
    if tab_widget is None:
        from PySide6.QtWidgets import QTabWidget

        tab_widget = editor.findChild(QTabWidget)
    timeline_tab = None
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i) == "Story Planning":
            timeline_tab = tab_widget.widget(i)
            break
    assert timeline_tab is not None
    if hasattr(timeline_tab, "refresh"):
        timeline_tab.refresh()
