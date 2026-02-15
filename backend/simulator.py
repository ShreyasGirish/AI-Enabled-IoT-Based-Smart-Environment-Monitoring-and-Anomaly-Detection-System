# backend/simulator.py

import time
import random
from ingestion import ingest

print("Starting LIVE sensor simulator... (Press CTRL+C to stop)")

# Initial baseline values (room environment)
temperature = 25.0     # °C
humidity = 60.0        # %
distance = 120         # cm

while True:
    # --- Simulate natural sensor drift ---
    temperature += random.uniform(-0.3, 0.3)
    humidity += random.uniform(-0.8, 0.8)
    distance += random.randint(-3, 3)

    # --- Clamp values to realistic ranges ---
    temperature = max(15, min(40, temperature))
    humidity = max(20, min(90, humidity))
    distance = max(5, min(200, distance))

    payload = {
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "distance": distance
    }

    result = ingest(payload)
    print("Ingested:", result)

    # Sensor update interval (seconds)
    time.sleep(2)
