import paho.mqtt.client as mqtt

broker = "test.mosquitto.org"
port = 1883
topic = "/map/mushroompoints"

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker! Return code: {rc}")
    client.subscribe(topic)

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic: {msg.topic}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(broker, port, 60)

mqtt_client.loop_start()
