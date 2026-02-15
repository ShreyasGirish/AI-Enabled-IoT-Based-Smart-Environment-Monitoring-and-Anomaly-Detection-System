# backend/ingestion.py

import os
import sqlite3
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "backend", "db")
DB_PATH = os.path.join(DB_DIR, "sensor_data.db")

# Ensure DB directory exists
os.makedirs(DB_DIR, exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            distance INTEGER
        )
    """)

    conn.commit()
    conn.close()


def ingest(sensor_payload: dict):
    """
    Central ingestion function using SQLite (concurrency safe).
    """

    # Ensure DB exists
    init_db()

    # Validate payload
    for key in ["temperature", "humidity", "distance"]:
        if key not in sensor_payload:
            raise ValueError(f"Missing required field: {key}")

    row = (
        datetime.now().isoformat(),
        float(sensor_payload["temperature"]),
        float(sensor_payload["humidity"]),
        int(sensor_payload["distance"])
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sensor_data (timestamp, temperature, humidity, distance)
        VALUES (?, ?, ?, ?)
    """, row)

    conn.commit()
    conn.close()

    return {
        "timestamp": row[0],
        "temperature": row[1],
        "humidity": row[2],
        "distance": row[3]
    }
