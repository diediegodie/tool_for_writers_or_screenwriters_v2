def sync_all_kanban_to_timeline(widget):
    """
    Sync all Kanban cards in all columns to the Timeline. Show a summary dialog.
    """
    from PySide6.QtWidgets import QMessageBox

    synced = 0
    already = 0
    failed = 0
    for col in widget.columns:
        lw = col.list_widget
        for i in range(lw.count()):
            item = lw.item(i)
            try:
                result = convert_kanban_to_timeline_bulk(widget, item)
                if result == "already":
                    already += 1
                elif result == "ok":
                    synced += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
    msg = QMessageBox(widget)
    msg.setWindowTitle("Sync to Timeline Complete")
    msg.setText(f"{synced} card(s) synced, {already} already existed, {failed} failed.")
    msg.exec()


def sync_column_kanban_to_timeline(widget, list_widget):
    """
    Sync all Kanban cards in a column to the Timeline. Show a summary dialog.
    """
    from PySide6.QtWidgets import QMessageBox

    synced = 0
    already = 0
    failed = 0
    for i in range(list_widget.count()):
        item = list_widget.item(i)
        try:
            result = convert_kanban_to_timeline_bulk(widget, item)
            if result == "already":
                already += 1
            elif result == "ok":
                synced += 1
            else:
                failed += 1
        except Exception:
            failed += 1
    msg = QMessageBox(widget)
    msg.setWindowTitle("Sync Column to Timeline Complete")
    msg.setText(f"{synced} card(s) synced, {already} already existed, {failed} failed.")
    msg.exec()


def convert_kanban_to_timeline_bulk(widget, kanban_card):
    """
    Bulk version: returns status string instead of showing dialogs.
    """
    try:
        parent = widget.parent()
        timeline_tab = None
        for _ in range(5):
            if parent is None:
                break
            if hasattr(parent, "timeline_widget"):
                timeline_tab = parent
                break
            parent = parent.parent() if hasattr(parent, "parent") else None
        if timeline_tab and hasattr(timeline_tab, "timeline_widget"):
            timeline_widget = timeline_tab.timeline_widget
            existing_ids = {
                getattr(c, "metadata", {}).get("id")
                for c in getattr(timeline_widget, "cards", [])
            }
            if kanban_card.metadata["id"] in existing_ids:
                return "already"
            timeline_widget.add_card(kanban_card.metadata)
            return "ok"
        else:
            return "failed"
    except Exception:
        return "failed"


"""
kanban_board2.py – Auxiliary and helper logic for KanbanBoardWidget

This module contains helper classes and functions for KanbanBoardWidget that are not core UI/event logic.
"""


from PySide6.QtWidgets import QMessageBox
from .kanban_models import KanbanCard, CardDetailsDialog, Column


def convert_kanban_to_timeline(self, kanban_card):
    print(
        f"[DEBUG] _convert_kanban_to_timeline called for card id={kanban_card.metadata.get('id')}"
    )
    """
    Convert a KanbanCard to a TimelineCard by passing its metadata.
    Attempts to find the TimelineTab in the parent chain and add the card.
    Shows a confirmation dialog on success.
    """
    try:
        parent = self.parent()
        timeline_tab = None
        for _ in range(5):
            if parent is None:
                break
            if hasattr(parent, "timeline_widget"):
                timeline_tab = parent
                break
            parent = parent.parent() if hasattr(parent, "parent") else None
        if timeline_tab and hasattr(timeline_tab, "timeline_widget"):
            timeline_widget = timeline_tab.timeline_widget
            existing_ids = {
                getattr(c, "metadata", {}).get("id")
                for c in getattr(timeline_widget, "cards", [])
            }
            if kanban_card.metadata["id"] in existing_ids:
                QMessageBox.information(
                    self, "Already Exists", "This card already exists in the timeline."
                )
                return
            print(f"[DEBUG] Adding card to timeline: {kanban_card.metadata}")
            timeline_widget.add_card(kanban_card.metadata)
            QMessageBox.information(self, "Converted", "Card added to Timeline.")
        else:
            QMessageBox.warning(
                self,
                "Timeline Not Found",
                "Could not find the Timeline view to add the card.",
            )
    except Exception as e:
        import traceback

        print(f"[ERROR] Exception in convert_kanban_to_timeline: {e}")
        traceback.print_exc()


def navigate_to_link(self, link_id: str):
    """
    Navigate to the scene/chapter with the given ID.
    This should be connected to the main project editor navigation logic.
    For now, show a message box as a placeholder.
    """
    QMessageBox.information(self, "Navigate", f"Navigate to scene/chapter: {link_id}")
