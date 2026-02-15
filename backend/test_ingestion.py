# backend/test_ingestion.py

from ingestion import ingest
import time

print("Starting ingestion test...")

test_payloads = [
    {"temperature": 25, "humidity": 60, "distance": 100},
    {"temperature": 26, "humidity": 61, "distance": 99},
    {"temperature": 27, "humidity": 62, "distance": 98},
    {"temperature": 28, "humidity": 63, "distance": 97},
    {"temperature": 29, "humidity": 64, "distance": 96},
]

for payload in test_payloads:
    result = ingest(payload)
    print("Ingested:", result)
    time.sleep(1)

print("Test completed successfully.")
