"""
Annotation and Footnote logic for Project Editor
- Modularized from project_editor.py
"""

from PySide6.QtWidgets import QMessageBox, QInputDialog
from PySide6.QtCore import Qt


def add_footnote(
    parent, text_editor, chapter_list, scene_list, chapters, refresh_callback
):
    cursor = text_editor.textCursor()
    if not cursor.hasSelection():
        QMessageBox.information(
            parent, "No Selection", "Select text to add a footnote."
        )
        return
    text = cursor.selectedText()
    note, ok = QInputDialog.getText(parent, "Add Footnote", f"Footnote for: '{text}'")
    if not ok or not note:
        return
    fmt = cursor.charFormat()
    fmt.setBackground(Qt.cyan)
    cursor.mergeCharFormat(fmt)
    text_editor.setTextCursor(cursor)
    cidx = chapter_list.currentRow()
    sidx = scene_list.currentRow()
    if cidx >= 0 and sidx >= 0 and cidx < len(chapters):
        scenes = chapters[cidx]["scenes"]
        if sidx < len(scenes):
            scene = scenes[sidx]
            if "footnotes" not in scene:
                scene["footnotes"] = []
            scene["footnotes"].append(
                {
                    "text": text,
                    "note": note,
                    "start": cursor.selectionStart(),
                    "end": cursor.selectionEnd(),
                }
            )
            refresh_callback()


def add_annotation(
    parent, text_editor, chapter_list, scene_list, chapters, refresh_callback
):
    cursor = text_editor.textCursor()
    if not cursor.hasSelection():
        QMessageBox.information(parent, "No Selection", "Select text to annotate.")
        return
    text = cursor.selectedText()
    note, ok = QInputDialog.getText(
        parent, "Add Annotation", f"Annotation for: '{text}'"
    )
    if not ok or not note:
        return
    fmt = cursor.charFormat()
    fmt.setBackground(Qt.yellow)
    cursor.mergeCharFormat(fmt)
    text_editor.setTextCursor(cursor)
    cidx = chapter_list.currentRow()
    sidx = scene_list.currentRow()
    if cidx >= 0 and sidx >= 0 and cidx < len(chapters):
        scenes = chapters[cidx]["scenes"]
        if sidx < len(scenes):
            scene = scenes[sidx]
            if "annotations" not in scene:
                scene["annotations"] = []
            scene["annotations"].append(
                {
                    "text": text,
                    "note": note,
                    "start": cursor.selectionStart(),
                    "end": cursor.selectionEnd(),
                }
            )
            refresh_callback()


def refresh_annotation_list(annotation_list, chapter_list, scene_list, chapters):
    annotation_list.clear()
    cidx = chapter_list.currentRow()
    sidx = scene_list.currentRow()
    if cidx >= 0 and sidx >= 0 and cidx < len(chapters):
        scenes = chapters[cidx]["scenes"]
        if sidx < len(scenes):
            scene = scenes[sidx]
            for ann in scene.get("annotations", []):
                annotation_list.addItem(f"[A] {ann['text']}: {ann['note']}")
            for fn in scene.get("footnotes", []):
                annotation_list.addItem(f"[F] {fn['text']}: {fn['note']}")


def on_annotation_clicked(
    parent, annotation_list, text_editor, chapter_list, scene_list, chapters
):
    cidx = chapter_list.currentRow()
    sidx = scene_list.currentRow()
    if cidx >= 0 and sidx >= 0 and cidx < len(chapters):
        scenes = chapters[cidx]["scenes"]
        if sidx < len(scenes):
            scene = scenes[sidx]
            idx = annotation_list.currentRow()
            ann_list = scene.get("annotations", [])
            fn_list = scene.get("footnotes", [])
            total = len(ann_list) + len(fn_list)
            if 0 <= idx < total:
                if idx < len(ann_list):
                    ann = ann_list[idx]
                    start, end = ann["start"], ann["end"]
                else:
                    fn = fn_list[idx - len(ann_list)]
                    start, end = fn["start"], fn["end"]
                cursor = text_editor.textCursor()
                from PySide6.QtGui import QTextCursor

                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                text_editor.setTextCursor(cursor)
