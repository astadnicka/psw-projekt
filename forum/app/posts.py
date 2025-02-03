from flask import Blueprint, jsonify, request, session
import json
import os
from flask import render_template


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

@posts_bp.route("/post_details/<int:post_id>", methods=["GET"])
def post_details(post_id):
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "Post nie istnieje"}), 404
    return render_template("post_details.html", post=post)





#KOMENTARZE
# Dodanie komentarza do posta
# Comment routes

@posts_bp.route("/post/<int:post_id>/comment", methods=["POST"])
def add_comment(post_id):
    if "username" not in session:
        return jsonify({"error": "Nie jesteś zalogowany"}), 403

    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)

    if not post:
        return jsonify({"error": "Post nie istnieje"}), 404

    if "comments" not in post:
        post["comments"] = []  # Inicjalizacja komentarzy

    new_comment = request.json
    new_comment["id"] = max((c["id"] for c in post["comments"]), default=0) + 1
    new_comment["author"] = session["username"]

    post["comments"].append(new_comment)
    save_posts(posts)

    return jsonify(new_comment), 201



@posts_bp.route("/post/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)

    if not post:
        return jsonify({"error": "Post nie istnieje"}), 404

    return jsonify(post.get("comments", []))

@posts_bp.route("/post/<int:post_id>/comment/<int:comment_id>", methods=["PUT"])
def update_comment(post_id, comment_id):
    if "username" not in session:
        return jsonify({"error": "Nie jesteś zalogowany"}), 403

    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)

    if not post:
        return jsonify({"error": "Post nie istnieje"}), 404

    comment = next((c for c in post["comments"] if c["id"] == comment_id), None)

    if not comment:
        return jsonify({"error": "Komentarz nie istnieje"}), 404

    if comment["author"] != session["username"]:
        return jsonify({"error": "Nie możesz edytować tego komentarza"}), 403

    comment["content"] = request.json.get("content", comment["content"])
    save_posts(posts)
    return jsonify(comment)

@posts_bp.route("/post/<int:post_id>/comment/<int:comment_id>", methods=["DELETE"])
def delete_comment(post_id, comment_id):
    if "username" not in session:
        return jsonify({"error": "Nie jesteś zalogowany"}), 403

    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)

    if not post:
        return jsonify({"error": "Post nie istnieje"}), 404

    comment = next((c for c in post["comments"] if c["id"] == comment_id), None)

    if not comment:
        return jsonify({"error": "Komentarz nie istnieje"}), 404

    if comment["author"] != session["username"] and not session.get("isAdmin", False):
        return jsonify({"error": "Nie możesz usunąć tego komentarza"}), 403

    post["comments"] = [c for c in post["comments"] if c["id"] != comment_id]
    save_posts(posts)
    return '', 204
