"""
NOTE: Always run this test via the project root's run_all_tests.sh script.
Do NOT run pytest directly. See docs/TESTING_STANDARD.md for details.
"""

"""
test_event_panel.py
Unit, edge, and failure case tests for EventPanel and EventStore.
"""

import pytest
from GUI.storage.event_store import EventStore, Event
import uuid
import os
from pathlib import Path


def temp_store():
    path = Path("/tmp/test_events.json")
    if path.exists():
        os.remove(path)
    return EventStore(file_path=path)


def test_add_event():
    store = temp_store()
    event = Event(id=str(uuid.uuid4()), title="Battle", description="Epic fight")
    store.add(event)
    assert len(store.list()) == 1
    assert store.list()[0].title == "Battle"


def test_edit_event():
    store = temp_store()
    event = Event(id=str(uuid.uuid4()), title="Meeting", description="")
    store.add(event)
    event.title = "Secret Meeting"
    event.description = "Plot twist"
    store.update(event)
    assert store.list()[0].title == "Secret Meeting"
    assert store.list()[0].description == "Plot twist"


def test_delete_event():
    store = temp_store()
    event = Event(id=str(uuid.uuid4()), title="Coronation")
    store.add(event)
    store.delete(event.id)
    assert len(store.list()) == 0


def test_edge_empty_title():
    store = temp_store()
    event = Event(id=str(uuid.uuid4()), title="", description="No title")
    store.add(event)
    assert store.list()[0].title == ""


def test_failure_update_nonexistent():
    store = temp_store()
    event = Event(id="notfound", title="Ghost Event")
    result = store.update(event)
    assert result is False
