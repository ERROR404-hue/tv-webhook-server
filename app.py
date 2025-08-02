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
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    signal = data.get("signal")
    price = data.get("price")
    symbol = data.get("symbol")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"{now} - Signal: {signal} | Symbol: {symbol} | Price: {price}\n"
    print(log_entry)

    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

    return jsonify({"status": "received", "data": data})

# THIS KEEPS THE SERVER RUNNING
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
