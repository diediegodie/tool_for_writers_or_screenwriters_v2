# Writer & Screenwriter Assistant

## 🚧 In Construction

### Project Goals
- Build a full-stack writing assistant for writers, screenwriters, and content creators.
- Support rich text editing, story structuring, offline usage, and multiple export formats.
- Ensure user-friendliness for workflows like novel writing, scriptwriting, academic writing, and technical documentation.

### Architecture Overview
#### Frontend
- **Framework**: React with Vite.
- **Rich Text Editor**: Slate.js.
- **State Management**: React Context and React Query.
- **Offline Storage**: IndexedDB.
- **Styling**: TailwindCSS.
- **Routing**: React Router v6.
- **Testing**: Jest, React Testing Library, and Playwright.

#### Backend
- **Language**: Python.
- **Framework**: FastAPI.
- **Database**: MongoDB with Motor or Beanie ODM.
- **Authentication**: JWT-based.
- **Export Formats**: DOCX, PDF, Markdown, Fountain.
- **Testing**: Pytest.
- **Containerization**: Docker.

#### Infrastructure
- **CI/CD**: GitHub Actions.
- **Deployment**: Fly.io, Render, or Railway.
- **Environment Management**: `.env` files.
