import json
import time
import paho.mqtt.client as mqtt
from ingestion import ingest

BROKER = "localhost"   # because Mosquitto is running locally
PORT = 1883
TOPIC = "iot/sensors/room1"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        ingest(payload)
        print("Received & stored:", payload)
    except Exception as e:
        print("Error processing message:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("MQTT subscriber running...")
client.loop_forever()