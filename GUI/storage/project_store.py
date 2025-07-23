import json
import os

PROJECTS_FILE = os.path.join(os.path.dirname(__file__), "projects.json")


def load_projects():
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_projects(projects):
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)


# Reason: Simple JSON-based persistence for project names. Replace with DB in production.
