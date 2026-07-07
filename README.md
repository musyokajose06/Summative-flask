# Inventory Management REST API + CLI

A Flask REST API for managing an inventory of grocery products, enriched with
real product data from the [OpenFoodFacts](https://world.openfoodfacts.org/)
API, plus an interactive command-line frontend that talks to that API.

## Problem Definition (Task 1)

Small grocery/inventory operations need a way to track products (name,
brand, ingredients, price, stock) without manually typing in every product's
details. This project solves that by:
- Storing inventory items in a simple backend (in-memory array, simulating a DB).
- Letting a barcode auto-fill product details via the OpenFoodFacts API.
- Exposing everything through a RESTful API.
- Giving the user a friendly CLI menu instead of requiring raw HTTP calls.

## Design (Task 2)

**Routes** (RESTful conventions):

| Method | Route                     | Purpose                                   |
|--------|----------------------------|-------------------------------------------|
| GET    | `/inventory`               | Fetch all items                           |
| GET    | `/inventory/<id>`          | Fetch a single item                       |
| POST   | `/inventory`                | Add a new item                            |
| PATCH  | `/inventory/<id>`          | Update an item (e.g. price, stock)        |
| DELETE | `/inventory/<id>`          | Remove an item                            |
| GET    | `/inventory/lookup`        | Query OpenFoodFacts directly (not saved)  |

**Storage:** a plain Python list of `InventoryItem` objects inside
`InventoryStorage` (see `storage.py`) simulates a database. Each item has an
auto-incrementing integer `id`.

**Data shape** (mirrors what OpenFoodFacts returns):
```json
{
  "id": 1,
  "product_name": "Organic Almond Milk",
  "barcode": "3017620422003",
  "brands": "Silk",
  "ingredients_text": "Filtered water, almonds, cane sugar, ...",
  "price": 3.49,
  "stock": 24
}
```

## Project Structure