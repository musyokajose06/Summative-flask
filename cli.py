import requests

API_BASE = "http://127.0.0.1:5000"

def _request(method, path, **kwargs):
    """Wrap requests calls so connection errors don't crash the CLI."""
    url = f"{API_BASE}{path}"
    try:
        response = requests.request(method, url, timeout=8, **kwargs)
    except requests.ConnectionError:
        print("\n[Error] Could not connect to the API. Is app.py running?\n")
        return None
    except requests.RequestException as exc:
        print(f"\n[Error] Request failed: {exc}\n")
        return None
    return response


def _print_item(item):
    print(f"  ID:          {item.get('id')}")
    print(f"  Name:        {item.get('product_name')}")
    print(f"  Barcode:     {item.get('barcode')}")
    print(f"  Brand:       {item.get('brands')}")
    print(f"  Ingredients: {item.get('ingredients_text')}")
    print(f"  Price:       ${item.get('price')}")
    print(f"  Stock:       {item.get('stock')}")

def view_all_items():
    response = _request("GET", "/inventory")
    if response is None:
        return
    if response.status_code != 200:
        print(f"[Error] {response.json().get('error')}")
        return

    items = response.json()
    if not items:
        print("\nInventory is empty.\n")
        return

    print(f"\n--- Inventory ({len(items)} items) ---")
    for item in items:
        print(f"  [{item['id']}] {item['product_name']}  "
              f"(${item['price']}, stock: {item['stock']})")
    print()


def view_item_details():
    item_id = input("Enter item ID: ").strip()
    if not item_id.isdigit():
        print("[Error] ID must be a number.")
        return

    response = _request("GET", f"/inventory/{item_id}")
    if response is None:
        return
    if response.status_code == 404:
        print(f"[Error] {response.json().get('error')}")
        return
    if response.status_code != 200:
        print(f"[Error] {response.json().get('error')}")
        return

    print("\n--- Item Details ---")
    _print_item(response.json())
    print()


def add_new_item():
    print("\nAdd a new item. Leave barcode blank to enter details manually.")
    barcode = input("Barcode (optional): ").strip() or None

    payload = {}
    if barcode:
        payload["barcode"] = barcode
        payload["enhance_from_api"] = True
        print("Will attempt to auto-fill product details from OpenFoodFacts.")
        name_override = input("Product name override (optional, press Enter to use API data): ").strip()
        if name_override:
            payload["product_name"] = name_override
    else:
        payload["product_name"] = input("Product name: ").strip()
        payload["brands"] = input("Brand (optional): ").strip() or None
        payload["ingredients_text"] = input("Ingredients (optional): ").strip() or None

    price = input("Price: ").strip()
    stock = input("Stock quantity: ").strip()
    try:
        payload["price"] = float(price) if price else 0.0
        payload["stock"] = int(stock) if stock else 0
    except ValueError:
        print("[Error] Price must be a number and stock must be an integer.")
        return

    response = _request("POST", "/inventory", json=payload)
    if response is None:
        return
    if response.status_code != 201:
        print(f"[Error] {response.json().get('error')}")
        return

    print("\nItem added successfully:")
    _print_item(response.json())
    print()


def update_item():
    item_id = input("Enter item ID to update: ").strip()
    if not item_id.isdigit():
        print("[Error] ID must be a number.")
        return

    print("Leave a field blank to leave it unchanged.")
    price = input("New price: ").strip()
    stock = input("New stock quantity: ").strip()

    payload = {}
    if price:
        try:
            payload["price"] = float(price)
        except ValueError:
            print("[Error] Price must be a number.")
            return
    if stock:
        try:
            payload["stock"] = int(stock)
        except ValueError:
            print("[Error] Stock must be an integer.")
            return

    if not payload:
        print("Nothing to update.")
        return

    response = _request("PATCH", f"/inventory/{item_id}", json=payload)
    if response is None:
        return
    if response.status_code != 200:
        print(f"[Error] {response.json().get('error')}")
        return

    print("\nItem updated:")
    _print_item(response.json())
    print()


def delete_item():
    item_id = input("Enter item ID to delete: ").strip()
    if not item_id.isdigit():
        print("[Error] ID must be a number.")
        return

    confirm = input(f"Are you sure you want to delete item {item_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    response = _request("DELETE", f"/inventory/{item_id}")
    if response is None:
        return
    if response.status_code != 200:
        print(f"[Error] {response.json().get('error')}")
        return

    print(f"\n{response.json().get('message')}\n")


def find_item_on_api():
    print("\nSearch OpenFoodFacts (this does NOT save the item to inventory).")
    choice = input("Search by (1) barcode or (2) product name? ").strip()

    params = {}
    if choice == "1":
        params["barcode"] = input("Barcode: ").strip()
    elif choice == "2":
        params["name"] = input("Product name: ").strip()
    else:
        print("[Error] Invalid choice.")
        return

    response = _request("GET", "/inventory/lookup", params=params)
    if response is None:
        return
    if response.status_code != 200:
        print(f"[Error] {response.json().get('error')}")
        return

    data = response.json()
    print("\n--- Product found on OpenFoodFacts ---")
    print(f"  Name:        {data.get('product_name')}")
    print(f"  Brand:       {data.get('brands')}")
    print(f"  Ingredients: {data.get('ingredients_text')}")
    print(f"  Barcode:     {data.get('barcode')}")
    print()


MENU_ACTIONS = {
    "1": ("Add new inventory item", add_new_item),
    "2": ("View inventory (all / one item)", None),  # handled specially below
    "3": ("Update item price or stock", update_item),
    "4": ("Delete a product", delete_item),
    "5": ("Find item on API (no save)", find_item_on_api),
    "6": ("Exit", None),
}


def view_menu():
    print("  a) View all items")
    print("  b) View one item's details")
    sub = input("Choice: ").strip().lower()
    if sub == "a":
        view_all_items()
    elif sub == "b":
        view_item_details()
    else:
        print("[Error] Invalid choice.")


def main():
    print("=" * 50)
    print("   Inventory Management CLI")
    print("=" * 50)

    while True:
        print("\nMenu:")
        for key, (label, _) in MENU_ACTIONS.items():
            print(f"  {key}. {label}")

        choice = input("\nSelect an option: ").strip()

        if choice == "6":
            print("Goodbye!")
            break
        elif choice == "2":
            view_menu()
        elif choice in MENU_ACTIONS:
            _, action = MENU_ACTIONS[choice]
            action()
        else:
            print("[Error] Invalid choice, please try again.")


if __name__ == "__main__":
    main()