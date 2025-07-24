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
  - All tests must be run via the `run_all_tests.sh` script at the project root. This is the single source of truth for running all test suites (GUI, backend, etc).
  - See `docs/TESTING_STANDARD.md` for details and rationale.

**Note:** These changes are critical for onboarding and future contributors to understand the current codebase structure and testing requirements.