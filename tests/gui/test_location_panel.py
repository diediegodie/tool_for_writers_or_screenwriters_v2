"""
NOTE: Always run this test via the project root's run_all_tests.sh script.
Do NOT run pytest directly. See docs/TESTING_STANDARD.md for details.
"""

"""
test_location_panel.py
Unit, edge, and failure case tests for LocationPanel and LocationStore.
"""

import pytest
from GUI.storage.location_store import LocationStore, Location
import uuid
import os
from pathlib import Path


def temp_store():
    path = Path("/tmp/test_locations.json")
    if path.exists():
        os.remove(path)
    return LocationStore(file_path=path)


def test_add_location():
    store = temp_store()
    loc = Location(id=str(uuid.uuid4()), name="Paris", description="City of Light")
    store.add(loc)
    assert len(store.list()) == 1
    assert store.list()[0].name == "Paris"


def test_edit_location():
    store = temp_store()
    loc = Location(id=str(uuid.uuid4()), name="London", description="")
    store.add(loc)
    loc.name = "Londinium"
    loc.description = "Ancient city"
    store.update(loc)
    assert store.list()[0].name == "Londinium"
    assert store.list()[0].description == "Ancient city"


def test_delete_location():
    store = temp_store()
    loc = Location(id=str(uuid.uuid4()), name="Berlin")
    store.add(loc)
    store.delete(loc.id)
    assert len(store.list()) == 0


def test_edge_empty_name():
    store = temp_store()
    loc = Location(id=str(uuid.uuid4()), name="", description="No name")
    store.add(loc)
    assert store.list()[0].name == ""


def test_failure_update_nonexistent():
    store = temp_store()
    loc = Location(id="notfound", name="Nowhere")
    result = store.update(loc)
    assert result is False
