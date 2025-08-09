from flask import Flask, request, jsonify
from datetime import datetime, timezone
import logging
import os
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from binance.exceptions import BinanceAPIException

# --- Flask app setup ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# --- Binance setup ---
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"

if TESTNET:
    binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    binance_client.API_URL = 'https://testnet.binance.vision/api'
else:
    binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# --- Test API keys on startup ---
try:
    server_time = binance_client.get_server_time()
    logging.info(f"Binance connection OK. Server time: {server_time}")
except BinanceAPIException as e:
    logging.error(f"Binance API error on startup: {e}")
except Exception as e:
    logging.error(f"Startup connection failed: {e}")

# --- Webhook endpoint ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True)
    if not data:
        logging.warning("No JSON received.")
        return jsonify({"error": "No JSON received"}), 400

    action = data.get("action")
    price = data.get("price")
    symbol = data.get("symbol", "SOLUSDT").upper()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f UTC")[:-3]
    log_entry = f"{now} - Action: {action} | Symbol: {symbol} | Price: {price}"
    logging.info(log_entry)

    try:
        if action == "long_entry":
            order = binance_client.create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=0.1  # adjust lot size
            )
        elif action == "short_entry":
            order = binance_client.create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=0.1
            )
        else:
            return jsonify({"status": "ignored", "reason": "unknown action"}), 200

        logging.info(f"Order executed: {order}")
        return jsonify({"status": "success", "order": order}), 200

    except BinanceAPIException as e:
        logging.error(f"Order failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Health check ---
@app.route("/", methods=["GET"])
def health_check():
    return "*nudges sorry boss hard to keep awake!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
