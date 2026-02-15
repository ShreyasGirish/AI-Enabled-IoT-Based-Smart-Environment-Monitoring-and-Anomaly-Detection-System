# AI-Enabled IoT Smart Environment Monitoring System

An end-to-end AI-integrated IoT monitoring system built using ESP32, MQTT, Python, SQLite, Streamlit, and a locally deployed LLM (Ollama).

This system performs real-time environmental monitoring, statistical anomaly detection using Z-score analysis, and natural language interpretation of sensor data — fully offline.

---

## Key Features

- Real-time sensor data acquisition using ESP32
- MQTT-based lightweight communication (Mosquitto broker)
- Local data storage using SQLite
- Live dashboard built with Streamlit
- Statistical anomaly detection using Z-score method
- AI-powered assistant using local LLM (Ollama)
- Fully offline architecture (no cloud dependency)

---

## System Architecture

ESP32 → MQTT Broker → Python Subscriber → SQLite Database → Streamlit Dashboard → AI Assistant (Ollama)

---

## Sensors Used

- DHT11 – Temperature and Humidity
- HC-SR04 – Ultrasonic Distance Sensor

---

## Machine Learning Component

Anomaly detection is implemented using statistical Z-score analysis:

Z = (X − μ) / σ

Where:
- X = Current sensor value  
- μ = Mean of recent readings  
- σ = Standard deviation  

Thresholds:
- |Z| < 1.5 → Normal  
- 1.5 ≤ |Z| < 2.5 → Warning  
- |Z| ≥ 2.5 → Anomaly  

---

## Tech Stack

### Hardware
- ESP32 Dev Module
- DHT11 Sensor
- HC-SR04 Sensor

### Software
- PlatformIO (Firmware Development)
- Mosquitto MQTT Broker
- Python 3.10+
- SQLite
- Streamlit
- Ollama (Local LLM)

---

## Project Structure

```
ai_iot_dashboard/
│
├── firmware/              # ESP32 PlatformIO code
├── backend/
│   ├── mqtt_sub.py        # MQTT subscriber
│   ├── ollama_engine.py   # LLM integration
│   └── db/
│       └── sensor_data.db
│
├── dashboard/
│   └── app.py             # Streamlit dashboard
│
└── README.md
```

---

## How to Run

### 1. Start Mosquitto Broker

```
"C:\Program Files\mosquitto\mosquitto.exe" -c "C:\Program Files\mosquitto\mosquitto.conf" -v
```

### 2. Start MQTT Subscriber

```
python backend/mqtt_sub.py
```

### 3. Run Streamlit Dashboard

```
streamlit run dashboard/app.py
```

### 4. Ensure Ollama is Installed

```
ollama list
```

---

## Applications

- Smart Room Monitoring
- Lab Environment Tracking
- Industrial Safety Monitoring
- Edge AI Monitoring Systems
- Academic Demonstrations

---

## Future Improvements

- Replace DHT11 with BME280 for higher accuracy
- Add multi-sensor data fusion
- Implement time-series forecasting
- Cloud deployment option
- Multi-room scaling

---

## Author

Shreyas G  
B.E. Electronics & Communication Engineering  
NMIT, Bengaluru  

GitHub: https://github.com/ShreyasGirish
