from flask import Flask
from app.mqtt_client import mqtt_client
from app.mushroom import mushroom_bp
from app.mushroompoint import mushroompoint_bp
from app.routes import main_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"

    app.register_blueprint(main_bp)
    app.register_blueprint(mushroom_bp, )
    app.register_blueprint(mushroompoint_bp)

    mqtt_client.connect("test.mosquitto.org", 1883, 60)
    mqtt_client.loop_start()

    return app
