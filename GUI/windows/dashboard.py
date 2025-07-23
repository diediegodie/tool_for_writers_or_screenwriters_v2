from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QHBoxLayout,
    QInputDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt
from GUI.storage.project_store import load_projects, save_projects


class DashboardWindow(QMainWindow):
    """
    Dashboard window for listing, creating, deleting, and renaming projects.
    # Reason: Central hub for project management in the app.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard – Projects")
        self.setMinimumSize(500, 400)
        self.projects = load_projects() or ["My First Project"]
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()
        title = QLabel("Your Projects")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.projects)
        layout.addWidget(title)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        btn_create = QPushButton("Create Project")
        btn_delete = QPushButton("Delete Project")
        btn_rename = QPushButton("Rename Project")
        btn_create.clicked.connect(self.create_project)
        btn_delete.clicked.connect(self.delete_project)
        btn_rename.clicked.connect(self.rename_project)
        btn_layout.addWidget(btn_create)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_rename)
        layout.addLayout(btn_layout)

        btn_project_editor = QPushButton("Open Project Editor")
        btn_project_editor.clicked.connect(self.open_project_editor_window)
        layout.addWidget(btn_project_editor)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def open_project_editor_window(self):
        from GUI.windows.project_editor import ProjectEditorWindow

        self.project_editor = ProjectEditorWindow(self)
        self.project_editor.show()

    def create_project(self):
        name, ok = QInputDialog.getText(self, "Create Project", "Project name:")
        if ok and name:
            self.projects.append(name)
            self.list_widget.addItem(name)
            save_projects(self.projects)

    def delete_project(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            name = self.list_widget.item(row).text()
            reply = QMessageBox.question(
                self,
                "Delete Project",
                f"Delete '{name}'?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.projects.pop(row)
                self.list_widget.takeItem(row)
                save_projects(self.projects)

    def rename_project(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            old_name = self.list_widget.item(row).text()
            name, ok = QInputDialog.getText(
                self, "Rename Project", "New name:", text=old_name
            )
            if ok and name:
                self.projects[row] = name
                self.list_widget.item(row).setText(name)
                save_projects(self.projects)


# Reason: This window is the main entry for project management and navigation.
