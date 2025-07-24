"""
conftest.py: Pytest fixtures for GUI/local storage tests

Fixtures:
- mock_project_setup: Sets up a temporary project with sample data (characters, locations, events)
- temp_json_file: Creates a temporary JSON file for testing
- readonly_file: Creates a file and makes it read-only
- corrupted_json_file: Creates a JSON file with invalid/corrupted content

All fixtures clean up after themselves.
"""

# --- Ensure project root is in sys.path for GUI imports ---
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import json
import tempfile
import shutil
import pytest


@pytest.fixture
def mock_project_setup(tmp_path):
    """Creates a mock project directory with sample character, location, and event JSON files."""
    project_dir = tmp_path / "mock_project"
    project_dir.mkdir()
    # Sample data
    characters = [{"id": 1, "name": "Alice"}]
    locations = [{"id": 1, "name": "Wonderland"}]
    events = [{"id": 1, "title": "Arrival"}]
    # Write files
    (project_dir / "characters.json").write_text(json.dumps(characters))
    (project_dir / "locations.json").write_text(json.dumps(locations))
    (project_dir / "events.json").write_text(json.dumps(events))
    yield project_dir
    # Cleanup handled by tmp_path


@pytest.fixture
def temp_json_file(tmp_path):
    """Creates a temporary JSON file and returns its path."""
    data = {"foo": "bar"}
    file_path = tmp_path / "temp.json"
    file_path.write_text(json.dumps(data))
    yield file_path
    # Cleanup handled by tmp_path


@pytest.fixture
def readonly_file(tmp_path):
    """Creates a file and makes it read-only."""
    file_path = tmp_path / "readonly.json"
    file_path.write_text('{"readonly": true}')
    os.chmod(file_path, 0o444)
    yield file_path
    # Reset permissions so tmp_path can clean up
    os.chmod(file_path, 0o666)


@pytest.fixture
def corrupted_json_file(tmp_path):
    """Creates a JSON file with invalid/corrupted content."""
    file_path = tmp_path / "corrupted.json"
    file_path.write_text("{ this is not valid json }")
    yield file_path
    # Cleanup handled by tmp_path
