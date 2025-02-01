from flask import Flask, request
from flask_socketio import SocketIO
import logging
import json
from datetime import datetime
from app.mqtt_client import mqtt_client
from app.mushroom import mushroom_bp
from app.mushroompoint import mushroompoint_bp
from app.routes import main_bp
from app.chat import chat_bp
from app.chat import register_chat_blueprint 

LOG_FILE = "logs.json"

# Funkcja czyszcząca logi
def clear_logs():
    with open(LOG_FILE, "w") as file:
        json.dump([], file, indent=4)

# Funkcja zapisująca logi w pliku JSON
def log_to_json(level, message):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        "method": request.method if request else "N/A",
        "endpoint": request.path if request else "N/A",
        "ip": request.remote_addr if request else "N/A"
    }

    try:
        with open(LOG_FILE, "r") as file:
            logs = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):

        logs = []

    logs.append(log_entry)

    with open(LOG_FILE, "w") as file:
        json.dump(logs, file, indent=4)

# Klasa do obsługi logowania do pliku JSON
class JsonFileHandler(logging.Handler):
    def emit(self, record):
        log_to_json(record.levelname, record.getMessage())

# Inicjalizacja Flask-SocketIO
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"  # Możesz zmienić ten klucz

    clear_logs()

    app.register_blueprint(main_bp)
    app.register_blueprint(mushroom_bp)
    app.register_blueprint(mushroompoint_bp)

    register_chat_blueprint(app, socketio) 

    # Konfiguracja logowania
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(JsonFileHandler())

    @app.before_request
    def log_request():
        log_to_json("INFO", f"Request to {request.path}")

    # Inicjalizacja MQTT
    mqtt_client.connect("test.mosquitto.org", 1883, 60)
    mqtt_client.loop_start()

    # Inicjalizacja WebSocket
    socketio.init_app(app)

    return app

# Aplikacja główna
app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
