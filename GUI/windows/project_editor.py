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
)
from PySide6.QtCore import Qt


class ProjectEditorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Editor")
        self.resize(800, 600)
        self.chapters = []  # List of dicts: {"title": str, "scenes": [str]}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # Chapter List
        self.chapter_list = QListWidget()
        self.chapter_list.setDragDropMode(QListWidget.InternalMove)
        self.chapter_list.currentItemChanged.connect(self._on_chapter_selected)
        layout.addWidget(QLabel("Chapters"))
        layout.addWidget(self.chapter_list)

        # Chapter controls
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
        layout.addLayout(chapter_btns)

        # Scene List
        self.scene_list = QListWidget()
        self.scene_list.setDragDropMode(QListWidget.InternalMove)
        layout.addWidget(QLabel("Scenes"))
        layout.addWidget(self.scene_list)

        # Scene controls
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
        layout.addLayout(scene_btns)

    def _on_chapter_selected(self, current, previous):
        self.scene_list.clear()
        idx = self.chapter_list.currentRow()
        if idx >= 0 and idx < len(self.chapters):
            for scene in self.chapters[idx]["scenes"]:
                self.scene_list.addItem(scene)

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
            self.chapters[idx]["scenes"].append(title)
            self.scene_list.addItem(title)

    def _edit_scene(self):
        cidx = self.chapter_list.currentRow()
        sidx = self.scene_list.currentRow()
        if cidx < 0 or sidx < 0:
            return
        title, ok = QInputDialog.getText(
            self, "Edit Scene", "Scene title:", text=self.chapters[cidx]["scenes"][sidx]
        )
        if ok and title:
            self.chapters[cidx]["scenes"][sidx] = title
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
