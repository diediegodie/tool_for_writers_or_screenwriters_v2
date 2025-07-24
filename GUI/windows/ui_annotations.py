"""
Annotations panel logic for Project Editor
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QFrame


def create_annotations_panel(editor):
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.addWidget(QLabel("Annotations & Footnotes"))
    annotation_list = QListWidget()
    annotation_list.setFrameShape(QFrame.StyledPanel)

    # Populate the annotation list from the current scene/chapter
    def update_annotations():
        annotation_list.clear()
        # Assume editor.get_current_annotations() returns a list of dicts with 'text' and 'type'
        annotations = getattr(editor, "get_current_annotations", lambda: [])()
        if not annotations:
            annotation_list.addItem("No annotations or footnotes.")
            annotation_list.setEnabled(False)
        else:
            annotation_list.setEnabled(True)
            for ann in annotations:
                label = f"[{ann.get('type', 'Note')}] {ann.get('text', '')[:40]}"
                annotation_list.addItem(label)

    # Show annotation details when selected
    def on_annotation_selected():
        idx = annotation_list.currentRow()
        annotations = getattr(editor, "get_current_annotations", lambda: [])()
        if 0 <= idx < len(annotations):
            ann = annotations[idx]
            # Assume editor.show_annotation_details exists
            if hasattr(editor, "show_annotation_details"):
                editor.show_annotation_details(ann)

    annotation_list.currentRowChanged.connect(on_annotation_selected)

    # Expose update_annotations for external calls (e.g., when scene changes)
    right_panel.update_annotations = update_annotations

    right_layout.addWidget(annotation_list, 1)
    return right_panel, annotation_list
