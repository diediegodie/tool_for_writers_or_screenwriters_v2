import os
import json
from datetime import datetime

TIMELINE_FILE = os.path.join(os.path.dirname(__file__), "timeline_board.json")
TIMELINE_HISTORY_DIR = os.path.join(os.path.dirname(__file__), "timeline_history")
os.makedirs(TIMELINE_HISTORY_DIR, exist_ok=True)


def load_timeline_board():
    if not os.path.exists(TIMELINE_FILE):
        return None
    with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def save_timeline_board(state):
    with open(TIMELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    # Also save a timestamped version for history
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    hist_file = os.path.join(TIMELINE_HISTORY_DIR, f"timeline_{ts}.json")
    with open(hist_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
