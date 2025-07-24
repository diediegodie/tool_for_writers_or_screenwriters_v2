"""
NOTE: Always run this test via the project root's run_all_tests.sh script.
Do NOT run pytest directly. See docs/TESTING_STANDARD.md for details.
"""

"""
test_character_panel.py
Unit, edge, and failure case tests for CharacterPanel and CharacterStore.
"""

import pytest
from GUI.storage.character_store import CharacterStore, Character
import uuid
import os
from pathlib import Path


def temp_store():
    # Use a temp file for testing
    path = Path("/tmp/test_characters.json")
    if path.exists():
        os.remove(path)
    return CharacterStore(file_path=path)


def test_add_character():
    store = temp_store()
    char = Character(id=str(uuid.uuid4()), name="Alice", description="Protagonist")
    store.add(char)
    assert len(store.list()) == 1
    assert store.list()[0].name == "Alice"


def test_edit_character():
    store = temp_store()
    char = Character(id=str(uuid.uuid4()), name="Bob", description="")
    store.add(char)
    char.name = "Bobby"
    char.description = "Sidekick"
    store.update(char)
    assert store.list()[0].name == "Bobby"
    assert store.list()[0].description == "Sidekick"


def test_delete_character():
    store = temp_store()
    char = Character(id=str(uuid.uuid4()), name="Charlie")
    store.add(char)
    store.delete(char.id)
    assert len(store.list()) == 0


def test_edge_empty_name():
    store = temp_store()
    char = Character(id=str(uuid.uuid4()), name="", description="No name")
    store.add(char)
    assert store.list()[0].name == ""


def test_failure_update_nonexistent():
    store = temp_store()
    char = Character(id="notfound", name="Ghost")
    result = store.update(char)
    assert result is False
