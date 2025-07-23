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


# --- Normal case: create project ---
def test_create_project_normal(qtbot, app, monkeypatch):
    win = DashboardWindow()
    qtbot.addWidget(win)
    monkeypatch.setattr(
        "PySide6.QtWidgets.QInputDialog.getText", lambda *a, **k: ("Project X", True)
    )
    win.create_project()
    assert "Project X" in win.projects


# --- Edge case: create project with empty name ---
def test_create_project_empty_name(qtbot, app, monkeypatch):
    win = DashboardWindow()
    qtbot.addWidget(win)
    monkeypatch.setattr(
        "PySide6.QtWidgets.QInputDialog.getText", lambda *a, **k: ("", True)
    )
    win.create_project()
    assert "" not in win.projects


# --- Normal case: delete project ---
def test_delete_project_normal(qtbot, app, monkeypatch):
    win = DashboardWindow()
    qtbot.addWidget(win)
    win.projects.append("ToDelete")
    win.list_widget.addItem("ToDelete")
    win.list_widget.setCurrentRow(win.list_widget.count() - 1)
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)
    win.delete_project()
    assert "ToDelete" not in win.projects


# --- Edge case: delete with no selection ---
def test_delete_project_no_selection(qtbot, app):
    win = DashboardWindow()
    qtbot.addWidget(win)
    win.list_widget.setCurrentRow(-1)
    win.delete_project()  # Should not raise
    assert True


# --- Normal case: rename project ---
def test_rename_project_normal(qtbot, app, monkeypatch):
    win = DashboardWindow()
    qtbot.addWidget(win)
    win.projects.append("OldName")
    win.list_widget.addItem("OldName")
    win.list_widget.setCurrentRow(win.list_widget.count() - 1)
    monkeypatch.setattr(
        "PySide6.QtWidgets.QInputDialog.getText", lambda *a, **k: ("NewName", True)
    )
    win.rename_project()
    assert "NewName" in win.projects


# --- Edge case: rename with no selection ---
def test_rename_project_no_selection(qtbot, app):
    win = DashboardWindow()
    qtbot.addWidget(win)
    win.list_widget.setCurrentRow(-1)
    win.rename_project()  # Should not raise
    assert True


# --- Failure case: rename to empty name ---
def test_rename_project_empty_name(qtbot, app, monkeypatch):
    win = DashboardWindow()
    qtbot.addWidget(win)
    win.projects.append("OldName")
    win.list_widget.addItem("OldName")
    win.list_widget.setCurrentRow(win.list_widget.count() - 1)
    monkeypatch.setattr(
        "PySide6.QtWidgets.QInputDialog.getText", lambda *a, **k: ("", True)
    )
    win.rename_project()
    assert "" not in win.projects


# Reason: Each function is tested for normal, edge, and failure cases as per project standards.
