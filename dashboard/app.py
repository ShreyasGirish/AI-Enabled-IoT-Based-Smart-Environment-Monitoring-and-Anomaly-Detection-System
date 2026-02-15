import os
import numpy as np
import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="AI + IoT Smart Environment Dashboard",
    layout="wide"
)

# =================================================
# AUTO REFRESH — every 2 seconds
# =================================================
st_autorefresh(interval=2000, key="live_refresh")

# =================================================
# TITLE
# =================================================
st.markdown("""
<h1 style="text-align:center;">AI + IoT Smart Environment Monitoring Dashboard</h1>
<p style="text-align:center; color:gray;">
ESP32 • MQTT • Real-time Analytics • System Health
</p>
""", unsafe_allow_html=True)

# =================================================
# PATHS
# =================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "db", "sensor_data.db")

# =================================================
# LOAD DATA
# =================================================
def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT timestamp, temperature, humidity, distance
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 500
        """,
        conn
    )
    conn.close()

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    FAR_DISTANCE = 100
    df["distance"] = df["distance"].apply(
        lambda d: FAR_DISTANCE if pd.isna(d) or d <= 0 else d
    )

    return df.sort_values("timestamp")


df = load_data()

if df.empty:
    st.warning("Waiting for live data from ESP32...")
    st.stop()

# =================================================
# LIVE WINDOW — 60 seconds (more sensitive)
# =================================================
now = datetime.now()
df_recent = df[df["timestamp"] > now - timedelta(seconds=60)]

if df_recent.empty:
    df_recent = df.tail(5)

latest = df_recent.iloc[-1]

# =================================================
# ML: Improved Z-Score Anomaly Detection
# =================================================
def compute_z_score(series):
    if len(series) < 15:
        return 0.0

    baseline = series[:-1]  # exclude latest
    current_value = series.iloc[-1]

    mean = np.mean(baseline)
    std = np.std(baseline)

    if std < 0.5:
        std = 0.5

    z = (current_value - mean) / std
    return round(float(z), 2)


def z_to_status(z):
    z = abs(z)
    if z < 1.5:
        return "Normal"
    elif z < 2.5:
        return "Warning"
    else:
        return "Anomaly"


temp_z = compute_z_score(df_recent["temperature"].reset_index(drop=True))
hum_z = compute_z_score(df_recent["humidity"].reset_index(drop=True))
dist_z = compute_z_score(df_recent["distance"].reset_index(drop=True))

temp_status = z_to_status(temp_z)
hum_status = z_to_status(hum_z)
dist_status = z_to_status(dist_z)

# =================================================
# SYSTEM STATUS
# =================================================
st.divider()
st.subheader("📡 System Status")

latency = (now - latest["timestamp"]).total_seconds()

if latency < 5:
    st.success("ESP32 is ONLINE and streaming live data")
elif latency < 15:
    st.warning("ESP32 data delayed")
else:
    st.error("ESP32 is OFFLINE")

# =================================================
# SYSTEM HEALTH
# =================================================
st.divider()
st.subheader("🩺 System Health Monitor")

h1, h2, h3 = st.columns(3)

h1.metric("Last Data Received", latest["timestamp"].strftime("%H:%M:%S"))
h2.metric("Latency (sec)", f"{latency:.2f}")

if latency < 5:
    h3.metric("System Health", "Healthy")
elif latency < 15:
    h3.metric("System Health", "Delayed")
else:
    h3.metric("System Health", "Offline")

# =================================================
# LIVE SENSOR READINGS
# =================================================
st.divider()
st.subheader("📊 Live Sensor Readings")

c1, c2, c3 = st.columns(3)
c1.metric("Temperature (°C)", f"{latest['temperature']:.2f}")
c2.metric("Humidity (%)", f"{latest['humidity']:.2f}")
c3.metric("Distance (cm)", int(latest["distance"]))

# =================================================
# RULE-BASED INSIGHTS
# =================================================
st.divider()
st.subheader("🧠 Rule-Based Insights")

if latest["temperature"] > 32:
    st.error("High temperature detected")
elif latest["temperature"] < 18:
    st.warning("Low temperature detected")
else:
    st.success("Temperature is comfortable")

if latest["humidity"] > 70:
    st.warning("High humidity")
elif latest["humidity"] < 30:
    st.warning("Low humidity")
else:
    st.success("Humidity is normal")

if latest["distance"] < 30:
    st.error(f"Object VERY close ({int(latest['distance'])} cm)")
elif latest["distance"] < 50:
    st.warning(f"Object nearby ({int(latest['distance'])} cm)")
else:
    st.success("No object nearby")

# =================================================
# ML ANOMALY SCORES
# =================================================
st.divider()
st.subheader("📊 ML-Based Anomaly Scores")

a1, a2, a3 = st.columns(3)

a1.metric("Temperature Z-Score", temp_z, temp_status)
a2.metric("Humidity Z-Score", hum_z, hum_status)
a3.metric("Distance Z-Score", dist_z, dist_status)

# =================================================
# LIVE SENSOR TRENDS
# =================================================
st.divider()
st.subheader("📉 Live Sensor Trends")

st.line_chart(
    df_recent.set_index("timestamp")[["temperature", "humidity", "distance"]],
    height=350
)