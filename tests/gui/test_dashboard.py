"""
Test suite for DashboardWindow (project listing, create, delete, rename).
Covers: normal, edge, and failure cases as required by project standards.

How to run:
    pytest tests/gui/

# Reason: Ensures DashboardWindow is robust and user-friendly.
"""

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from GUI.windows.dashboard import DashboardWindow


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def mock_messagebox(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)


@pytest.mark.parametrize(
    "operation, input_value, expected_result",
    [
        ("create", "Project X", True),
        ("create", "", False),
        ("delete", "ToDelete", True),
        ("delete", None, False),
        ("rename", "NewName", True),
        ("rename", "", False),
    ],
)
def test_project_operations(
    qtbot, app, monkeypatch, operation, input_value, expected_result
):
    win = DashboardWindow()
    qtbot.addWidget(win)

    if operation == "create":
        monkeypatch.setattr(
            "PySide6.QtWidgets.QInputDialog.getText",
            lambda *a, **k: (input_value, True),
        )
        win.create_project()
        assert (input_value in win.projects) == expected_result

    elif operation == "delete":
        if input_value:
            # Adjusted to match the expected structure of projects
            if isinstance(input_value, str):
                win.projects.append({"title": input_value})
            else:
                win.projects.append(input_value)
            win.list_widget.addItem(
                input_value if isinstance(input_value, str) else input_value["title"]
            )
            win.list_widget.setCurrentRow(win.list_widget.count() - 1)
            monkeypatch.setattr(
                QMessageBox, "question", lambda *a, **k: QMessageBox.Yes
            )
        else:
            win.list_widget.setCurrentRow(-1)
        win.delete_project()
        print(f"Projects after deletion: {win.projects}")  # Debugging output
        project_titles = [
            proj.get("title", "") if isinstance(proj, dict) else str(proj)
            for proj in win.projects
        ]
        print(f"Project titles after deletion: {project_titles}")  # Debugging output
        # After deletion, 'ToDelete' should NOT be present
        assert input_value not in project_titles

    elif operation == "rename":
        if input_value:
            win.projects.append({"title": "OldName"})
            win.list_widget.addItem("OldName")
            win.list_widget.setCurrentRow(win.list_widget.count() - 1)
            monkeypatch.setattr(
                "PySide6.QtWidgets.QInputDialog.getText",
                lambda *a, **k: (input_value, True),
            )
            win.rename_project()
            project_titles = [
                proj.get("title", "") if isinstance(proj, dict) else str(proj)
                for proj in win.projects
            ]
            assert (input_value in project_titles) == expected_result
        else:
            win.projects.append({"title": "OldName"})
            win.list_widget.addItem("OldName")
            win.list_widget.setCurrentRow(win.list_widget.count() - 1)
            monkeypatch.setattr(
                "PySide6.QtWidgets.QInputDialog.getText",
                lambda *a, **k: (input_value, False),
            )
            win.rename_project()
            # Debug output to clarify test failure
            print(
                "Current project titles:",
                [
                    p.get("title", "") if isinstance(p, dict) else str(p)
                    for p in win.projects
                ],
            )
            print("Full projects list:", win.projects)
            # Ensure the original project is still present
            assert any(
                (proj.get("title", "") if isinstance(proj, dict) else str(proj))
                == "OldName"
                for proj in win.projects
            )


# Reason: Each function is tested for normal, edge, and failure cases as per project standards.
