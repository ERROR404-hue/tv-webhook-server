from flask import Flask, request, jsonify
from datetime import datetime, timezone
import logging
import os
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET

# --- Flask app setup ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# --- Binance setup ---
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
if TESTNET:
    binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET, testnet=True)
else:
    binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

def get_yolo_quantity(symbol):
    """Calculate quantity to use 100% of available USDT balance."""
    try:
        balance_info = binance_client.futures_account_balance()
        usdt_balance = float([b['balance'] for b in balance_info if b['asset'] == 'USDT'][0])

        # Get current symbol price
        ticker = binance_client.futures_symbol_ticker(symbol=symbol)
        price = float(ticker['price'])

        # Quantity = all balance / current price
        qty = usdt_balance / price

        # Round down to 3 decimal places (Binance rule for SOL)
        qty = round(qty, 3)
        logging.info(f"YOLO Quantity for {symbol}: {qty} (USDT balance: {usdt_balance}, Price: {price})")
        return qty
    except Exception as e:
        logging.error(f"Error calculating YOLO quantity: {e}")
        return 0.0

# --- Webhook endpoint ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True)
    if not data:
        logging.warning("No JSON received.")
        return jsonify({"error": "No JSON received"}), 400

    action = data.get("action")
    symbol = data.get("symbol")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f UTC")[:-3]
    logging.info(f"{now} - Action: {action} | Symbol: {symbol}")

    try:
        qty = get_yolo_quantity(symbol)
        if qty <= 0:
            return jsonify({"status": "error", "message": "Invalid quantity"}), 500

        if action == "long_entry":
            order = binance_client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=qty
            )
        elif action == "short_entry":
            order = binance_client.futures_create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=qty
            )
        else:
            return jsonify({"status": "ignored", "reason": "unknown action"}), 200

        logging.info(f"Order executed: {order}")
        return jsonify({"status": "success", "order": order}), 200

    except Exception as e:
        logging.error(f"Order failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def health_check():
    return "*yawns* Boss I’m alive and ready to YOLO!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
