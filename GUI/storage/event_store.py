"""
event_store.py
Modular data model and persistence for Events.
Follows the pattern of kanban_store.py.
"""

import json
import os
from typing import List, Optional, Dict
from pathlib import Path

EVENT_FILE = Path(__file__).parent / "events.json"


class Event:
    def __init__(
        self,
        id: str,
        title: str,
        description: str = "",
        metadata: Optional[Dict] = None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data: dict):
        return Event(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )


class EventStore:
    def __init__(self, file_path: Path = EVENT_FILE):
        self.file_path = file_path
        self.events: List[Event] = []
        self.load()

    def load(self):
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.events = [Event.from_dict(e) for e in data]
        else:
            self.events = []

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(
                [e.to_dict() for e in self.events], f, indent=2, ensure_ascii=False
            )

    def add(self, event: Event):
        self.events.append(event)
        self.save()

    def update(self, event: Event):
        for idx, e in enumerate(self.events):
            if e.id == event.id:
                self.events[idx] = event
                self.save()
                return True
        return False

    def delete(self, event_id: str):
        self.events = [e for e in self.events if e.id != event_id]
        self.save()

    def get(self, event_id: str) -> Optional[Event]:
        for e in self.events:
            if e.id == event_id:
                return e
        return None

    def list(self) -> List[Event]:
        return self.events
