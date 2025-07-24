"""
Timeline-related widgets and logic for Project Editor
"""

# ...import needed widgets...
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt


class TimelineCard(QListWidgetItem):
    def __init__(self, title):
        super().__init__(title)
        self.title = title


class TimelineTab(QWidget):
    def __init__(self, get_scenes, set_scenes):
        super().__init__()
        self.get_scenes = get_scenes
        self.set_scenes = set_scenes
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Drag to reorder scenes. Double-click to edit.")
        self.layout.addWidget(self.label)
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.layout.addWidget(self.list_widget, 1)
        self.refresh()

        # Connect signals
        self.list_widget.model().rowsMoved.connect(self._on_reorder)
        self.list_widget.itemDoubleClicked.connect(self._on_edit)

    def refresh(self):
        self.list_widget.clear()
        for scene in self.get_scenes():
            title = scene["title"] if isinstance(scene, dict) else str(scene)
            self.list_widget.addItem(TimelineCard(title))

    def _on_reorder(self):
        # Update scene order in parent using set_scenes
        titles = [
            self.list_widget.item(i).text() for i in range(self.list_widget.count())
        ]
        scenes = self.get_scenes()
        new_scenes = []
        for title in titles:
            for scene in scenes:
                if (
                    isinstance(scene, dict) and scene["title"] == title
                ) or scene == title:
                    new_scenes.append(scene)
                    break
        self.set_scenes(new_scenes)

    def _on_edit(self, item):
        # Double-click to edit scene title
        idx = self.list_widget.row(item)
        scenes = self.get_scenes()
        if 0 <= idx < len(scenes):
            scene = scenes[idx]
            # Assume parent editor has edit_scene method
            if hasattr(self.parent(), "edit_scene"):
                self.parent().edit_scene(idx)


def create_timeline_tab(get_scenes, set_scenes):
    # ...create and return timeline tab widget...
    pass
