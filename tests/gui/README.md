# GUI Tests – Authentication Dialogs

This folder contains tests for PySide6 authentication dialogs (Login, Register, Logout) as required by project standards.

## How to Run

1. Make sure you have pytest and pytest-qt installed:
   ```bash
   pip install pytest pytest-qt
   ```
2. Run all GUI tests:
   ```bash
   pytest --qt tests/gui/
   ```

## Test Coverage
- **LoginDialog**: normal, edge, and failure cases
- **RegisterDialog**: normal, edge, and failure cases
- **LogoutDialog**: normal and edge cases

## Test Philosophy
- Each dialog is tested for normal, edge, and failure cases as per `/docs/TESTING_STANDARD.md` and `/docs/TASK.md`.
- All tests are isolated and do not require a running backend.
- Mock logic is used for authentication (no real JWT or DB required).

# Reason: Ensures all contributors and LLMs understand the test structure, coverage, and execution for GUI authentication dialogs.
