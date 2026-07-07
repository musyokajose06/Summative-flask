from models import InventoryItem


class InventoryStorage:
    def __init__(self):
        self._items = []          
        self._next_id = 1

    def get_all(self):
        return list(self._items)

    def get_by_id(self, item_id):
        for item in self._items:
            if item.id == item_id:
                return item
        return None


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

storage = InventoryStorage()