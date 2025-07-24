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
        self.list_widget.addItems(
            [
                p["title"] if isinstance(p, dict) and "title" in p else str(p)
                for p in self.projects
            ]
        )
        layout.addWidget(title)
        layout.addWidget(self.list_widget)

        # Double-click to open project
        self.list_widget.itemDoubleClicked.connect(self.open_selected_project)

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
        btn_project_editor.clicked.connect(self.open_selected_project)
        layout.addWidget(btn_project_editor)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def open_selected_project(self, *args):
        """Open the Project Editor for the currently selected project."""
        from GUI.windows.project_editor_window import ProjectEditorWindow

        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.projects):
            QMessageBox.warning(
                self, "Open Project", "Please select a project to open."
            )
            return
        project = self.projects[row]
        self.project_editor = ProjectEditorWindow(self, project=project)
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
            print(f"Attempting to delete project: {name}")  # Debugging output
            print(
                f"Current projects before deletion: {self.projects}"
            )  # Debugging output
            titles_before = [
                proj.get("title", "") if isinstance(proj, dict) else str(proj)
                for proj in self.projects
            ]
            print(f"Project titles before deletion: {titles_before}")
            reply = QMessageBox.question(
                self,
                "Delete Project",
                f"Delete '{name}'?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:

                def remove_matching_projects(projects, target):
                    # Recursively remove any dict with title==target or str==target
                    result = []
                    for proj in projects:
                        if isinstance(proj, dict):
                            if proj.get("title", None) == target:
                                continue
                            # Recursively clean nested lists in dict values
                            cleaned = {
                                k: (
                                    remove_matching_projects(v, target)
                                    if isinstance(v, list)
                                    else v
                                )
                                for k, v in proj.items()
                            }
                            result.append(cleaned)
                        elif isinstance(proj, list):
                            # Should not happen at top-level, but handle just in case
                            cleaned = remove_matching_projects(proj, target)
                            result.append(cleaned)
                        elif isinstance(proj, str):
                            if proj == target:
                                continue
                            result.append(proj)
                        else:
                            result.append(proj)
                    return result

                self.projects = remove_matching_projects(self.projects, name)
                # Remove all matching items from the list widget
                i = 0
                while i < self.list_widget.count():
                    item = self.list_widget.item(i)
                    if item.text() == name:
                        self.list_widget.takeItem(i)
                    else:
                        i += 1
                save_projects(self.projects)
                print(f"Deleted project: {name}")  # Debugging output
                print(f"Projects after deletion: {self.projects}")  # Debugging output
                titles_after = [
                    proj.get("title", "") if isinstance(proj, dict) else str(proj)
                    for proj in self.projects
                ]
                print(f"Project titles after deletion: {titles_after}")
            else:
                print(f"Deletion cancelled for project: {name}")  # Debugging output

    def rename_project(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            old_name = self.list_widget.item(row).text()
            print(f"Attempting to rename project: {old_name}")  # Debugging output
            print(
                f"Current projects before renaming: {self.projects}"
            )  # Debugging output
            name, ok = QInputDialog.getText(
                self, "Rename Project", "New name:", text=old_name
            )
            # If user cancels or provides empty/whitespace, do not proceed
            if not ok or not name or not name.strip():
                if not ok:
                    print(f"Rename cancelled by user.")
                else:
                    QMessageBox.warning(
                        self,
                        "Rename Project",
                        "Project name cannot be empty or whitespace.",
                    )
                    print(f"Rename failed: Empty or whitespace name provided.")
                return
            name = name.strip()
            if any(
                (
                    proj.get("title", "") == name
                    if isinstance(proj, dict)
                    else proj == name
                )
                for proj in self.projects
            ):
                QMessageBox.warning(
                    self,
                    "Rename Project",
                    f"A project with the name '{name}' already exists.",
                )
                print(f"Rename failed: Duplicate name '{name}'")
                return
            # Update the project title
            renamed = False
            for proj in self.projects:
                if isinstance(proj, dict) and proj.get("title", "") == old_name:
                    proj["title"] = name
                    renamed = True
                    break
                elif isinstance(proj, str) and proj == old_name:
                    idx = self.projects.index(proj)
                    self.projects[idx] = name
                    renamed = True
                    break
            if renamed:
                self.list_widget.item(row).setText(name)
                save_projects(self.projects)
                print(f"Renamed project: {old_name} to {name}")
            else:
                print(f"Rename failed: Project '{old_name}' not found.")


# Reason: This window is the main entry for project management and navigation.
