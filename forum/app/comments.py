# from flask import Blueprint, jsonify, request, session
# import json
# import os
# import uuid

# comments_bp = Blueprint("comments", __name__)

# COMMENTS_FILE = "comments.json"

# def load_comments(post_id=None):
#     if os.path.exists(COMMENTS_FILE):
#         with open(COMMENTS_FILE, "r", encoding="utf-8") as file:
#             comments = json.load(file)
#             if post_id is not None:
#                 return [c for c in comments if c["post_id"] == post_id]
#             return comments
#     return []

# def save_comments(comments):
#     with open(COMMENTS_FILE, "w", encoding="utf-8") as file:
#         json.dump(comments, file, indent=4, ensure_ascii=False)

# def add_comment(comment):
#     comments = load_comments()
#     comment["id"] = str(uuid.uuid4())  # Unikalne ID dla komentarza
#     comments.append(comment)
#     save_comments(comments)

# def update_comment(comment_id, new_content):
#     comments = load_comments()
#     for comment in comments:
#         if comment["id"] == comment_id and comment["author"] == session.get("username"):
#             comment["content"] = new_content
#             save_comments(comments)
#             return True
#     return False

# def delete_comment(comment_id):
#     comments = load_comments()
#     new_comments = [c for c in comments if not (c["id"] == comment_id and c["author"] == session.get("username"))]
#     if len(new_comments) < len(comments):
#         save_comments(new_comments)
#         return True
#     return False

# @comments_bp.route("/post/<int:post_id>/comments", methods=["POST", "GET"])
# def handle_comments(post_id):
#     if request.method == "POST":
#         if "username" not in session:
#             return jsonify({"error": "Nie jesteś zalogowany"}), 403

#         comment = request.json
#         comment["author"] = session["username"]
#         comment["post_id"] = post_id
#         add_comment(comment)
#         return jsonify(comment), 201

#     if request.method == "GET":
#         comments = load_comments(post_id)
#         return jsonify(comments), 200

# @comments_bp.route("/comments/<comment_id>", methods=["PUT", "DELETE"])
# def modify_comment(comment_id):
#     if "username" not in session:
#         return jsonify({"error": "Nie jesteś zalogowany"}), 403

#     if request.method == "PUT":
#         new_content = request.json.get("content")
#         if update_comment(comment_id, new_content):
#             return jsonify({"message": "Komentarz zaktualizowany"}), 200
#         return jsonify({"error": "Nie znaleziono komentarza lub brak uprawnień"}), 403

#     if request.method == "DELETE":
#         if delete_comment(comment_id):
#             return jsonify({"message": "Komentarz usunięty"}), 200
#         return jsonify({"error": "Nie znaleziono komentarza lub brak uprawnień"}), 403
