from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.model.user import User

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    if "username" in session:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_data = User.read(username)
        if user_data and user_data["password"] == password:
            session["username"] = username
            session["isAdmin"] = user_data["isAdmin"]  # Dodajemy informację o adminie do sesji
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("main.login"))

    return render_template("login.html")

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Sprawdzamy, czy użytkownik już istnieje
        if User.read(username):
            flash("Username is already taken!", "danger")
            return redirect(url_for("main.register"))

        # Tworzymy nowego użytkownika
        new_user = User(username, password)
        try:
            new_user.create()  
            session["username"] = username
            session["isAdmin"] = new_user.isAdmin  
            flash("Registration successful! Redirecting to dashboard.", "success")
            return redirect(url_for("main.dashboard"))  
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("main.register"))

    return render_template("register.html")

@main_bp.route("/dashboard")
def dashboard():
    if "username" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("main.login"))
    return render_template("dashboard.html", username=session["username"])

@main_bp.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


@main_bp.route("/mushroom-atlas")
def mushroomatlas():
    return render_template("mushroomatlas.html")

@main_bp.route("/map")
def map():
    return render_template("map.html")


from flask import send_from_directory, app
import os

@main_bp.route('/mushrooms.json')
def get_mushrooms_json():
    return send_from_directory(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'mushrooms.json'
    )

@main_bp.route('/mushroompoints.json')
def get_mushroompoints_json():
    return send_from_directory(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'mushroompoints.json'
    )


@main_bp.route("/guest")
def guest_login():
    session["username"] = ''
    session["isAdmin"] = False  
    flash("You are now visiting as a guest.", "info")
    return redirect(url_for("main.dashboard"))


@main_bp.route('/chat/<float:latitude>/<float:longitude>', methods=['POST', 'GET'])
def chat(latitude, longitude):
    # Sprawdź, czy użytkownik jest zalogowany
    if "username" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect('/map')  # Przekieruj na stronę mapy, aby się zalogować
    
    username = session["username"]  
    room = f"{latitude},{longitude}"  

    return render_template('chat.html', username=username, room=room, latitude=latitude, longitude=longitude)