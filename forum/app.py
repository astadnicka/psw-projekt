from flask import Flask, jsonify, json, render_template, request, redirect, url_for, flash, session
from model.user import User  # Importowanie klasy User

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/")
def home():
    # Sprawdzenie, czy użytkownik jest zalogowany
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Wykorzystanie klasy User do weryfikacji użytkownika
        user_data = User.read(username)
        if user_data and user_data["password"] == password:
            session["username"] = username
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Sprawdzenie, czy użytkownik już istnieje za pomocą klasy User
        if User.read(username):
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        # Dodanie nowego użytkownika
        new_user = User(username, password)
        try:
            new_user.create()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/guest")
def guest():
    # Strona dla gości
    return render_template("guest.html")

@app.route("/dashboard")
def dashboard():
    # Sprawdzenie, czy użytkownik jest zalogowany
    if "username" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route('/mushroomatlas')
def mushroomatlas():
    return render_template('mushroomatlas.html')

@app.route('/mushrooms.json')
def mushrooms():
    try:
        with open('mushrooms.json') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"Error loading mushrooms.json: {e}")
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)
