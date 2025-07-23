import pytest
from PySide6.QtWidgets import QApplication
from GUI.windows.project_editor import ProjectEditorWindow


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


def test_scene_editor_basic_formatting(editor, qtbot):
    # Normal: Add a chapter and scene, select scene, edit content, apply formatting
    editor.chapters = []
    editor.chapter_list.clear()
    editor.scene_list.clear()
    editor.chapters.append({"title": "Chapter 1", "scenes": []})
    editor.chapter_list.addItem("Chapter 1")
    editor.chapter_list.setCurrentRow(0)
    editor._add_scene()
    editor.scene_list.setCurrentRow(0)
    # Simulate entering text
    editor.text_editor.setPlainText("Hello world")
    # Apply bold
    editor.text_editor.selectAll()
    editor._toggle_bold()
    html = editor.text_editor.toHtml()
    assert (
        "font-weight:600" in html
        or "font-weight:bold" in html
        or "font-weight:700" in html
    )
    # Apply italic
    editor._toggle_italic()
    html = editor.text_editor.toHtml()
    assert "font-style:italic" in html
    # Apply underline
    editor._toggle_underline()
    html = editor.text_editor.toHtml()
    assert "text-decoration: underline" in html or "underline" in html


def test_scene_editor_edge_case_empty_scene(editor, qtbot):
    # Edge: Select a scene with no content
    editor.chapters = [
        {"title": "Chapter 1", "scenes": [{"title": "Scene 1", "content": ""}]}
    ]
    editor.chapter_list.clear()
    editor.scene_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.chapter_list.setCurrentRow(0)
    editor.scene_list.addItem("Scene 1")
    editor.scene_list.setCurrentRow(0)
    editor._on_scene_selected(editor.scene_list.currentItem(), None)
    assert editor.text_editor.toPlainText() == ""


def test_scene_editor_failure_no_scene_selected(editor, qtbot):
    # Failure: Try to edit content with no scene selected
    editor.chapters = [{"title": "Chapter 1", "scenes": []}]
    editor.chapter_list.clear()
    editor.scene_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.chapter_list.setCurrentRow(0)
    editor.scene_list.setCurrentRow(-1)
    before = editor.text_editor.toPlainText()
    editor.text_editor.setPlainText("Should not save")
    editor._on_text_changed()
    # No scene to update, so chapters data should remain unchanged
    assert editor.chapters[0]["scenes"] == []
