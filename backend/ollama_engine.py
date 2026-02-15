# backend/ollama_engine.py

import sqlite3
import os
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "db", "sensor_data.db")

MODEL_NAME = "gemma3:1b"
OLLAMA_URL = "http://localhost:11434/api/generate"


def get_recent_data(limit=10):
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT timestamp, temperature, humidity, distance
        FROM sensor_data
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def ask_llm(user_question: str) -> str:
    data = get_recent_data()

    if not data:
        return "No sensor data available yet."

    context_lines = []
    for row in data:
        ts, temp, hum, dist = row
        context_lines.append(
            f"{ts} | T:{temp}C H:{hum}% D:{dist}cm"
        )

    context = "\n".join(context_lines)

    prompt = f"""
You are analyzing IoT environmental sensor data.

Recent readings:
{context}

User question:
{user_question}

Respond in 3 short lines.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=20
        )

        if response.status_code == 200:
            return response.json()["response"].strip()
        else:
            return "AI error occurred."

    except Exception as e:
        return f"AI error: {str(e)}"