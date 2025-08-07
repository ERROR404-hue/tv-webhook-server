from flask import Flask, request, jsonify
from datetime import datetime, timezone
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Force JSON parsing even if headers are wrong
    data = request.get_json(force=True, silent=True)
    if not data:
        logging.warning("No JSON received.")
        return jsonify({"error": "No JSON received"}), 400

    action = data.get("action")
    price = data.get("price")
    symbol = data.get("symbol")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f UTC")[:-3]

    log_entry = f"{now} - Action: {action} | Symbol: {symbol} | Price: {price}"
    logging.info(log_entry)

    return jsonify({"status": "success"}), 200

@app.route("/", methods=["GET"])
def health_check():
    return "*nudges sorry boss hard to keep awake!", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
