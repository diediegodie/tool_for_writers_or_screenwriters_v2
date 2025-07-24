
# Project Editor Window is now split into feature modules:
# - ui_main.py: core window and layout
# - ui_toolbar.py: toolbar and navigation buttons
# - ui_annotations.py: annotations panel logic
# - ui_timeline.py: timeline-related widgets and logic
# - utils_ui.py: helper functions or small reusable UI elements

from .ui_main import ProjectEditorWindow

    def _insert_numbered_list(self):
        cursor = self.text_editor.textCursor()
        selected = cursor.selectedText()
        if selected:
            lines = selected.split("\u2029")
            new_text = "\n".join([f"{i+1}. {line}" for i, line in enumerate(lines)])
            cursor.insertText(new_text)
        else:
            cursor.insertText("1. ")

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
                self.text_editor.setReadOnly(False)
                if isinstance(scene, dict):
                    self.text_editor.setHtml(scene.get("content", ""))
                else:
                    self.text_editor.setPlainText("")
                # Refresh annotation/footnote list
                self._refresh_annotation_list()
                # Show placeholder if no annotations/footnotes
                ann = scene.get("annotations", []) if isinstance(scene, dict) else []
                fn = scene.get("footnotes", []) if isinstance(scene, dict) else []
                if not ann and not fn:
                    self.annotation_list.clear()
                    self.annotation_list.addItem("(No annotations or footnotes)")
            else:
                self.text_editor.clear()
                self.text_editor.setReadOnly(True)
                self.annotation_list.clear()
                self.annotation_list.addItem("(No annotations or footnotes)")
        else:
            self.text_editor.clear()
            self.text_editor.setReadOnly(True)
            self.annotation_list.clear()
            self.annotation_list.addItem("(No annotations or footnotes)")
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
                # Update markdown preview if enabled
                if getattr(self, "markdown_preview_enabled", False):
                    import markdown

                    html = markdown.markdown(self.text_editor.toPlainText())
                    self.markdown_view.setHtml(html)
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
