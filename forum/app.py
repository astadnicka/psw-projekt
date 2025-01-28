from flask import Flask, jsonify, json, render_template, request, redirect, url_for, flash, session
from model.user import User  
import paho.mqtt.client as mqtt  
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATA_FILE = 'mushrooms.json'

broker = "test.mosquitto.org"  
port = 1883
topic = "/map/mushrooms"

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker! Return code: {rc}")
    client.subscribe(topic)

# Obsługa przychodzących wiadomości MQTT (opcjonalne logowanie)
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic: {msg.topic}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(broker, port, 60)
mqtt_client.loop_start()

@app.route("/")
def home():
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

        if User.read(username):
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

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
    return render_template("guest.html")

@app.route("/dashboard")
def dashboard():
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
        with open(DATA_FILE) as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"Error loading mushrooms.json: {e}")
        return jsonify([])

def load_mushrooms():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []

def save_mushrooms(mushrooms):
    with open(DATA_FILE, 'w') as file:
        json.dump(mushrooms, file, indent=4)

# CRUD API dla grzybów
@app.route('/mushroom/<int:mushroom_id>', methods=['GET'])
def get_mushroom(mushroom_id):
    mushrooms = load_mushrooms()
    mushroom = next((m for m in mushrooms if m['id'] == mushroom_id), None)
    if mushroom:
        return jsonify(mushroom)
    return jsonify({'error': 'Mushroom not found'}), 404

@app.route('/mushroom', methods=['POST'])
def add_mushroom():
    mushrooms = load_mushrooms()
    new_mushroom = request.json
    new_mushroom['id'] = max([m['id'] for m in mushrooms], default=0) + 1
    mushrooms.append(new_mushroom)
    save_mushrooms(mushrooms)
    return jsonify(new_mushroom), 201

@app.route('/mushroom/<int:mushroom_id>', methods=['PUT'])
def update_mushroom(mushroom_id):
    mushrooms = load_mushrooms()
    mushroom = next((m for m in mushrooms if m['id'] == mushroom_id), None)
    if not mushroom:
        return jsonify({'error': 'Mushroom not found'}), 404
    for key, value in request.json.items():
        mushroom[key] = value
    save_mushrooms(mushrooms)
    return jsonify(mushroom)

@app.route('/mushroom/<int:mushroom_id>', methods=['DELETE'])
def delete_mushroom(mushroom_id):
    mushrooms = load_mushrooms()
    mushrooms = [m for m in mushrooms if m['id'] != mushroom_id]
    save_mushrooms(mushrooms)
    return '', 204

# MQTT API do publikowania lokalizacji grzybów
@app.route("/add_mushroom", methods=["POST"])
def mqtt_add_mushroom():
    data = request.json
    mushroom_data = {
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "name": data["name"],
        "description": data["description"],
        "rating": data.get("rating", 0)
    }
    mqtt_message = json.dumps(mushroom_data)  # Użyj json.dumps zamiast jsonify
    mqtt_client.publish(topic, mqtt_message)
    return {"status": "Published", "data": mushroom_data}, 201

# Strona do wyświetlania mapy i dodawania lokalizacji grzybów
@app.route('/map')
def map():
    return render_template('map.html')

if __name__ == "__main__":
    app.run(debug=True)
