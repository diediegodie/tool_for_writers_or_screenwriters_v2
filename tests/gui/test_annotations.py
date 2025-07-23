"""
Tests for annotation and footnote logic in annotations.py
Covers normal, edge, and failure cases for all functions.
"""

import pytest
from PySide6.QtWidgets import QTextEdit, QListWidget, QWidget
from GUI.windows.project_editor import annotations


@pytest.fixture
def dummy_chapters():
    return [
        {
            "title": "Chapter 1",
            "scenes": [{"title": "Scene A", "annotations": [], "footnotes": []}],
        }
    ]


@pytest.fixture
def chapter_list(qtbot, dummy_chapters):
    widget = QListWidget()
    for ch in dummy_chapters:
        widget.addItem(ch["title"])
    widget.setCurrentRow(0)
    return widget


@pytest.fixture
def scene_list(qtbot, dummy_chapters):
    widget = QListWidget()
    for s in dummy_chapters[0]["scenes"]:
        widget.addItem(s["title"])
    widget.setCurrentRow(0)
    return widget


@pytest.fixture
def text_editor(qtbot):
    editor = QTextEdit()
    editor.setPlainText("Some text to annotate.")
    qtbot.addWidget(editor)
    return editor


@pytest.fixture
def annotation_list(qtbot):
    widget = QListWidget()
    qtbot.addWidget(widget)
    return widget


class DummyParent(QWidget):
    pass


def test_add_annotation_normal(
    qtbot, text_editor, chapter_list, scene_list, dummy_chapters
):
    parent = DummyParent()
    text_editor.selectAll()

    def fake_refresh():
        pass

    # Simulate dialog
    annotations.QInputDialog.getText = lambda *a, **k: ("note", True)
    annotations.QMessageBox.information = lambda *a, **k: None
    annotations.add_annotation(
        parent, text_editor, chapter_list, scene_list, dummy_chapters, fake_refresh
    )
    scene = dummy_chapters[0]["scenes"][0]
    assert scene["annotations"]


def test_add_annotation_no_selection(
    qtbot, text_editor, chapter_list, scene_list, dummy_chapters
):
    parent = DummyParent()

    def fake_refresh():
        pass

    from PySide6.QtGui import QTextCursor

    text_editor.moveCursor(QTextCursor.End)
    annotations.QInputDialog.getText = lambda *a, **k: ("note", True)
    called = {}

    def fake_info(*a, **k):
        called["info"] = True

    annotations.QMessageBox.information = fake_info
    annotations.add_annotation(
        parent, text_editor, chapter_list, scene_list, dummy_chapters, fake_refresh
    )
    assert called["info"]


def test_add_footnote_normal(
    qtbot, text_editor, chapter_list, scene_list, dummy_chapters
):
    parent = DummyParent()
    text_editor.selectAll()

    def fake_refresh():
        pass

    annotations.QInputDialog.getText = lambda *a, **k: ("foot", True)
    annotations.QMessageBox.information = lambda *a, **k: None
    annotations.add_footnote(
        parent, text_editor, chapter_list, scene_list, dummy_chapters, fake_refresh
    )
    scene = dummy_chapters[0]["scenes"][0]
    assert scene["footnotes"]


def test_add_footnote_no_selection(
    qtbot, text_editor, chapter_list, scene_list, dummy_chapters
):
    parent = DummyParent()

    def fake_refresh():
        pass

    from PySide6.QtGui import QTextCursor

    text_editor.moveCursor(QTextCursor.End)
    annotations.QInputDialog.getText = lambda *a, **k: ("foot", True)
    called = {}

    def fake_info(*a, **k):
        called["info"] = True

    annotations.QMessageBox.information = fake_info
    annotations.add_footnote(
        parent, text_editor, chapter_list, scene_list, dummy_chapters, fake_refresh
    )
    assert called["info"]


def test_refresh_annotation_list(
    annotation_list, chapter_list, scene_list, dummy_chapters
):
    # Add dummy annotation and footnote
    scene = dummy_chapters[0]["scenes"][0]
    scene["annotations"].append({"text": "a", "note": "n"})
    scene["footnotes"].append({"text": "b", "note": "m"})
    annotations.refresh_annotation_list(
        annotation_list, chapter_list, scene_list, dummy_chapters
    )
    assert annotation_list.count() == 2


def test_on_annotation_clicked(
    annotation_list, text_editor, chapter_list, scene_list, dummy_chapters
):
    # Add dummy annotation and footnote with positions
    scene = dummy_chapters[0]["scenes"][0]
    scene["annotations"].append({"text": "a", "note": "n", "start": 0, "end": 1})
    scene["footnotes"].append({"text": "b", "note": "m", "start": 2, "end": 3})
    annotation_list.addItem("[A] a: n")
    annotation_list.addItem("[F] b: m")
    annotation_list.setCurrentRow(1)
    annotations.on_annotation_clicked(
        None, annotation_list, text_editor, chapter_list, scene_list, dummy_chapters
    )
    cursor = text_editor.textCursor()
    assert cursor.selectionStart() == 2 and cursor.selectionEnd() == 3
