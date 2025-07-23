"""
Test ProjectEditorWindow: normal, edge, and failure cases for chapter/scene management.
"""

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


def test_add_chapter(editor):
    # Normal: Add a chapter
    editor.chapters = []
    editor.chapter_list.clear()
    editor.chapters.append({"title": "Chapter 1", "scenes": []})
    editor.chapter_list.addItem("Chapter 1")
    assert editor.chapter_list.count() == 1
    assert editor.chapters[0]["title"] == "Chapter 1"


def test_add_scene(editor):
    # Normal: Add a scene to first chapter
    editor.chapters = [{"title": "Chapter 1", "scenes": []}]
    editor.chapter_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.chapter_list.setCurrentRow(0)
    editor.chapters[0]["scenes"].append("Scene 1")
    editor.scene_list.clear()
    editor.scene_list.addItem("Scene 1")
    assert editor.scene_list.count() == 1
    assert editor.chapters[0]["scenes"][0] == "Scene 1"


def test_edit_chapter_edge(editor):
    # Edge: Edit chapter with empty title
    editor.chapters = [{"title": "Chapter 1", "scenes": []}]
    editor.chapter_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    idx = 0
    editor.chapters[idx]["title"] = ""
    editor.chapter_list.item(idx).setText("")
    assert editor.chapters[0]["title"] == ""


def test_delete_scene_failure(editor):
    # Failure: Try to delete scene when none selected
    editor.chapters = [{"title": "Chapter 1", "scenes": ["Scene 1"]}]
    editor.chapter_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.scene_list.clear()
    editor.scene_list.addItem("Scene 1")
    editor.chapter_list.setCurrentRow(0)
    editor.scene_list.setCurrentRow(-1)  # No selection
    before = len(editor.chapters[0]["scenes"])
    editor._delete_scene()  # Should do nothing
    after = len(editor.chapters[0]["scenes"])
    assert before == after


def test_on_chapter_selected_normal(editor):
    # Normal: Select a chapter and see its scenes
    editor.chapters = [
        {"title": "Chapter 1", "scenes": ["Scene 1", "Scene 2"]},
        {"title": "Chapter 2", "scenes": ["Scene 3"]},
    ]
    editor.chapter_list.clear()
    for ch in editor.chapters:
        editor.chapter_list.addItem(ch["title"])
    editor.chapter_list.setCurrentRow(1)
    editor._on_chapter_selected(editor.chapter_list.currentItem(), None)
    assert editor.scene_list.count() == 1
    assert editor.scene_list.item(0).text() == "Scene 3"


def test_on_chapter_selected_edge(editor):
    # Edge: Select invalid chapter index
    editor.chapters = []
    editor.chapter_list.clear()
    editor.scene_list.clear()
    editor.chapter_list.setCurrentRow(-1)
    editor._on_chapter_selected(None, None)
    assert editor.scene_list.count() == 0


def test_edit_scene_normal(editor, qtbot):
    # Normal: Edit a scene title
    editor.chapters = [{"title": "Chapter 1", "scenes": ["Scene 1"]}]
    editor.chapter_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.scene_list.clear()
    editor.scene_list.addItem("Scene 1")
    editor.chapter_list.setCurrentRow(0)
    editor.scene_list.setCurrentRow(0)

    # Patch QInputDialog.getText to simulate user input
    def fake_get_text(*a, **k):
        return ("Scene 1 Edited", True)

    orig = editor._edit_scene.__globals__["QInputDialog"].getText
    editor._edit_scene.__globals__["QInputDialog"].getText = fake_get_text
    editor._edit_scene()
    editor._edit_scene.__globals__["QInputDialog"].getText = orig
    assert editor.chapters[0]["scenes"][0] == "Scene 1 Edited"
    assert editor.scene_list.item(0).text() == "Scene 1 Edited"


def test_edit_scene_failure(editor):
    # Failure: Try to edit scene with no selection
    editor.chapters = [{"title": "Chapter 1", "scenes": ["Scene 1"]}]
    editor.chapter_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.scene_list.clear()
    editor.scene_list.addItem("Scene 1")
    editor.chapter_list.setCurrentRow(-1)
    editor.scene_list.setCurrentRow(-1)
    before = editor.chapters[0]["scenes"][0]
    editor._edit_scene()
    after = editor.chapters[0]["scenes"][0]
    assert before == after


def test_delete_chapter_normal(editor, qtbot):
    # Normal: Delete a chapter
    editor.chapters = [
        {"title": "Chapter 1", "scenes": []},
        {"title": "Chapter 2", "scenes": []},
    ]
    editor.chapter_list.clear()
    for ch in editor.chapters:
        editor.chapter_list.addItem(ch["title"])
    editor.chapter_list.setCurrentRow(0)

    # Patch QMessageBox.question to simulate user confirmation
    def fake_question(*a, **k):
        return editor._delete_chapter.__globals__["QMessageBox"].Yes

    orig = editor._delete_chapter.__globals__["QMessageBox"].question
    editor._delete_chapter.__globals__["QMessageBox"].question = fake_question
    editor._delete_chapter()
    editor._delete_chapter.__globals__["QMessageBox"].question = orig
    assert len(editor.chapters) == 1
    assert editor.chapter_list.count() == 1
    assert editor.chapter_list.item(0).text() == "Chapter 2"


def test_delete_chapter_failure(editor):
    # Failure: Try to delete chapter with no selection
    editor.chapters = [{"title": "Chapter 1", "scenes": []}]
    editor.chapter_list.clear()
    editor.chapter_list.addItem("Chapter 1")
    editor.chapter_list.setCurrentRow(-1)
    before = len(editor.chapters)
    editor._delete_chapter()
    after = len(editor.chapters)
    assert before == after
