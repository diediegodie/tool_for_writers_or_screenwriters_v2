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
