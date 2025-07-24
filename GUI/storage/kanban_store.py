import json
import os
import datetime

KANBAN_FILE = os.path.join(os.path.dirname(__file__), "kanban_board.json")
KANBAN_HISTORY_DIR = os.path.join(os.path.dirname(__file__), "kanban_history")


def load_kanban_board():
    if os.path.exists(KANBAN_FILE):
        with open(KANBAN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Defensive: ensure all cards have 'metadata' and 'links' fields
            for col_cards in data.values():
                for card in col_cards:
                    if isinstance(card, dict):
                        if "metadata" not in card or not isinstance(
                            card["metadata"], dict
                        ):
                            card["metadata"] = {}
                        if "links" not in card["metadata"] or not isinstance(
                            card["metadata"].get("links"), list
                        ):
                            card["metadata"]["links"] = []
            return data
    return {}


def save_kanban_board(state):
    with open(KANBAN_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    # Also save a timestamped version for history
    if not os.path.exists(KANBAN_HISTORY_DIR):
        os.makedirs(KANBAN_HISTORY_DIR)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    hist_file = os.path.join(KANBAN_HISTORY_DIR, f"kanban_{ts}.json")
    with open(hist_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def list_kanban_versions():
    if not os.path.exists(KANBAN_HISTORY_DIR):
        return []
    files = [f for f in os.listdir(KANBAN_HISTORY_DIR) if f.endswith(".json")]
    files.sort(reverse=True)
    return files


def load_kanban_version(filename):
    path = os.path.join(KANBAN_HISTORY_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
