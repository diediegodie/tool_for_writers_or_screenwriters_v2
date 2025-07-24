"""
character_store.py
Modular data model and persistence for Characters.
Follows the pattern of kanban_store.py.
"""

import json
import os
from typing import List, Optional, Dict
from pathlib import Path

CHARACTER_FILE = Path(__file__).parent / "characters.json"


class Character:
    def __init__(
        self, id: str, name: str, description: str = "", traits: Optional[Dict] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.traits = traits or {}

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "traits": self.traits,
        }

    @staticmethod
    def from_dict(data: dict):
        return Character(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            traits=data.get("traits", {}),
        )


class CharacterStore:
    def __init__(self, file_path: Path = CHARACTER_FILE):
        self.file_path = file_path
        self.characters: List[Character] = []
        self.load()

    def load(self):
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.characters = [Character.from_dict(c) for c in data]
        else:
            self.characters = []

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(
                [c.to_dict() for c in self.characters], f, indent=2, ensure_ascii=False
            )

    def add(self, character: Character):
        self.characters.append(character)
        self.save()

    def update(self, character: Character):
        for idx, c in enumerate(self.characters):
            if c.id == character.id:
                self.characters[idx] = character
                self.save()
                return True
        return False

    def delete(self, character_id: str):
        self.characters = [c for c in self.characters if c.id != character_id]
        self.save()

    def get(self, character_id: str) -> Optional[Character]:
        for c in self.characters:
            if c.id == character_id:
                return c
        return None

    def list(self) -> List[Character]:
        return self.characters
