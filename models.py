"""
models.py
---------
Defines the InventoryItem data model.

Each item mirrors the shape of data returned by the OpenFoodFacts API
(status, product_name, brands, ingredients_text, barcode) plus fields
specific to our own inventory (id, price, stock).
"""


class InventoryItem:
    """Represents a single product in the inventory."""

    def __init__(self, item_id, product_name, barcode=None, brands=None,
                 ingredients_text=None, price=0.0, stock=0):
        self.id = item_id
        self.product_name = product_name
        self.barcode = barcode
        self.brands = brands
        self.ingredients_text = ingredients_text
        self.price = float(price)
        self.stock = int(stock)

    def to_dict(self):
        """Serialize the item to a plain dict (used for JSON responses)."""
        return {
            "id": self.id,
            "product_name": self.product_name,
            "barcode": self.barcode,
            "brands": self.brands,
            "ingredients_text": self.ingredients_text,
            "price": self.price,
            "stock": self.stock,
        }

    @classmethod
    def from_dict(cls, data):
        """Build an InventoryItem from a dict (used when reading requests)."""
        return cls(
            item_id=data.get("id"),
            product_name=data.get("product_name"),
            barcode=data.get("barcode"),
            brands=data.get("brands"),
            ingredients_text=data.get("ingredients_text"),
            price=data.get("price", 0.0),
            stock=data.get("stock", 0),
        )

    def update(self, data):
        """Apply a partial update (used by PATCH)."""
        if "product_name" in data:
            self.product_name = data["product_name"]
        if "barcode" in data:
            self.barcode = data["barcode"]
        if "brands" in data:
            self.brands = data["brands"]
        if "ingredients_text" in data:
            self.ingredients_text = data["ingredients_text"]
        if "price" in data:
            self.price = float(data["price"])
        if "stock" in data:
            self.stock = int(data["stock"])

    def __repr__(self):
        return f"<InventoryItem id={self.id} name={self.product_name!r}>"