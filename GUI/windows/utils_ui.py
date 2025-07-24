"""
Helper functions and small reusable UI elements for Project Editor
"""

from PySide6.QtWidgets import QListWidget, QTextEdit, QListWidgetItem


def refresh_annotation_list(annotation_list, chapter_list, scene_list, chapters):
    """
    Refresh the annotation/footnote list for the current scene.
    """
    annotation_list.clear()
    cidx = chapter_list.currentRow()
    sidx = scene_list.currentRow()
    if cidx < 0 or sidx < 0 or cidx >= len(chapters):
        annotation_list.addItem("(No annotations or footnotes)")
        return
    scenes = chapters[cidx]["scenes"]
    if sidx >= len(scenes):
        annotation_list.addItem("(No annotations or footnotes)")
        return
    scene = scenes[sidx]
    ann = scene.get("annotations", []) if isinstance(scene, dict) else []
    fn = scene.get("footnotes", []) if isinstance(scene, dict) else []
    if not ann and not fn:
        annotation_list.addItem("(No annotations or footnotes)")
        return
    for a in ann:
        annotation_list.addItem(f"[Annotation] {a[:40]}")
    for f in fn:
        annotation_list.addItem(f"[Footnote] {f[:40]}")


def on_annotation_clicked(
    editor, annotation_list, text_editor, chapter_list, scene_list, chapters
):
    """
    Show annotation/footnote details when clicked in the list.
    """
    idx = annotation_list.currentRow()
    cidx = chapter_list.currentRow()
    sidx = scene_list.currentRow()
    if cidx < 0 or sidx < 0 or cidx >= len(chapters):
        return
    scenes = chapters[cidx]["scenes"]
    if sidx >= len(scenes):
        return
    scene = scenes[sidx]
    ann = scene.get("annotations", []) if isinstance(scene, dict) else []
    fn = scene.get("footnotes", []) if isinstance(scene, dict) else []
    total = len(ann) + len(fn)
    if idx < 0 or idx >= total:
        return
    if idx < len(ann):
        text = ann[idx]
        # Show annotation details (could be a dialog or status bar)
        if hasattr(editor, "show_annotation_details"):
            editor.show_annotation_details({"type": "annotation", "text": text})
    else:
        text = fn[idx - len(ann)]
        if hasattr(editor, "show_annotation_details"):
            editor.show_annotation_details({"type": "footnote", "text": text})
