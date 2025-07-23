"""
Smoke test for GUI/main.py main() entry point.
This test is separated from GUI tests to avoid QApplication conflicts.
"""

import pytest
import sys
from PySide6.QtWidgets import QApplication

pytestmark = pytest.mark.smoke


def test_main_runs(monkeypatch):
    # Import main and patch QApplication to prevent full event loop
    import GUI.main as gui_main

    called = {}

    class DummyApp(QApplication):
        def exec(self):
            called["ran"] = True
            return 0

    monkeypatch.setattr(gui_main, "QApplication", DummyApp)
    import pytest

    with pytest.raises(SystemExit) as excinfo:
        gui_main.main()
    assert excinfo.value.code == 0
    assert called.get("ran")
