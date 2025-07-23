# Backend (FastAPI + MongoDB)

## Structure
- `app/main.py`: FastAPI entrypoint
- `app/core/config.py`: Settings and environment
- `app/db/`: Database connection and Beanie ODM init
- `app/features/`: Feature modules (projects, scenes, auth, etc.)
- `requirements.txt`: Python dependencies

## Quickstart
1. Install requirements:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Run the server:
   ```bash
   uvicorn backend.app.main:app --reload
   ```

## Testing
- Place all backend tests in `tests/backend/`
- Use `pytest` to run tests:
   ```bash
   pytest tests/backend/
   ```
