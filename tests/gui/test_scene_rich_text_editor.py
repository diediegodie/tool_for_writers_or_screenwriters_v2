import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import pytest
from PySide6.QtWidgets import QApplication
from GUI.windows.project_editor_window import ProjectEditorWindow
import time
from GUI.windows.project_editor import annotations


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


def test_basic_formatting(editor, qtbot):
    editor.chapters = [
        {"title": "Chapter 1", "scenes": [{"title": "Scene 1", "content": ""}]}
    ]
    editor.chapter_list.clear()
    editor.scene_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.chapter_list.setCurrentRow(0)
    editor.scene_list.addItem("Scene 1")
    editor.scene_list.setCurrentRow(0)
    editor.text_editor.setPlainText("Hello world")
    editor.text_editor.selectAll()
    editor._toggle_bold()
    html = editor.text_editor.toHtml()
    assert "font-weight" in html
    editor._toggle_italic()
    html = editor.text_editor.toHtml()
    assert "font-style:italic" in html
    editor._toggle_underline()
    html = editor.text_editor.toHtml()
    assert "underline" in html or "text-decoration" in html


def test_add_annotation(editor, qtbot):
    editor.chapters = [
        {"title": "Chapter 1", "scenes": [{"title": "Scene 1", "content": ""}]}
    ]
    editor.chapter_list.clear()
    editor.scene_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.chapter_list.setCurrentRow(0)
    editor.scene_list.addItem("Scene 1")
    editor.scene_list.setCurrentRow(0)
    editor.text_editor.setPlainText("annotate me")
    editor.text_editor.selectAll()
    # Patch QInputDialog.getText to simulate user input
    orig = annotations.QInputDialog.getText
    annotations.QInputDialog.getText = lambda *a, **k: (
        "Test annotation",
        True,
    )
    annotations.add_annotation(
        editor,
        editor.text_editor,
        editor.chapter_list,
        editor.scene_list,
        editor.chapters,
        editor._refresh_annotation_list,
    )
    annotations.QInputDialog.getText = orig
    scene = editor.chapters[0]["scenes"][0]
    assert "annotations" in scene
    assert scene["annotations"][0]["note"] == "Test annotation"
    assert editor.annotation_list.count() > 0


def test_add_footnote(editor, qtbot):
    editor.chapters = [
        {"title": "Chapter 1", "scenes": [{"title": "Scene 1", "content": ""}]}
    ]
    editor.chapter_list.clear()
    editor.scene_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.chapter_list.setCurrentRow(0)
    editor.scene_list.addItem("Scene 1")
    editor.scene_list.setCurrentRow(0)
    editor.text_editor.setPlainText("footnote me")
    editor.text_editor.selectAll()
    # Patch QInputDialog.getText to simulate user input
    orig = annotations.QInputDialog.getText
    annotations.QInputDialog.getText = lambda *a, **k: (
        "Test footnote",
        True,
    )
    annotations.add_footnote(
        editor,
        editor.text_editor,
        editor.chapter_list,
        editor.scene_list,
        editor.chapters,
        editor._refresh_annotation_list,
    )
    annotations.QInputDialog.getText = orig
    scene = editor.chapters[0]["scenes"][0]
    assert "footnotes" in scene
    assert scene["footnotes"][0]["note"] == "Test footnote"
    assert editor.annotation_list.count() > 0


def test_autosave_and_offline(editor, qtbot, tmp_path, monkeypatch):
    # Patch project_store to use a temp file
    import GUI.storage.project_store as ps

    temp_file = tmp_path / "projects.json"
    monkeypatch.setattr(ps, "PROJECTS_FILE", str(temp_file))
    editor.chapters = [
        {
            "title": "Chapter 1",
            "scenes": [{"title": "Scene 1", "content": "Initial content"}],
        }
    ]
    editor.chapter_list.clear()
    editor.scene_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.chapter_list.setCurrentRow(0)
    editor.scene_list.addItem("Scene 1")
    editor.scene_list.setCurrentRow(0)
    editor.text_editor.setPlainText("Autosave test")
    editor._on_text_changed()
    qtbot.wait(2200)  # Wait for autosave debounce
    # Reload from file
    projects = ps.load_projects()
    assert projects[0]["chapters"][0]["scenes"][0]["content"]


def test_version_history(editor, qtbot):
    editor.chapters = [
        {"title": "Chapter 1", "scenes": [{"title": "Scene 1", "content": "v1"}]}
    ]
    editor.chapter_list.clear()
    editor.scene_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.chapter_list.setCurrentRow(0)
    editor.scene_list.addItem("Scene 1")
    editor.scene_list.setCurrentRow(0)
    editor.text_editor.setPlainText("v1")
    editor._on_text_changed()
    editor.text_editor.setPlainText("v2")
    editor._on_text_changed()
    scene = editor.chapters[0]["scenes"][0]
    assert "versions" in scene
    assert len(scene["versions"]) >= 1
    # Patch QInputDialog.getItem to simulate user restoring version
    orig = editor.show_version_history.__globals__["QInputDialog"].getItem
    editor.show_version_history.__globals__["QInputDialog"].getItem = lambda *a, **k: (
        "Version 1",
        True,
    )
    editor.show_version_history()
    editor.show_version_history.__globals__["QInputDialog"].getItem = orig
    assert editor.text_editor.toPlainText() == "v1"
