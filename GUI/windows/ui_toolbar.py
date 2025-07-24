"""
Toolbar and navigation buttons for Project Editor
"""

from PySide6.QtWidgets import QToolBar, QPushButton
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt


def create_toolbar(editor):
    """
    Create the main toolbar for the Project Editor.
    Includes navigation, formatting, undo, and markdown preview buttons.
    Connects actions to editor methods.
    """
    toolbar = QToolBar()
    btn_undo = QPushButton("Undo")
    btn_undo.setToolTip("Undo last change (Ctrl+Z)")
    # Use _handle_undo if present, else fallback to text_editor.undo
    if hasattr(editor, "_handle_undo"):
        btn_undo.clicked.connect(editor._handle_undo)
    else:
        btn_undo.clicked.connect(editor.text_editor.undo)
    toolbar.addWidget(btn_undo)

    # Navigation actions
    prev_chapter = QAction("Prev Chapter", toolbar)
    next_chapter = QAction("Next Chapter", toolbar)
    prev_scene = QAction("Prev Scene", toolbar)
    next_scene = QAction("Next Scene", toolbar)
    prev_chapter.triggered.connect(getattr(editor, "go_to_prev_chapter", lambda: None))
    next_chapter.triggered.connect(getattr(editor, "go_to_next_chapter", lambda: None))
    prev_scene.triggered.connect(getattr(editor, "go_to_prev_scene", lambda: None))
    next_scene.triggered.connect(getattr(editor, "go_to_next_scene", lambda: None))
    toolbar.addAction(prev_chapter)
    toolbar.addAction(next_chapter)
    toolbar.addSeparator()
    toolbar.addAction(prev_scene)
    toolbar.addAction(next_scene)
    toolbar.addSeparator()

    # Formatting actions
    bold_action = QAction("Bold", toolbar)
    italic_action = QAction("Italic", toolbar)
    underline_action = QAction("Underline", toolbar)
    numbered_list_action = QAction("Numbered List", toolbar)
    bold_action.triggered.connect(editor._toggle_bold)
    italic_action.triggered.connect(editor._toggle_italic)
    underline_action.triggered.connect(editor._toggle_underline)
    numbered_list_action.triggered.connect(
        getattr(editor, "_insert_numbered_list", lambda: None)
    )
    toolbar.addAction(bold_action)
    toolbar.addAction(italic_action)
    toolbar.addAction(underline_action)
    toolbar.addAction(numbered_list_action)
    toolbar.addSeparator()

    # Undo action (persistent)
    undo_action = QAction("Undo", toolbar)
    undo_action.triggered.connect(editor.text_editor.undo)
    toolbar.addAction(undo_action)
    toolbar.addSeparator()

    # Markdown preview toggle
    if hasattr(editor, "toggle_markdown_preview"):
        md_action = QAction("Markdown Preview", toolbar)
        md_action.setCheckable(True)
        md_action.setChecked(getattr(editor, "markdown_preview_enabled", False))
        md_action.toggled.connect(editor.toggle_markdown_preview)
        toolbar.addAction(md_action)

    return toolbar
