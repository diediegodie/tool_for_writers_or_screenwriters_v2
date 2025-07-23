"""
Test suite for PySide6 authentication dialogs (Login, Register, Logout).
Covers: normal, edge, and failure cases as required by project standards.

How to run:
    pytest --qt

# Reason: Ensures all authentication dialogs are robust and user-friendly.
"""

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from GUI.windows.auth_dialogs import LoginDialog, RegisterDialog, LogoutDialog

# --- Pytest fixture to mock QMessageBox for all tests ---
import pytest


@pytest.fixture(autouse=True)
def mock_messagebox(monkeypatch):
    """Mock QMessageBox methods to prevent blocking modal dialogs during tests."""
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)


@pytest.fixture(scope="module")
def app():
    """Ensure a QApplication exists for all tests."""
    app = QApplication.instance() or QApplication([])
    yield app


# --- LoginDialog Tests ---
def test_login_normal_case(qtbot, app):
    dialog = LoginDialog()
    qtbot.addWidget(dialog)
    dialog.username.setText("user")
    dialog.password.setText("pass")
    qtbot.mouseClick(dialog.btn_login, Qt.LeftButton)
    assert dialog.result() == 1  # QDialog.Accepted


def test_login_edge_empty_username(qtbot, app):
    dialog = LoginDialog()
    qtbot.addWidget(dialog)
    dialog.username.setText("")
    dialog.password.setText("pass")
    qtbot.mouseClick(dialog.btn_login, Qt.LeftButton)
    assert dialog.result() == 0  # QDialog.Rejected


def test_login_failure_empty_fields(qtbot, app):
    dialog = LoginDialog()
    qtbot.addWidget(dialog)
    dialog.username.setText("")
    dialog.password.setText("")
    qtbot.mouseClick(dialog.btn_login, Qt.LeftButton)
    assert dialog.result() == 0


# --- RegisterDialog Tests ---
def test_register_normal_case(qtbot, app):
    dialog = RegisterDialog()
    qtbot.addWidget(dialog)
    dialog.username.setText("newuser")
    dialog.password.setText("newpass")
    qtbot.mouseClick(dialog.btn_register, Qt.LeftButton)
    assert dialog.result() == 1


def test_register_edge_empty_username(qtbot, app):
    dialog = RegisterDialog()
    qtbot.addWidget(dialog)
    dialog.username.setText("")
    dialog.password.setText("newpass")
    qtbot.mouseClick(dialog.btn_register, Qt.LeftButton)
    assert dialog.result() == 0


def test_register_failure_empty_fields(qtbot, app):
    dialog = RegisterDialog()
    qtbot.addWidget(dialog)
    dialog.username.setText("")
    dialog.password.setText("")
    qtbot.mouseClick(dialog.btn_register, Qt.LeftButton)
    assert dialog.result() == 0


# --- LogoutDialog Tests ---
def test_logout_normal_case(qtbot, app):
    dialog = LogoutDialog()
    qtbot.addWidget(dialog)
    qtbot.mouseClick(dialog.btn_logout, Qt.LeftButton)
    assert dialog.result() == 1


def test_logout_edge_case_cancel(qtbot, app):
    dialog = LogoutDialog()
    qtbot.addWidget(dialog)
    # Simulate closing the dialog without clicking logout
    dialog.reject()
    assert dialog.result() == 0


# Reason: Each dialog is tested for normal, edge, and failure cases as per project standards.
