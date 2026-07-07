from flask import Flask, jsonify, request

from storage import storage
from openfoodfacts_client import fetch_by_barcode, fetch_by_name, OpenFoodFactsError

app = Flask(__name__)

@app.route("/inventory", methods=["GET"])
def get_all_items():
    items = [item.to_dict() for item in storage.get_all()]
    return jsonify(items), 200

@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = storage.get_by_id(item_id)
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify(item.to_dict()), 200

@app.route("/inventory/lookup", methods=["GET"])
def lookup_item():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if not barcode and not name:
        return jsonify({"error": "Provide a 'barcode' or 'name' query parameter"}), 400

    try:
        if barcode:
            product_data = fetch_by_barcode(barcode)
        else:
            product_data = fetch_by_name(name)
    except OpenFoodFactsError as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify(product_data), 200

@app.route("/inventory", methods=["POST"])
def add_item():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    barcode = body.get("barcode")
    enhance = body.get("enhance_from_api", bool(barcode))

    item_data = {
        "product_name": body.get("product_name"),
        "barcode": barcode,
        "brands": body.get("brands"),
        "ingredients_text": body.get("ingredients_text"),
        "price": body.get("price", 0.0),
        "stock": body.get("stock", 0),
    }

    # Enhance stored inventory data with additional details from the API
    if enhance and barcode:
        try:
            off_data = fetch_by_barcode(barcode)
            for field in ("product_name", "brands", "ingredients_text"):
                if not item_data.get(field):
                    item_data[field] = off_data.get(field)
        except OpenFoodFactsError as exc:
            return jsonify({"error": f"API enhancement failed: {exc}"}), 502

    if not item_data.get("product_name"):
        return jsonify({"error": "product_name is required (or a valid barcode to look it up)"}), 400

    try:
        item_data["price"] = float(item_data.get("price", 0.0))
        item_data["stock"] = int(item_data.get("stock", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "price must be a number and stock must be an integer"}), 400

    new_item = storage.add(item_data)
    return jsonify(new_item.to_dict()), 201

@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    if "price" in body:
        try:
            body["price"] = float(body["price"])
        except (TypeError, ValueError):
            return jsonify({"error": "price must be a number"}), 400

    if "stock" in body:
        try:
            body["stock"] = int(body["stock"])
        except (TypeError, ValueError):
            return jsonify({"error": "stock must be an integer"}), 400

    updated = storage.update(item_id, body)
    if updated is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404

    return jsonify(updated.to_dict()), 200

@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    deleted = storage.delete(item_id)
    if not deleted:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify({"message": f"Item {item_id} deleted"}), 200

@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return jsonify({"error": "Method not allowed on this endpoint"}), 405


def seed_demo_data():
    storage.seed([
        {
            "product_name": "Organic Almond Milk",
            "barcode": "3017620422003",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar, ...",
            "price": 3.49,
            "stock": 24,
        },
        {
            "product_name": "Peanut Butter",
            "barcode": "0016000275287",
            "brands": "Jif",
            "ingredients_text": "Roasted peanuts, sugar, salt, ...",
            "price": 4.99,
            "stock": 15,
        },
    ])


if __name__ == "__main__":
    seed_demo_data()
    app.run(debug=True, port=5000)