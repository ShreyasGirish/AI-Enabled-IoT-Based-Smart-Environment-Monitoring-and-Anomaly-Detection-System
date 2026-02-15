import json
import time
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "iot/sensors/room1"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

payload = {
    "temperature": 26.5,
    "humidity": 58.2,
    "distance": 110
}

client.publish(TOPIC, json.dumps(payload))
print("Published:", payload)

client.disconnect()