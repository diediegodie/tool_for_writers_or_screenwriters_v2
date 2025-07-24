"""
Export Dialog for Project Editor
Provides export functionality to various formats (DOCX, PDF, Markdown, Fountain)
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QTextEdit,
    QGroupBox,
)
from PySide6.QtCore import Qt, QThread, QTimer, Signal
import json
import os
from pathlib import Path


class ExportWorker(QThread):
    """Worker thread for export operations"""

    finished = Signal(str)  # Signal with success/error message
    progress = Signal(int)  # Progress percentage

    def __init__(self, export_data, format_type, output_path):
        super().__init__()
        self.export_data = export_data
        self.format_type = format_type
        self.output_path = output_path

    def run(self):
        try:
            self.progress.emit(25)

            if self.format_type == "Markdown":
                self._export_markdown()
            elif self.format_type == "JSON":
                self._export_json()
            elif self.format_type == "Plain Text":
                self._export_plain_text()
            elif self.format_type == "Fountain":
                self._export_fountain()
            else:
                # For DOCX/PDF, we'd need additional libraries
                self.finished.emit(
                    f"Export format '{self.format_type}' not yet implemented"
                )
                return

            self.progress.emit(100)
            self.finished.emit(f"Successfully exported to {self.output_path}")

        except Exception as e:
            self.finished.emit(f"Export failed: {str(e)}")

    def _export_markdown(self):
        """Export project to Markdown format"""
        content = "# " + self.export_data.get("title", "Untitled Project") + "\n\n"

        for chapter in self.export_data.get("chapters", []):
            content += f"## {chapter.get('title', 'Untitled Chapter')}\n\n"

            for scene in chapter.get("scenes", []):
                scene_title = (
                    scene.get("title", "Untitled Scene")
                    if isinstance(scene, dict)
                    else str(scene)
                )
                scene_content = (
                    scene.get("content", "") if isinstance(scene, dict) else ""
                )

                content += f"### {scene_title}\n\n"
                content += scene_content + "\n\n"

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _export_json(self):
        """Export project to JSON format"""
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.export_data, f, indent=2, ensure_ascii=False)

    def _export_plain_text(self):
        """Export project to plain text format"""
        content = (
            self.export_data.get("title", "Untitled Project") + "\n" + "=" * 50 + "\n\n"
        )

        for chapter in self.export_data.get("chapters", []):
            content += (
                chapter.get("title", "Untitled Chapter") + "\n" + "-" * 30 + "\n\n"
            )

            for scene in chapter.get("scenes", []):
                scene_title = (
                    scene.get("title", "Untitled Scene")
                    if isinstance(scene, dict)
                    else str(scene)
                )
                scene_content = (
                    scene.get("content", "") if isinstance(scene, dict) else ""
                )

                content += scene_title + "\n\n"
                content += scene_content + "\n\n"

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _export_fountain(self):
        """Export project to Fountain screenplay format"""
        content = f"Title: {self.export_data.get('title', 'Untitled Project')}\n\n"

        for chapter in self.export_data.get("chapters", []):
            content += f"# {chapter.get('title', 'Untitled Chapter')}\n\n"

            for scene in chapter.get("scenes", []):
                scene_title = (
                    scene.get("title", "Untitled Scene")
                    if isinstance(scene, dict)
                    else str(scene)
                )
                scene_content = (
                    scene.get("content", "") if isinstance(scene, dict) else ""
                )

                content += f"## {scene_title}\n\n"
                content += scene_content + "\n\n"

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(content)


class ExportDialog(QDialog):
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.export_worker = None
        self.setWindowTitle("Export Project")
        self.setMinimumSize(500, 400)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Project info
        info_group = QGroupBox("Project Information")
        info_layout = QVBoxLayout(info_group)

        project_title = self.project_data.get("title", "Untitled Project")
        chapter_count = len(self.project_data.get("chapters", []))
        scene_count = sum(
            len(ch.get("scenes", [])) for ch in self.project_data.get("chapters", [])
        )

        info_layout.addWidget(QLabel(f"Project: {project_title}"))
        info_layout.addWidget(QLabel(f"Chapters: {chapter_count}"))
        info_layout.addWidget(QLabel(f"Scenes: {scene_count}"))
        layout.addWidget(info_group)

        # Export format selection
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout(format_group)

        self.format_combo = QComboBox()
        self.format_combo.addItems(
            [
                "Markdown (.md)",
                "Plain Text (.txt)",
                "JSON (.json)",
                "Fountain (.fountain)",
                "DOCX (Word Document) - Coming Soon",
                "PDF - Coming Soon",
            ]
        )
        format_layout.addWidget(QLabel("Select export format:"))
        format_layout.addWidget(self.format_combo)
        layout.addWidget(format_group)

        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)

        self.include_annotations = QCheckBox("Include annotations and footnotes")
        self.include_annotations.setChecked(True)

        self.include_metadata = QCheckBox("Include scene metadata")
        self.include_metadata.setChecked(True)

        options_layout.addWidget(self.include_annotations)
        options_layout.addWidget(self.include_metadata)
        layout.addWidget(options_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status display
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setPlaceholderText("Export status will appear here...")
        layout.addWidget(self.status_text)

        # Buttons
        button_layout = QHBoxLayout()

        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self._start_export)

        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self._show_preview)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def _show_preview(self):
        """Show a preview of the export content"""
        format_text = self.format_combo.currentText().split()[0]

        # Generate preview content
        preview = f"Preview for {format_text} export:\n\n"

        if format_text == "Markdown":
            preview += f"# {self.project_data.get('title', 'Untitled')}\n\n"
            for i, chapter in enumerate(
                self.project_data.get("chapters", [])[:2]
            ):  # Show first 2 chapters
                preview += f"## {chapter.get('title', f'Chapter {i+1}')}\n\n"
                for j, scene in enumerate(
                    chapter.get("scenes", [])[:2]
                ):  # Show first 2 scenes
                    scene_title = (
                        scene.get("title", f"Scene {j+1}")
                        if isinstance(scene, dict)
                        else str(scene)
                    )
                    preview += f"### {scene_title}\n\n"
                    if isinstance(scene, dict) and scene.get("content"):
                        preview += scene["content"][:100] + "...\n\n"

        elif format_text == "JSON":
            preview += (
                json.dumps(self.project_data, indent=2, ensure_ascii=False)[:500]
                + "..."
            )

        else:
            preview += f"Preview for {format_text} format would appear here..."

        # Show preview dialog
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("Export Preview")
        preview_dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout(preview_dialog)
        text_edit = QTextEdit()
        text_edit.setPlainText(preview)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(preview_dialog.accept)
        layout.addWidget(close_btn)

        preview_dialog.exec()

    def _start_export(self):
        """Start the export process"""
        format_text = self.format_combo.currentText().split()[0]

        # Check if format is implemented
        if "Coming Soon" in self.format_combo.currentText():
            QMessageBox.information(
                self,
                "Not Implemented",
                f"{format_text} export is not yet implemented. Please choose another format.",
            )
            return

        # Get output file path
        file_filter = self._get_file_filter(format_text)
        default_name = f"{self.project_data.get('title', 'project')}.{self._get_extension(format_text)}"

        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Export As", default_name, file_filter
        )

        if not output_path:
            return

        # Prepare export data
        export_data = dict(self.project_data)
        if not self.include_annotations.isChecked():
            # Remove annotations from export data
            for chapter in export_data.get("chapters", []):
                for scene in chapter.get("scenes", []):
                    if isinstance(scene, dict):
                        scene.pop("annotations", None)
                        scene.pop("footnotes", None)

        # Start export worker
        self.export_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.export_worker = ExportWorker(export_data, format_text, output_path)
        self.export_worker.progress.connect(self.progress_bar.setValue)
        self.export_worker.finished.connect(self._on_export_finished)
        self.export_worker.start()

        self.status_text.append(f"Starting {format_text} export to {output_path}...")

    def _on_export_finished(self, message):
        """Handle export completion"""
        self.export_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_text.append(message)

        if "Successfully" in message:
            QMessageBox.information(self, "Export Complete", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Export Failed", message)

    def _get_file_filter(self, format_type):
        """Get file filter for save dialog"""
        filters = {
            "Markdown": "Markdown Files (*.md)",
            "JSON": "JSON Files (*.json)",
            "Plain": "Text Files (*.txt)",
            "Fountain": "Fountain Files (*.fountain)",
        }
        return filters.get(format_type, "All Files (*)")

    def _get_extension(self, format_type):
        """Get file extension for format"""
        extensions = {
            "Markdown": "md",
            "JSON": "json",
            "Plain": "txt",
            "Fountain": "fountain",
        }
        return extensions.get(format_type, "txt")
