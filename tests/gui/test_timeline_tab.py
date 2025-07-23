"""
Tests for TimelineTab (story planning tab) in the Project Editor.
Covers normal, edge, and failure cases for timeline sync and UI.
"""

import pytest
from PySide6.QtWidgets import QApplication, QListWidget, QWidget
from GUI.windows.project_editor.timeline_tab import TimelineTab


@pytest.fixture
def dummy_chapters():
    return [
        {
            "title": "Chapter 1",
            "scenes": [
                {"title": "Scene A"},
                {"title": "Scene B"},
                {"title": "Scene C"},
            ],
        },
        {"title": "Chapter 2", "scenes": []},
    ]


@pytest.fixture
def chapter_list(qtbot, dummy_chapters):
    widget = QListWidget()
    for ch in dummy_chapters:
        widget.addItem(ch["title"])
    widget.setCurrentRow(0)
    return widget


def get_scenes_factory(chapters, chapter_list):
    def get_scenes():
        cidx = chapter_list.currentRow()
        if cidx < 0 or cidx >= len(chapters):
            return []
        return chapters[cidx]["scenes"]

    return get_scenes


def set_scenes_factory(chapters, chapter_list):
    def set_scenes(new_scenes):
        cidx = chapter_list.currentRow()
        if cidx < 0 or cidx >= len(chapters):
            return
        chapters[cidx]["scenes"] = new_scenes

    return set_scenes


@pytest.fixture
def timeline_tab(qtbot, dummy_chapters, chapter_list):
    get_scenes = get_scenes_factory(dummy_chapters, chapter_list)
    set_scenes = set_scenes_factory(dummy_chapters, chapter_list)
    tab = TimelineTab(get_scenes, set_scenes)
    qtbot.addWidget(tab)
    return tab


def test_sync_scenes_to_timeline_normal(timeline_tab, dummy_chapters, chapter_list):
    # Normal case: scenes present
    timeline_tab.sync_scenes_to_timeline()
    titles = [c.title for c in timeline_tab.timeline_widget.cards]
    assert titles == ["Scene A", "Scene B", "Scene C"]


def test_sync_scenes_to_timeline_empty(timeline_tab, dummy_chapters, chapter_list):
    # Edge case: no scenes in chapter 2
    chapter_list.setCurrentRow(1)
    timeline_tab.sync_scenes_to_timeline()
    assert len(timeline_tab.timeline_widget.cards) == 0


def test_sync_timeline_to_scenes_reorder(timeline_tab, dummy_chapters, chapter_list):
    # Normal: reorder timeline cards, sync back to scenes
    timeline_tab.sync_scenes_to_timeline()
    # Simulate drag-and-drop reorder
    cards = timeline_tab.timeline_widget.cards
    cards[0], cards[2] = cards[2], cards[0]  # Swap first and last
    timeline_tab.sync_timeline_to_scenes()
    scenes = dummy_chapters[0]["scenes"]
    assert scenes[0]["title"] == "Scene C"
    assert scenes[2]["title"] == "Scene A"


def test_sync_timeline_to_scenes_empty(timeline_tab, dummy_chapters, chapter_list):
    # Edge: sync with empty timeline
    chapter_list.setCurrentRow(1)
    timeline_tab.sync_timeline_to_scenes()
    assert dummy_chapters[1]["scenes"] == []


def test_sync_timeline_to_scenes_invalid_index(
    timeline_tab, dummy_chapters, chapter_list
):
    # Failure: invalid chapter index
    chapter_list.setCurrentRow(-1)
    timeline_tab.sync_timeline_to_scenes()  # Should not raise
    assert True
