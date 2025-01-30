from flask import Blueprint, jsonify, request
import json
import os
import paho.mqtt.client as mqtt
from .mqtt_client import mqtt_client 

mushroompoint_bp = Blueprint("mushroompoints", __name__)

MUSHROOM_FILE = "mushroompoints.json"
topic = "/map/mushroompoints"

# MQTT API do publikowania lokalizacji grzybów
@mushroompoint_bp.route("/add_mushroompoints", methods=["POST"])
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


# CRUD dla MushroomPoint
@mushroompoint_bp.route('/mushroompoints', methods=['POST'])
def create_mushroompoints():
    mushroompoints = load_mushroom_points()  
    new_mushroompoints = request.json  
    new_mushroompoints['id'] = max([m['id'] for m in mushroompoints], default=0) + 1  
    mushroompoints.append(new_mushroompoints)  
    save_mushroomspoint(mushroompoints)  
    return jsonify(new_mushroompoints), 201  

@mushroompoint_bp.route('/mushroompoints', methods=['GET'])
def get_mushroompoints():
    mushroompoints = load_mushroom_points() 
    return jsonify(mushroompoints)  

@mushroompoint_bp.route('/mushroompoints/<int:mushroompoint_id>', methods=['PUT'])
def update_mushroompoint(mushroompoint_id):
    mushroompoints = load_mushroom_points()
    mushroom = next((m for m in mushroompoints if m['id'] == mushroompoint_id), None)
    
    if mushroom:
        for key, value in request.json.items():
            mushroom[key] = value
        save_mushroomspoint(mushroompoints) 
        return jsonify(mushroom)
    
    return jsonify({'error': 'MushroomPoint not found'}), 404

@mushroompoint_bp.route('/mushroompoints/<int:mushroompoint_id>', methods=['DELETE'])
def delete_mushroompoints(mushroompoint_id):  
    mushroompoints = load_mushroom_points() 
    mushroompoints = [m for m in mushroompoints if m['id'] != mushroompoint_id]  
    save_mushroomspoint(mushroompoints)  
    return '', 204
