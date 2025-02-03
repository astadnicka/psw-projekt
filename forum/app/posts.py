from flask import Blueprint, jsonify, request, session
import json
import os

posts_bp = Blueprint("posts", __name__)

DATA_FILE = "posts.json"

def load_posts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(posts, file, indent=4, ensure_ascii=False)

@posts_bp.route("/post/<int:post_id>", methods=["GET"])
def get_post(post_id):
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if post:
        return jsonify(post)
    return jsonify({"error": "Post not found"}), 404

@posts_bp.route("/post", methods=["POST"])
def add_post():
    if "username" not in session:
        return jsonify({"error": "Nie jesteś zalogowany"}), 403

    posts = load_posts()
    new_post = request.json
    new_post["id"] = max([p["id"] for p in posts], default=0) + 1
    new_post["author"] = session["username"] 
    posts.append(new_post)
    save_posts(posts)
    
    return jsonify(new_post), 201

@posts_bp.route("/post/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    if "username" not in session:
        return jsonify({"error": "Nie jesteś zalogowany"}), 403

    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)

    if not post:
        return jsonify({"error": "Post nie istnieje"}), 404

    if post["author"] != session["username"]:  
        return jsonify({"error": "Nie możesz edytować tego posta"}), 403

    post["title"] = request.json.get("title", post["title"])
    post["content"] = request.json.get("content", post["content"])

    save_posts(posts)
    return jsonify(post)

@posts_bp.route("/post/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    if "username" not in session:
        return jsonify({"error": "Nie jesteś zalogowany"}), 403

    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)

    if not post:
        return jsonify({"error": "Post nie istnieje"}), 404

    if post["author"] != session["username"] and not session.get("isAdmin", False):
        return jsonify({"error": "Nie możesz usunąć tego posta"}), 403

    posts = [p for p in posts if p["id"] != post_id]
    save_posts(posts)
    return '', 204

@posts_bp.route("/api/posts", methods=["GET"])
def get_posts():
    posts = load_posts()
    return jsonify(posts)
