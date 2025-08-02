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
    try:
        data = request.get_json(force=True)  # force=True just in case headers are off
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

    print("✅ RAW POST BODY:", request.data)  # DEBUG
    print("✅ PARSED JSON:", data)            # DEBUG

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    signal = data.get("signal")
    price = data.get("price")
    symbol = data.get("symbol")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"{now} - Signal: {signal} | Symbol: {symbol} | Price: {price}\n"
    print("✅ LOG ENTRY:", log_entry)

    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

    return jsonify({"status": "received", "data": data}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

