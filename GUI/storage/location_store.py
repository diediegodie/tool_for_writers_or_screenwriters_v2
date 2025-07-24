"""
location_store.py
Modular data model and persistence for Locations.
Follows the pattern of kanban_store.py.
"""

import json
import os
from typing import List, Optional, Dict
from pathlib import Path

LOCATION_FILE = Path(__file__).parent / "locations.json"


class Location:
    def __init__(
        self, id: str, name: str, description: str = "", details: Optional[Dict] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.details = details or {}

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "details": self.details,
        }

    @staticmethod
    def from_dict(data: dict):
        return Location(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            details=data.get("details", {}),
        )


class LocationStore:
    def __init__(self, file_path: Path = LOCATION_FILE):
        self.file_path = file_path
        self.locations: List[Location] = []
        self.load()

    def load(self):
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.locations = [Location.from_dict(l) for l in data]
        else:
            self.locations = []

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(
                [l.to_dict() for l in self.locations], f, indent=2, ensure_ascii=False
            )

    def add(self, location: Location):
        self.locations.append(location)
        self.save()

    def update(self, location: Location):
        for idx, l in enumerate(self.locations):
            if l.id == location.id:
                self.locations[idx] = location
                self.save()
                return True
        return False

    def delete(self, location_id: str):
        self.locations = [l for l in self.locations if l.id != location_id]
        self.save()

    def get(self, location_id: str) -> Optional[Location]:
        for l in self.locations:
            if l.id == location_id:
                return l
        return None

    def list(self) -> List[Location]:
        return self.locations
