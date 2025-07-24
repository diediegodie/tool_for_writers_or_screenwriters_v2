"""
Project Editor Window for Writer & Screenwriter Assistant
- Chapter and Scene list with drag-and-drop reordering
- Add/edit/delete chapters and scenes

Follows project structure and coding standards in docs/PLANNING.md and docs/instructions.instructions.md
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QLabel,
    QMessageBox,
    QInputDialog,
    QTextEdit,
    QToolBar,
    QSplitter,
    QListWidget as QtListWidget,
    QFrame,
    QTabWidget,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# Local storage for autosave/offline
from GUI.storage import project_store
from GUI.windows.project_editor.timeline_tab import TimelineTab
from GUI.windows.kanban_board import KanbanBoardWidget
from GUI.windows.project_editor.annotations import (
    add_footnote,
    add_annotation,
    refresh_annotation_list,
    on_annotation_clicked,
)


class ProjectEditorWindow(QWidget):
    def _autosave(self):
        """Autosave the current chapters/scenes to local storage."""
        # Reason: This method is required for QTimer and is missing, causing AttributeError in tests.
        # Save chapters to local storage (offline sync)
        project_store.save_projects([{"chapters": self.chapters}])
        # Optionally, add versioning logic here if needed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Editor")
        self.resize(1000, 700)
        self.chapters = []  # List of dicts: {"title": str, "scenes": [str]}
        self.current_scene_idx = None
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.timeout.connect(self._autosave)
        self._setup_ui()

    def _setup_ui(self):
        tab_widget = QTabWidget(self)
        self.tab_widget = tab_widget  # Store reference for testing and access

        # --- Main Editor Tab ---
        splitter = QSplitter(self)
        splitter.setChildrenCollapsible(False)

        # Left panel: Chapters and Scenes
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Chapters"))
        self.chapter_list = QListWidget()
        self.chapter_list.setDragDropMode(QListWidget.InternalMove)
        self.chapter_list.currentItemChanged.connect(self._on_chapter_selected)
        left_layout.addWidget(self.chapter_list)

        chapter_btns = QHBoxLayout()
        btn_add_chapter = QPushButton("Add Chapter")
        btn_edit_chapter = QPushButton("Edit Chapter")
        btn_delete_chapter = QPushButton("Delete Chapter")
        btn_add_chapter.clicked.connect(self._add_chapter)
        btn_edit_chapter.clicked.connect(self._edit_chapter)
        btn_delete_chapter.clicked.connect(self._delete_chapter)
        chapter_btns.addWidget(btn_add_chapter)
        chapter_btns.addWidget(btn_edit_chapter)
        chapter_btns.addWidget(btn_delete_chapter)
        left_layout.addLayout(chapter_btns)

        left_layout.addWidget(QLabel("Scenes"))
        self.scene_list = QListWidget()
        self.scene_list.setDragDropMode(QListWidget.InternalMove)
        self.scene_list.currentItemChanged.connect(self._on_scene_selected)
        left_layout.addWidget(self.scene_list)

        scene_btns = QHBoxLayout()
        btn_add_scene = QPushButton("Add Scene")
        btn_edit_scene = QPushButton("Edit Scene")
        btn_delete_scene = QPushButton("Delete Scene")
        btn_add_scene.clicked.connect(self._add_scene)
        btn_edit_scene.clicked.connect(self._edit_scene)
        btn_delete_scene.clicked.connect(self._delete_scene)
        scene_btns.addWidget(btn_add_scene)
        scene_btns.addWidget(btn_edit_scene)
        scene_btns.addWidget(btn_delete_scene)
        left_layout.addLayout(scene_btns)

        splitter.addWidget(left_panel)

        # Center panel: Scene Editor
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.addWidget(QLabel("Scene Editor"))

        # Formatting toolbar
        toolbar = QToolBar()
        btn_bold = QPushButton("B")
        btn_bold.setCheckable(True)
        btn_bold.setStyleSheet("font-weight: bold;")
        btn_bold.clicked.connect(self._toggle_bold)
        toolbar.addWidget(btn_bold)

        btn_italic = QPushButton("I")
        btn_italic.setCheckable(True)
        btn_italic.setStyleSheet("font-style: italic;")
        btn_italic.clicked.connect(self._toggle_italic)
        toolbar.addWidget(btn_italic)

        btn_underline = QPushButton("U")
        btn_underline.setCheckable(True)
        btn_underline.setStyleSheet("text-decoration: underline;")
        btn_underline.clicked.connect(self._toggle_underline)
        toolbar.addWidget(btn_underline)

        # Annotation button
        btn_add_annotation = QPushButton("Add Annotation")
        btn_add_annotation.clicked.connect(
            lambda: add_annotation(
                self,
                self.text_editor,
                self.chapter_list,
                self.scene_list,
                self.chapters,
                self._refresh_annotation_list,
            )
        )
        toolbar.addWidget(btn_add_annotation)

        # Footnote button
        btn_add_footnote = QPushButton("Add Footnote")
        btn_add_footnote.clicked.connect(
            lambda: add_footnote(
                self,
                self.text_editor,
                self.chapter_list,
                self.scene_list,
                self.chapters,
                self._refresh_annotation_list,
            )
        )
        toolbar.addWidget(btn_add_footnote)

        # Version history button
        btn_version_history = QPushButton("Version History")
        btn_version_history.clicked.connect(self.show_version_history)
        toolbar.addWidget(btn_version_history)

        center_layout.addWidget(toolbar)

        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Write your scene here...")
        self.text_editor.textChanged.connect(self._on_text_changed)
        center_layout.addWidget(self.text_editor, 1)

        splitter.addWidget(center_panel)

        # Right panel: Annotations/Footnotes
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("Annotations & Footnotes"))
        self.annotation_list = QtListWidget()
        self.annotation_list.setFrameShape(QFrame.StyledPanel)
        self.annotation_list.itemClicked.connect(
            lambda item: on_annotation_clicked(
                self,
                self.annotation_list,
                self.text_editor,
                self.chapter_list,
                self.scene_list,
                self.chapters,
            )
        )
        right_layout.addWidget(self.annotation_list, 1)

        splitter.addWidget(right_panel)
        splitter.setSizes([200, 600, 200])

        tab_widget.addTab(splitter, "Editor")

        # --- Story Planning Tab (Timeline) ---
        def get_scenes():
            cidx = self.chapter_list.currentRow()
            if cidx < 0 or cidx >= len(self.chapters):
                return []
            return self.chapters[cidx]["scenes"]

        def set_scenes(new_scenes):
            cidx = self.chapter_list.currentRow()
            if cidx < 0 or cidx >= len(self.chapters):
                return
            self.chapters[cidx]["scenes"] = new_scenes
            self._on_chapter_selected(self.chapter_list.currentItem(), None)

        timeline_tab = TimelineTab(get_scenes, set_scenes)
        tab_widget.addTab(timeline_tab, "Story Planning")

        # --- Kanban Board Tab ---
        # Gather available chapters and scenes for Kanban linking
        def get_available_links():
            links = []
            for cidx, chapter in enumerate(self.chapters):
                chapter_id = f"chapter:{cidx}"
                links.append(
                    {"id": chapter_id, "type": "chapter", "title": chapter["title"]}
                )
                for sidx, scene in enumerate(chapter.get("scenes", [])):
                    scene_id = f"chapter:{cidx}:scene:{sidx}"
                    scene_title = (
                        scene["title"] if isinstance(scene, dict) else str(scene)
                    )
                    links.append(
                        {
                            "id": scene_id,
                            "type": "scene",
                            "title": scene_title,
                            "chapter": chapter["title"],
                        }
                    )
            return links

        kanban_tab = KanbanBoardWidget(self, get_available_links)
        tab_widget.addTab(kanban_tab, "Kanban Board")

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(tab_widget)

        self._updating_text = False  # Prevent recursion

    def _sync_scenes_to_timeline(self):
        """Push current scenes to the timeline widget."""
        self.timeline_widget.layout.setSpacing(12)
        self.timeline_widget.layout.setContentsMargins(12, 12, 12, 12)
        # Clear timeline
        for i in reversed(range(self.timeline_widget.layout.count())):
            self.timeline_widget.layout.itemAt(i).widget().setParent(None)
        self.timeline_widget.cards.clear()
        cidx = self.chapter_list.currentRow()
        if cidx < 0 or cidx >= len(self.chapters):
            return
        scenes = self.chapters[cidx]["scenes"]
        for scene in scenes:
            title = scene["title"] if isinstance(scene, dict) else str(scene)
            self.timeline_widget.add_card(title)

    def _sync_timeline_to_scenes(self):
        """Update scene order in chapter from timeline widget order."""
        cidx = self.chapter_list.currentRow()
        if cidx < 0 or cidx >= len(self.chapters):
            return
        timeline_titles = [c.title for c in self.timeline_widget.cards]
        scenes = self.chapters[cidx]["scenes"]
        # Reorder scenes to match timeline
        new_scenes = []
        for title in timeline_titles:
            for scene in scenes:
                if (
                    isinstance(scene, dict) and scene["title"] == title
                ) or scene == title:
                    new_scenes.append(scene)
                    break
        self.chapters[cidx]["scenes"] = new_scenes
        self._on_chapter_selected(self.chapter_list.currentItem(), None)

    # --- Version History UI ---
    def show_version_history(self):
        cidx = self.chapter_list.currentRow()
        sidx = self.scene_list.currentRow()
        if cidx < 0 or sidx < 0:
            QMessageBox.information(
                self, "No Scene Selected", "Select a scene to view version history."
            )
            return
        scenes = self.chapters[cidx]["scenes"]
        scene = scenes[sidx]
        versions = scene.get("versions", [])
        if not versions:
            QMessageBox.information(self, "No Versions", "No previous versions found.")
            return
        # Simple dialog to select and restore version
        items = [f"Version {i+1}" for i in range(len(versions))]
        idx, ok = QInputDialog.getItem(
            self, "Restore Version", "Select version:", items, editable=False
        )
        if ok and idx:
            v_idx = items.index(idx)
            scene["content"] = versions[v_idx]["content"]
            self.text_editor.setHtml(scene["content"])
            # Remove restored version from history
            scene["versions"] = [v for i, v in enumerate(versions) if i != v_idx]

    def _refresh_annotation_list(self):
        refresh_annotation_list(
            self.annotation_list, self.chapter_list, self.scene_list, self.chapters
        )

    def _on_chapter_selected(self, current, previous):
        self.scene_list.clear()
        idx = self.chapter_list.currentRow()
        if idx >= 0 and idx < len(self.chapters):
            for scene in self.chapters[idx]["scenes"]:
                if isinstance(scene, dict):
                    self.scene_list.addItem(scene.get("title", "Untitled"))
                else:
                    self.scene_list.addItem(scene)
        self.text_editor.clear()
        self.current_scene_idx = None

    def _on_scene_selected(self, current, previous):
        cidx = self.chapter_list.currentRow()
        sidx = self.scene_list.currentRow()
        self.current_scene_idx = sidx
        self._updating_text = True
        if cidx >= 0 and sidx >= 0 and cidx < len(self.chapters):
            scenes = self.chapters[cidx]["scenes"]
            if sidx < len(scenes):
                scene = scenes[sidx]
                if isinstance(scene, dict):
                    self.text_editor.setHtml(scene.get("content", ""))
                else:
                    self.text_editor.setPlainText("")
        else:
            self.text_editor.clear()
        self._updating_text = False

    def _on_text_changed(self):
        if self._updating_text:
            return
        cidx = self.chapter_list.currentRow()
        sidx = self.scene_list.currentRow()
        if cidx >= 0 and sidx >= 0 and cidx < len(self.chapters):
            scenes = self.chapters[cidx]["scenes"]
            if sidx < len(scenes):
                scene = scenes[sidx]
                if not isinstance(scene, dict):
                    # Convert to dict if not already
                    scene = {"title": str(scene), "content": ""}
                    scenes[sidx] = scene
                # Versioning: save previous version if content changed
                new_content = self.text_editor.toHtml()
                if "content" in scene and scene["content"] != new_content:
                    if "versions" not in scene:
                        scene["versions"] = []
                    scene["versions"].append({"content": scene["content"]})
                scene["title"] = self.scene_list.item(sidx).text()
                scene["content"] = new_content
        # Start autosave debounce
        self._autosave_timer.start(2000)

    def _toggle_bold(self):
        cursor = self.text_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontWeight(
            QFont.Bold if fmt.fontWeight() != QFont.Bold else QFont.Normal
        )
        cursor.mergeCharFormat(fmt)
        self.text_editor.setTextCursor(cursor)

    def _toggle_italic(self):
        cursor = self.text_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        cursor.mergeCharFormat(fmt)
        self.text_editor.setTextCursor(cursor)

    def _toggle_underline(self):
        cursor = self.text_editor.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        cursor.mergeCharFormat(fmt)
        self.text_editor.setTextCursor(cursor)

    def _add_chapter(self):
        title, ok = QInputDialog.getText(self, "Add Chapter", "Chapter title:")
        if ok and title:
            self.chapters.append({"title": title, "scenes": []})
            self.chapter_list.addItem(title)

    def _edit_chapter(self):
        idx = self.chapter_list.currentRow()
        if idx < 0:
            return
        title, ok = QInputDialog.getText(
            self, "Edit Chapter", "Chapter title:", text=self.chapters[idx]["title"]
        )
        if ok and title:
            self.chapters[idx]["title"] = title
            self.chapter_list.item(idx).setText(title)

    def _delete_chapter(self):
        idx = self.chapter_list.currentRow()
        if idx < 0:
            return
        reply = QMessageBox.question(
            self,
            "Delete Chapter",
            f"Delete chapter '{self.chapters[idx]['title']}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.chapters.pop(idx)
            self.chapter_list.takeItem(idx)
            self.scene_list.clear()

    def _add_scene(self):
        idx = self.chapter_list.currentRow()
        if idx < 0:
            return
        title, ok = QInputDialog.getText(self, "Add Scene", "Scene title:")
        if ok and title:
            self.chapters[idx]["scenes"].append({"title": title, "content": ""})
            self.scene_list.addItem(title)

    def _edit_scene(self):
        cidx = self.chapter_list.currentRow()
        sidx = self.scene_list.currentRow()
        if cidx < 0 or sidx < 0:
            return
        scenes = self.chapters[cidx]["scenes"]
        current = scenes[sidx]
        current_title = current["title"] if isinstance(current, dict) else current
        title, ok = QInputDialog.getText(
            self, "Edit Scene", "Scene title:", text=current_title
        )
        if ok and title:
            if isinstance(current, dict):
                current["title"] = title
            else:
                scenes[sidx] = {"title": title, "content": ""}
            self.scene_list.item(sidx).setText(title)

    def _delete_scene(self):
        cidx = self.chapter_list.currentRow()
        sidx = self.scene_list.currentRow()
        if cidx < 0 or sidx < 0:
            return
        reply = QMessageBox.question(
            self,
            "Delete Scene",
            f"Delete scene '{self.chapters[cidx]['scenes'][sidx]}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.chapters[cidx]["scenes"].pop(sidx)
            self.scene_list.takeItem(sidx)
