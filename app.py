from flask import Flask, request, jsonify
from datetime import datetime, timezone
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route("/webhook", methods=["POST"])
def webhook():
    raw = request.data.decode("utf-8")
    logging.info(f"Raw data: {raw}")

    data = request.get_json()
    if not data:
        logging.warning("No JSON received.")
        return jsonify({"error": "No JSON received"}), 400

    logging.info(f"Received JSON: {data}")

    signal = data.get("signal")
    price = data.get("price")
    symbol = data.get("symbol")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    log_entry = f"{now} - Signal: {signal} | Symbol: {symbol} | Price: {price}"
    logging.info(log_entry)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
