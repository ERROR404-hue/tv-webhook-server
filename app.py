from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

LOG_FILE = "alerts.log"

@app.route("/", methods=["GET"])
def index():
    return "Server is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    print("Raw data:", request.data.decode("utf-8"))  # 👈 NEW LINE
    data = request.get_json()
    if not data:
        print("No JSON received.")
        return jsonify({"error": "No JSON received"}), 400

    print("Received JSON:", data)  # 🔥 Already there

    signal = data.get("signal")
    price = data.get("price")
    symbol = data.get("symbol")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"{now} - Signal: {signal} | Symbol: {symbol} | Price: {price}\n"
    print(log_entry)

    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

    return jsonify({"status": "received", "data": data})
