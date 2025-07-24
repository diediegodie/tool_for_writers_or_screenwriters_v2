"""
Test suite for newly integrated GUI features
Tests for export functionality, navigation, entity panels integration, and menu actions
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from GUI.windows.project_editor_window import ProjectEditorWindow
from GUI.windows.export_dialog import ExportDialog
from GUI.windows.character_panel import CharacterPanel
from GUI.windows.location_panel import LocationPanel
from GUI.windows.event_panel import EventPanel


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture
def project_editor(app, qtbot, monkeypatch):
    # Mock QMessageBox to prevent blocking dialogs
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)

    editor = ProjectEditorWindow()
    qtbot.addWidget(editor)
    editor.show()
    yield editor
    editor.close()


def test_export_dialog_creation(project_editor, qtbot):
    """Test that export dialog can be created and opened"""
    # Add some test data
    project_editor.chapters = [
        {
            "title": "Test Chapter",
            "scenes": [{"title": "Test Scene", "content": "Test content"}],
        }
    ]

    # Test opening export dialog
    project_editor._show_export_dialog()
    # Since dialog is modal, we just verify no exception was thrown
    assert True


def test_navigation_functions(project_editor, qtbot):
    """Test chapter and scene navigation functions"""
    # Add test chapters and scenes
    project_editor.chapters = [
        {
            "title": "Chapter 1",
            "scenes": [
                {"title": "Scene 1", "content": "Content 1"},
                {"title": "Scene 2", "content": "Content 2"},
            ],
        },
        {
            "title": "Chapter 2",
            "scenes": [{"title": "Scene 3", "content": "Content 3"}],
        },
    ]

    # Populate the lists
    project_editor.chapter_list.clear()
    for chapter in project_editor.chapters:
        project_editor.chapter_list.addItem(chapter["title"])

    # Test chapter navigation
    project_editor.chapter_list.setCurrentRow(0)
    project_editor.go_to_next_chapter()
    assert project_editor.chapter_list.currentRow() == 1

    project_editor.go_to_prev_chapter()
    assert project_editor.chapter_list.currentRow() == 0


def test_scene_navigation(project_editor, qtbot):
    """Test scene navigation within a chapter"""
    # Setup test data
    project_editor.chapters = [
        {
            "title": "Test Chapter",
            "scenes": [
                {"title": "Scene 1", "content": "Content 1"},
                {"title": "Scene 2", "content": "Content 2"},
                {"title": "Scene 3", "content": "Content 3"},
            ],
        }
    ]

    # Populate the chapter list first
    project_editor.chapter_list.clear()
    project_editor.chapter_list.addItem("Test Chapter")
    project_editor.chapter_list.setCurrentRow(0)  # Select the chapter

    # Populate the scene list
    project_editor.scene_list.clear()
    for scene in project_editor.chapters[0]["scenes"]:
        project_editor.scene_list.addItem(scene["title"])

    # Test scene navigation
    project_editor.scene_list.setCurrentRow(1)  # Start at scene 2
    project_editor.go_to_next_scene()
    assert project_editor.scene_list.currentRow() == 2

    project_editor.go_to_prev_scene()
    assert project_editor.scene_list.currentRow() == 1

    # Test navigate to specific scene
    project_editor._navigate_to_scene(0)
    assert project_editor.scene_list.currentRow() == 0

    project_editor._navigate_to_scene(-1)  # Last scene
    assert project_editor.scene_list.currentRow() == 2


def test_version_history_functionality(project_editor, qtbot, monkeypatch):
    """Test version history feature"""
    # Mock QInputDialog to prevent blocking
    monkeypatch.setattr(
        "PySide6.QtWidgets.QInputDialog.getItem",
        lambda *args, **kwargs: ("Version 1", True),
    )

    # Setup test data with versions
    project_editor.chapters = [
        {
            "title": "Test Chapter",
            "scenes": [
                {
                    "title": "Test Scene",
                    "content": "Current content",
                    "versions": [
                        {"content": "Old content 1"},
                        {"content": "Old content 2"},
                    ],
                }
            ],
        }
    ]

    # Select the scene
    project_editor.chapter_list.clear()
    project_editor.chapter_list.addItem("Test Chapter")
    project_editor.chapter_list.setCurrentRow(0)

    project_editor.scene_list.clear()
    project_editor.scene_list.addItem("Test Scene")
    project_editor.scene_list.setCurrentRow(0)

    # Test version history
    project_editor.show_version_history()
    # Verify no exception was thrown
    assert True


def test_annotation_details_display(project_editor, qtbot):
    """Test annotation details dialog"""
    annotation_data = {
        "type": "annotation",
        "text": "Selected text",
        "note": "This is a test annotation",
    }

    project_editor.show_annotation_details(annotation_data)
    # Verify no exception was thrown
    assert True


def test_menu_bar_actions(project_editor, qtbot):
    """Test that menu bar actions are properly connected"""
    # Test that menu bar exists
    menu_bar = project_editor.findChild(project_editor.__class__, "")
    # Just verify the methods exist and can be called
    assert hasattr(project_editor, "_show_export_dialog")
    assert hasattr(project_editor, "show_version_history")
    assert hasattr(project_editor, "go_to_prev_chapter")
    assert hasattr(project_editor, "go_to_next_chapter")
    assert hasattr(project_editor, "go_to_prev_scene")
    assert hasattr(project_editor, "go_to_next_scene")


def test_entity_panel_integration(project_editor, qtbot):
    """Test integration with character, location, and event panels"""
    # Test opening panels
    project_editor._open_characters_panel()
    assert hasattr(project_editor, "_characters_panel")

    project_editor._open_locations_panel()
    assert hasattr(project_editor, "_locations_panel")

    project_editor._open_events_panel()
    assert hasattr(project_editor, "_events_panel")


def test_context_menu_creation(project_editor, qtbot):
    """Test context menu creation and actions"""
    # Simulate right-click to trigger context menu
    project_editor._show_context_menu(project_editor.rect().center())
    # Verify no exception was thrown
    assert True


def test_keyboard_shortcuts_setup(project_editor, qtbot):
    """Test that keyboard shortcuts are properly configured"""
    # Verify shortcuts setup method exists
    assert hasattr(project_editor, "_setup_keyboard_shortcuts")

    # Test shortcuts were created (F1-F4)
    shortcuts = project_editor.findChildren(project_editor.__class__, "")
    # Just verify the method runs without error
    project_editor._setup_keyboard_shortcuts()


def test_character_panel_insertion(app, qtbot, monkeypatch):
    """Test character reference insertion functionality"""
    # Mock QMessageBox
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)

    # Create a mock parent with text_editor
    parent = ProjectEditorWindow()
    qtbot.addWidget(parent)

    panel = CharacterPanel(parent)
    qtbot.addWidget(panel)

    # Add a test character
    panel.name_input.setText("Test Character")
    panel.desc_input.setPlainText("A test character")
    panel.add_character()

    # Test insertion (should handle gracefully even without proper text editor)
    panel.list_widget.setCurrentRow(0)
    panel.insert_character_reference()

    parent.close()
    panel.close()


def test_export_worker_functionality(qtbot):
    """Test export worker for different formats"""
    from GUI.windows.export_dialog import ExportWorker
    import tempfile
    import os

    test_data = {
        "title": "Test Project",
        "chapters": [
            {
                "title": "Test Chapter",
                "scenes": [{"title": "Test Scene", "content": "Test content"}],
            }
        ],
    }

    # Test Markdown export
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        worker = ExportWorker(test_data, "Markdown", f.name)
        worker.run()

        # Check file was created
        assert os.path.exists(f.name)

        # Check content
        with open(f.name, "r", encoding="utf-8") as rf:
            content = rf.read()
            assert "Test Project" in content
            assert "Test Chapter" in content
            assert "Test Scene" in content

        os.unlink(f.name)


def test_toolbar_integration(project_editor, qtbot):
    """Test that toolbar functions are properly integrated"""
    # Test toolbar functions exist and can be called
    assert hasattr(project_editor, "_insert_numbered_list")
    assert hasattr(project_editor, "_handle_undo")
    assert hasattr(project_editor, "toggle_markdown_preview")

    # Test calling these functions
    project_editor._insert_numbered_list()
    project_editor._handle_undo()
    project_editor.toggle_markdown_preview(True)
    project_editor.toggle_markdown_preview(False)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
