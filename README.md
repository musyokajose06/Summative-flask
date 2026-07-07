# Inventory Management REST API + CLI

A Flask REST API for managing an inventory of grocery products, enriched with
real product data from the [OpenFoodFacts](https://world.openfoodfacts.org/)
API, plus an interactive command-line frontend that talks to that API.

## Problem Definition

Small grocery/inventory operations need a way to track products (name,
brand, ingredients, price, stock) without manually typing in every product's
details. This project solves that by:
- Storing inventory items in a simple backend (in-memory array, simulating a DB).
- Letting a barcode auto-fill product details via the OpenFoodFacts API.
- Exposing everything through a RESTful API.
- Giving the user a friendly CLI menu instead of requiring raw HTTP calls.

## Design

**Routes** (RESTful conventions):

| Method | Route                     | Purpose                                   |
|--------|----------------------------|-------------------------------------------|
| GET    | `/inventory`               | Fetch all items                           |
| GET    | `/inventory/<id>`          | Fetch a single item                       |
| POST   | `/inventory`                | Add a new item                            |
| PATCH  | `/inventory/<id>`          | Update an item (e.g. price, stock)        |
| DELETE | `/inventory/<id>`          | Remove an item                            |
| GET    | `/inventory/lookup`        | Query OpenFoodFacts directly (not saved)  |

