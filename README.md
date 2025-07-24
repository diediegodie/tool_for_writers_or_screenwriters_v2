# Writer & Screenwriter Assistant

## 🚧 In Construction

### Project Goals
- Build a full-stack writing assistant for writers, screenwriters, and content creators.
- Support rich text editing, story structuring, offline usage, and multiple export formats.
- Ensure user-friendliness for workflows like novel writing, scriptwriting, academic writing, and technical documentation.

### Architecture Overview

#### GUI (Desktop)
- **Framework**: PySide6 (Qt for Python)
- **Rich Text Editor**: QTextEdit-based, with formatting, annotations, and custom blocks
- **State Management**: Python classes, signals/slots
- **Offline Storage**: Local file system (JSON) and/or SQLite
- **Styling**: Qt Stylesheets and built-in theming
- **Navigation**: Stacked widgets, dialogs, and menus
- **Testing**: pytest-qt (unit/integration), see `run_all_tests.sh`


#### Backend
- **Language**: Python
- **Framework**: FastAPI
- **Database**: MongoDB with Motor or Beanie ODM
- **Authentication**: JWT-based
- **Export Formats**: DOCX, PDF, Markdown, Fountain
- **Testing**: Pytest (unit/integration)
- **Containerization**: Docker


#### Infrastructure & Testing
- **CI/CD**: GitHub Actions
- **Deployment**: Fly.io, Render, or Railway
- **Environment Management**: `.env` files
- **Unified Testing**: All tests (GUI, backend, future E2E) are run via `./run_all_tests.sh` for consistency and maintainability.

---

## 📝 Recent Architecture Changes (2025-07-24)

- **Kanban Board Refactor:**
  - The original `kanban_board.py` (>700 lines) was split into:
    - `kanban_board.py`: Core UI/event logic for the Kanban board widget.
    - `kanban_board2.py`: Helper classes and functions (e.g., `KanbanCard`, `Column`, dialog logic, conversion helpers).
  - Each file is now <500 lines for maintainability.
  - All imports and references were updated to match the new structure.
  - The Kanban-to-Timeline conversion test was fixed for headless/Wayland environments by calling the context menu handler with `pos=None`.
  - All Kanban board and integration tests pass (except expected xfail).

- **Testing Policy:**

  - **All tests must be run via the `run_all_tests.sh` script at the project root.**
    - Never run `pytest` directly. This script is the only supported way to run all test suites (GUI, backend, smoke, etc).
    - The script sets up the correct environment and runs tests in the correct order, handling PySide6 QApplication singleton issues and import paths.
    - See `docs/TESTING_STANDARD.md` for details and rationale.
    - If you add new tests or test types, update both this README and the script.

**Note:** These changes are critical for onboarding and future contributors to understand the current codebase structure and testing requirements.

---

## 🟦 Kanban <-> Timeline/Storyboard Sync & Conversion

- **Convert & Sync:**
  - Kanban cards can be converted to timeline/storyboard cards via the UI or programmatically.
  - All relevant fields (title, notes, tags, color, links, id) are copied and mapped.
  - Sync utilities ensure that updates, deletions, and renames are reflected in both views.
  - Duplicate prevention: Only one timeline card per Kanban card (by id).
  - Deletion/rename handling: Timeline cards are removed if the Kanban card is deleted or renamed.
  - Two-way sync: Timeline cards can also be synced back to Kanban columns.
  - All sync/convert logic is modular, fully tested, and documented.

- **Persistence:**
  - Timeline/storyboard state is saved to and loaded from JSON via `timeline_store.py`.
  - Kanban board state is saved via `kanban_store.py`.
  - All mappings are id-based for robust updates.

- **Testing:**
  - Unit, edge, integration, and UI tests cover all sync/convert scenarios.
  - See `tests/gui/test_kanban_timeline_full.py` and related files for examples.

- **Accessibility:**
  - All columns, lists, and cards have accessible names and descriptions for screen readers.
  - See `docs/accessibility.md` for details.