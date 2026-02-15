import os
import sys
import sqlite3
import numpy as np
import streamlit as st
import pandas as pd
from datetime import datetime

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Assistant",
    layout="wide"
)

# =================================================
# TITLE
# =================================================
st.markdown(
    """
    <h1 style="text-align:center;">Assistant</h1>
    <p style="text-align:center; color:#666;">
    Simple view of current environment and quick answers
    </p>
    """,
    unsafe_allow_html=True
)

# =================================================
# PATHS
# =================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "db", "sensor_data.db")

sys.path.append(os.path.join(BASE_DIR, "backend"))
from ollama_engine import ask_llm

# =================================================
# LOAD DATA
# =================================================
def load_data():
    if not os.path.exists(DB_PATH):
        return None, None

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT timestamp, temperature, humidity, distance
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 300
        """,
        conn
    )
    conn.close()

    if df.empty:
        return None, None

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    FAR = 100
    df["distance"] = df["distance"].apply(
        lambda d: FAR if pd.isna(d) or d <= 0 or d > 120 else d
    )

    latest = df.iloc[0]
    return df, latest

# =================================================
# ML: Z-SCORE
# =================================================
def z_score(series, value):
    if len(series) < 10:
        return 0.0
    mean = np.mean(series)
    std = np.std(series)
    if std == 0:
        return 0.0
    return round((value - mean) / std, 2)

def z_label(z):
    z = abs(z)
    if z < 2:
        return "Normal"
    elif z < 3:
        return "Unusual"
    else:
        return "Anomaly"

# =================================================
# SESSION STATE
# =================================================
if "question" not in st.session_state:
    st.session_state.question = None

if "answer" not in st.session_state:
    st.session_state.answer = None

# =================================================
# REFRESH BUTTON
# =================================================
col_l, col_r = st.columns([6, 1])
with col_r:
    if st.button("🔄 Refresh"):
        st.session_state.question = None
        st.session_state.answer = None

# =================================================
# LOAD SNAPSHOT
# =================================================
df, latest = load_data()

if df is None:
    st.error("No sensor data available. Start MQTT and subscriber.")
    st.stop()

# =================================================
# COMPUTE ML SCORES
# =================================================
temp_z = z_score(df["temperature"], latest["temperature"])
hum_z = z_score(df["humidity"], latest["humidity"])
dist_z = z_score(df["distance"], latest["distance"])

# =================================================
# CURRENT READINGS
# =================================================
st.subheader("Current readings")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Temperature (°C)", f"{latest['temperature']:.2f}")
c2.metric("Humidity (%)", f"{latest['humidity']:.2f}")
c3.metric("Distance (cm)", int(latest["distance"]))
c4.metric("Updated at", latest["timestamp"].strftime("%H:%M:%S"))

# =================================================
# STATUS
# =================================================
st.markdown("### Status")

s1, s2, s3 = st.columns(3)

# Temperature
if latest["temperature"] > 32:
    s1.error("Temperature is high")
elif latest["temperature"] < 18:
    s1.warning("Temperature is low")
else:
    s1.success("Temperature is normal")

# Humidity
if latest["humidity"] > 70:
    s2.warning("Humidity is high")
elif latest["humidity"] < 30:
    s2.warning("Humidity is low")
else:
    s2.success("Humidity is normal")

# Distance
if latest["distance"] <= 30:
    s3.error("Object very close")
elif latest["distance"] <= 50:
    s3.warning("Object nearby")
else:
    s3.success("Area clear")

# =================================================
# ML INSIGHT (COMPACT)
# =================================================
st.divider()
st.subheader("Pattern check")

m1, m2, m3 = st.columns(3)
m1.metric("Temperature", f"Z = {temp_z}", z_label(temp_z))
m2.metric("Humidity", f"Z = {hum_z}", z_label(hum_z))
m3.metric("Distance", f"Z = {dist_z}", z_label(dist_z))

# =================================================
# ASK ASSISTANT (SINGLE TURN)
# =================================================
st.divider()
st.subheader("Ask Assistant")

with st.form("ask_form", clear_on_submit=True):
    q = st.text_input(
        "Your question",
        placeholder="Is the environment safe right now?"
    )
    ask = st.form_submit_button("Ask")

if ask and q.strip():
    st.session_state.question = q

    context = f"""
Current readings:
Temperature: {latest['temperature']} °C
Humidity: {latest['humidity']} %
Distance: {latest['distance']} cm

Pattern analysis:
Temperature Z-score: {temp_z} ({z_label(temp_z)})
Humidity Z-score: {hum_z} ({z_label(hum_z)})
Distance Z-score: {dist_z} ({z_label(dist_z)})

Give a short, clear answer.
"""

    with st.spinner("Thinking..."):
        try:
            st.session_state.answer = ask_llm(
                context + "\n\nQuestion:\n" + q
            )
        except Exception:
            st.session_state.answer = "Unable to respond right now."

# =================================================
# RESULT
# =================================================
if st.session_state.question and st.session_state.answer:
    st.subheader("Result")
    st.markdown(f"**You:** {st.session_state.question}")
    st.success(st.session_state.answer)

# =================================================
# FOOTER
# =================================================
st.divider()
st.caption("Uses the latest available snapshot.")