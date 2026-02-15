# backend/llm_engine.py

import os
import sqlite3
import pandas as pd
from google import genai

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "db", "sensor_data.db")

# -------------------------------------------------
# GEMINI CLIENT
# -------------------------------------------------
from google import genai
import os

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-1.5-flash-latest"
# -------------------------------------------------
# LOAD SENSOR DATA
# -------------------------------------------------
def load_data(limit=50):
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"""
        SELECT timestamp, temperature, humidity, distance
        FROM sensor_data
        ORDER BY id DESC
        LIMIT {limit}
        """,
        conn
    )
    conn.close()
    return df

# -------------------------------------------------
# CHAT FUNCTION
# -------------------------------------------------
def ask_llm(question: str) -> str:
    df = load_data()

    if df.empty:
        context = "No sensor data available."
    else:
        latest = df.iloc[0]
        context = f"""
Latest Sensor Reading:
Temperature: {latest['temperature']} °C
Humidity: {latest['humidity']} %
Distance: {latest['distance']} cm

Recent Sensor Data:
{df.to_string(index=False)}
"""

    prompt = f"""
You are an AI assistant for a smart IoT environment monitoring system.

Context:
{context}

User Question:
{question}

Give a clear, practical answer.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text