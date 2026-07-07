"""
storage.py
----------
A simple in-memory "database" for InventoryItem objects.

This is intentionally a plain Python list wrapped in a class, per the
lab's requirement to "update temporary array to simulate storage."
Swapping this out for a real database later just means rewriting this
one file - nothing else in the app needs to change.
"""

from models import InventoryItem


class InventoryStorage:
    def __init__(self):
        self._items = []          # the "temporary array"
        self._next_id = 1

    # ---- read ----------------------------------------------------
    def get_all(self):
        return list(self._items)

    def get_by_id(self, item_id):
        for item in self._items:
            if item.id == item_id:
                return item
        return None

    # ---- write ------------------------------------------------------
    def add(self, item_data):
        """item_data: dict without an id. Returns the created InventoryItem."""
        item_data = dict(item_data)
        item_data["id"] = self._next_id
        item = InventoryItem.from_dict(item_data)
        self._items.append(item)
        self._next_id += 1
        return item

    def update(self, item_id, patch_data):
        item = self.get_by_id(item_id)
        if item is None:
            return None
        item.update(patch_data)
        return item

    def delete(self, item_id):
        item = self.get_by_id(item_id)
        if item is None:
            return False
        self._items.remove(item)
        return True

    def seed(self, items_data):
        """Load starter data (list of dicts) into storage."""
        for data in items_data:
            self.add(data)


# A single shared instance used across the whole app (module-level singleton)
storage = InventoryStorage()