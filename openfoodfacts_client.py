import requests

BASE_PRODUCT_URL = "https://world.openfoodfacts.org/api/v3/product/{barcode}.json"
SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

TIMEOUT_SECONDS = 8

# OpenFoodFacts asks every client to identify itself this way.
HEADERS = {"User-Agent": "InventoryCLI/1.0 (student-project@example.com)"}


class OpenFoodFactsError(Exception):
    pass


def _extract_fields(product):
    return {
        "product_name": product.get("product_name") or "Unknown product",
        "brands": product.get("brands"),
        "ingredients_text": product.get("ingredients_text"),
        "barcode": product.get("code"),
    }


def fetch_by_barcode(barcode):
    """Look up a single product by exact barcode. Returns a dict of fields."""
    try:
        response = requests.get(
            BASE_PRODUCT_URL.format(barcode=barcode),
            headers=HEADERS,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise OpenFoodFactsError(f"Could not reach OpenFoodFacts API: {exc}") from exc

    data = response.json()
    if data.get("status") != 1:
        raise OpenFoodFactsError(f"No product found for barcode '{barcode}'")

    return _extract_fields(data["product"])


def fetch_by_name(name):
    """Search for a product by name. Returns the first match's fields."""
    params = {"search_terms": name, "json": 1, "page_size": 1}
    try:
        response = requests.get(
            SEARCH_URL, params=params, headers=HEADERS, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise OpenFoodFactsError(f"Could not reach OpenFoodFacts API: {exc}") from exc

    data = response.json()
    products = data.get("products") or []
    if not products:
        raise OpenFoodFactsError(f"No product found matching '{name}'")

    return _extract_fields(products[0])