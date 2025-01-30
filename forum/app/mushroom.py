from flask import Blueprint, jsonify, request
import json
import os

mushroom_bp = Blueprint("mushroom", __name__)

DATA_FILE = "mushrooms.json"

def load_mushrooms():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []

def save_mushrooms(mushrooms):
    with open(DATA_FILE, "w") as file:
        json.dump(mushrooms, file, indent=4)

@mushroom_bp.route("/mushroom/<int:mushroom_id>", methods=["GET"])
def get_mushroom(mushroom_id):
    mushrooms = load_mushrooms()
    mushroom = next((m for m in mushrooms if m["id"] == mushroom_id), None)
    if mushroom:
        return jsonify(mushroom)
    return jsonify({"error": "Mushroom not found"}), 404

@mushroom_bp.route("/mushroom", methods=["POST"])
def add_mushroom():
    mushrooms = load_mushrooms()
    new_mushroom = request.json
    new_mushroom["id"] = max([m["id"] for m in mushrooms], default=0) + 1
    mushrooms.append(new_mushroom)
    save_mushrooms(mushrooms)
    return jsonify(new_mushroom), 201

@mushroom_bp.route("/mushroom/<int:mushroom_id>", methods=["PUT"])
def update_mushroom(mushroom_id):
    mushrooms = load_mushrooms()
    mushroom = next((m for m in mushrooms if m["id"] == mushroom_id), None)
    
    if mushroom:
        for key, value in request.json.items():
            mushroom[key] = value
        save_mushrooms(mushrooms)
        return jsonify(mushroom)
    
    return jsonify({"error": "Mushroom not found"}), 404

@mushroom_bp.route("/mushroom/<int:mushroom_id>", methods=["DELETE"])
def delete_mushroom(mushroom_id):
    mushrooms = load_mushrooms()
    mushrooms = [m for m in mushrooms if m["id"] != mushroom_id]
    save_mushrooms(mushrooms)
    return '', 204

@mushroom_bp.route("/mushrooms", methods=["GET"])
def search_mushrooms():
    pattern = request.args.get("pattern")
    
    if not pattern:
        return jsonify({"error": "Pattern parameter is required"}), 400

    mushrooms = load_mushrooms()
    filtered_mushrooms = [m for m in mushrooms if pattern.lower() in m["latin"].lower()]

    return jsonify(filtered_mushrooms)

@mushroom_bp.route("/mushrooms.json", methods=["GET"])
def mushrooms():
    try:
        mushrooms = load_mushrooms()
        return jsonify(mushrooms)
    except Exception as e:
        print(f"Error loading mushrooms.json: {e}")
        return jsonify([])

