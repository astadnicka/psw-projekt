from flask import Flask, jsonify, json, render_template, request, redirect, url_for, flash, session
from model.user import User  
import paho.mqtt.client as mqtt  
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATA_FILE = 'mushrooms.json'
MushroomPoint = 'MushroomPoint.json'


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

@app.route('/mushrooms', methods=['GET'])
def search_mushrooms():
    pattern = request.args.get('pattern')
    
    if not pattern:
        return jsonify({"error": "Pattern parameter is required"}), 400

    mushrooms = load_mushrooms()
    
    filtered_mushrooms = [m for m in mushrooms if pattern.lower() in m["latin"].lower()]

    return jsonify(filtered_mushrooms)


# MQTT API do publikowania lokalizacji grzybów
@app.route("/add_mushroompoints", methods=["POST"])
def mqtt_add_mushroom():
    data = request.json
    mushroompoints_data = {
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "name": data["name"],
        "description": data["description"],
        "rating": data.get("rating", 0)
    }
    mqtt_message = json.dumps(mushroompoints_data)  
    mqtt_client.publish(topic, mqtt_message)
    return {"status": "Published", "data": mushroompoints_data}, 201



# Strona do wyświetlania mapy i dodawania lokalizacji grzybów
@app.route('/map')
def map():
    return render_template('map.html')

MUSHROOM_FILE = "mushroompoints.json"

def load_mushroom_points():
    if os.path.exists(MUSHROOM_FILE):
        with open(MUSHROOM_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []  
    return []

def save_mushroomspoint(mushrooms):
    with open(MUSHROOM_FILE, 'w') as file:
        json.dump(mushrooms, file, indent=4)


#CRUD dla MushroomPoint
@app.route('/mushroompoints', methods=['POST'])
def create_mushroompoints():
    mushroompoints = load_mushroom_points()  
    new_mushroompoints = request.json  
    new_mushroompoints['id'] = max([m['id'] for m in mushroompoints], default=0) + 1  
    mushroompoints.append(new_mushroompoints)  
    save_mushroomspoint(mushroompoints)  
    return jsonify(new_mushroompoints), 201  

@app.route('/mushroompoints', methods=['GET'])
def get_mushroompoints():
    mushroompoints = load_mushroom_points() 
    return jsonify(mushroompoints)  

@app.route('/mushroompoints/<int:mushroompoint_id>', methods=['PUT'])
def update_mushroompoint(mushroompoint_id):
    mushroompoints = load_mushroom_points()
    mushroom = next((m for m in mushroompoints if m['id'] == mushroompoint_id), None)
    
    if mushroom:
        for key, value in request.json.items():
            mushroom[key] = value
        save_mushroomspoint(mushroompoints) 
        return jsonify(mushroom)
    
    return jsonify({'error': 'MushroomPoint not found'}), 404

@app.route('/mushroompoints/<int:mushroompoint_id>', methods=['DELETE'])
def delete_mushroompoints(mushroompoint_id):  
    mushroompoints = load_mushroom_points() 
    mushroompoints = [m for m in mushroompoints if m['id'] != mushroompoint_id]  
    save_mushroomspoint(mushroompoints)  
    return '', 204  

if __name__ == "__main__":
    app.run(debug=True)
