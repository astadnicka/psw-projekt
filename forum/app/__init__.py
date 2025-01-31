import logging
import json
import os
from flask import Flask, request
from datetime import datetime

from app.mqtt_client import mqtt_client
from app.mushroom import mushroom_bp
from app.mushroompoint import mushroompoint_bp
from app.routes import main_bp

LOG_FILE = "logs.json"

def clear_logs():
    with open(LOG_FILE, "w") as file:
        json.dump([], file, indent=4)

def log_to_json(level, message):
    """Zapisuje logi do pliku logs.json"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        "method": request.method if request else "N/A",
        "endpoint": request.path if request else "N/A",
        "ip": request.remote_addr if request else "N/A"
    }

    # Sprawdzamy, czy plik jest pusty lub nieistniejący
    try:
        with open(LOG_FILE, "r") as file:
            logs = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        # Jeśli plik jest pusty lub nie istnieje, inicjalizujemy go jako pustą listę
        logs = []

    logs.append(log_entry)

    with open(LOG_FILE, "w") as file:
        json.dump(logs, file, indent=4)


class JsonFileHandler(logging.Handler):
    def emit(self, record):
        log_to_json(record.levelname, record.getMessage())

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"

    clear_logs()

    app.register_blueprint(main_bp)
    app.register_blueprint(mushroom_bp)
    app.register_blueprint(mushroompoint_bp)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(JsonFileHandler())

    @app.before_request
    def log_request():
        log_to_json("INFO", f"Request to {request.path}")

    mqtt_client.connect("test.mosquitto.org", 1883, 60)
    mqtt_client.loop_start()

    return app
