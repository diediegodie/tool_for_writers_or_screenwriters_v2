from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from GUI.windows.timeline_board import TimelineBoardWidget


class TimelineTab(QWidget):
    def __init__(self, get_scenes_callback, set_scenes_callback, parent=None):
        super().__init__(parent)
        self.get_scenes = get_scenes_callback
        self.set_scenes = set_scenes_callback
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Timeline / Storyboard"))
        self.timeline_widget = TimelineBoardWidget()
        layout.addWidget(self.timeline_widget)
        sync_btns = QHBoxLayout()
        btn_sync_to_timeline = QPushButton("Sync Scenes to Timeline")
        btn_sync_to_timeline.clicked.connect(self.sync_scenes_to_timeline)
        btn_sync_from_timeline = QPushButton("Sync Timeline to Scenes")
        btn_sync_from_timeline.clicked.connect(self.sync_timeline_to_scenes)
        sync_btns.addWidget(btn_sync_to_timeline)
        sync_btns.addWidget(btn_sync_from_timeline)
        layout.addLayout(sync_btns)

    def sync_scenes_to_timeline(self):
        self.timeline_widget.layout.setSpacing(12)
        self.timeline_widget.layout.setContentsMargins(12, 12, 12, 12)
        for i in reversed(range(self.timeline_widget.layout.count())):
            self.timeline_widget.layout.itemAt(i).widget().setParent(None)
        self.timeline_widget.cards.clear()
        scenes = self.get_scenes()
        for scene in scenes:
            title = scene["title"] if isinstance(scene, dict) else str(scene)
            self.timeline_widget.add_card(title)

    def sync_timeline_to_scenes(self):
        timeline_titles = [c.title for c in self.timeline_widget.cards]
        scenes = self.get_scenes()
        new_scenes = []
        for title in timeline_titles:
            for scene in scenes:
                if (
                    isinstance(scene, dict) and scene["title"] == title
                ) or scene == title:
                    new_scenes.append(scene)
                    break
        self.set_scenes(new_scenes)
