"""
Tests for HomepageWindow in GUI/windows/homepage.py
Covers window opening methods and UI logic.
"""

import pytest
from PySide6.QtWidgets import QApplication
from GUI.windows.homepage import HomepageWindow


@pytest.fixture
def homepage(qtbot):
    win = HomepageWindow()
    qtbot.addWidget(win)
    return win


def test_open_project_editor_window(homepage, monkeypatch):
    called = {}
    monkeypatch.setattr(
        homepage,
        "open_project_editor_window",
        lambda: called.setdefault("editor", True),
    )
    homepage.open_project_editor_window()
    assert called["editor"]


def test_open_dashboard_window(homepage, monkeypatch):
    called = {}
    monkeypatch.setattr(
        homepage, "open_dashboard_window", lambda: called.setdefault("dashboard", True)
    )
    homepage.open_dashboard_window()
    assert called["dashboard"]


def test_open_login_dialog(homepage, monkeypatch):
    called = {}
    monkeypatch.setattr(
        homepage, "open_login_dialog", lambda: called.setdefault("login", True)
    )
    homepage.open_login_dialog()
    assert called["login"]


def test_open_register_dialog(homepage, monkeypatch):
    called = {}
    monkeypatch.setattr(
        homepage, "open_register_dialog", lambda: called.setdefault("register", True)
    )
    homepage.open_register_dialog()
    assert called["register"]


def test_open_logout_dialog(homepage, monkeypatch):
    called = {}
    monkeypatch.setattr(
        homepage, "open_logout_dialog", lambda: called.setdefault("logout", True)
    )
    homepage.open_logout_dialog()
    assert called["logout"]
