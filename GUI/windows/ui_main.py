"""
Main Project Editor Window: core window and layout
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QTabWidget, QSplitter
from .ui_toolbar import create_toolbar
from .ui_annotations import create_annotations_panel
from .ui_timeline import create_timeline_tab


class ProjectEditorWindow(QWidget):
    def __init__(self, parent=None, project=None):
        super().__init__(parent)
        self.setWindowTitle("Project Editor")
        self.resize(1000, 700)
        self._setup_ui()

    def _setup_ui(self):
        tab_widget = QTabWidget(self)
        splitter = QSplitter(self)
        splitter.setChildrenCollapsible(False)

        # --- Toolbar (top, above splitter) ---
        self.toolbar = create_toolbar(self)
        # --- Left panel: Chapters/Scenes (placeholder, to be implemented or imported) ---
        # For now, just a QWidget placeholder
        left_panel = QWidget()
        splitter.addWidget(left_panel)

        # --- Center panel: Text Editor (placeholder, to be implemented or imported) ---
        center_panel = QWidget()
        splitter.addWidget(center_panel)

        # --- Right panel: Annotations/Footnotes ---
        right_panel, self.annotation_list = create_annotations_panel(self)
        splitter.addWidget(right_panel)

        splitter.setSizes([200, 600, 200])
        tab_widget.addTab(splitter, "Editor")

        # --- Story Planning Tab (Timeline) ---
        def get_scenes():
            cidx = getattr(self, "chapter_list", None)
            chapters = getattr(self, "chapters", None)
            if cidx is None or chapters is None:
                return []
            idx = cidx.currentRow()
            if idx < 0 or idx >= len(chapters):
                return []
            return chapters[idx]["scenes"]

        def set_scenes(new_scenes):
            cidx = getattr(self, "chapter_list", None)
            chapters = getattr(self, "chapters", None)
            if cidx is None or chapters is None:
                return
            idx = cidx.currentRow()
            if idx < 0 or idx >= len(chapters):
                return
            chapters[idx]["scenes"] = new_scenes
            if hasattr(self, "_on_chapter_selected"):
                self._on_chapter_selected(cidx.currentItem(), None)

        from .ui_timeline import TimelineTab

        timeline_tab = TimelineTab(get_scenes, set_scenes)
        tab_widget.addTab(timeline_tab, "Story Planning")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(tab_widget)
        self._updating_text = False  # Prevent recursion
