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
        content_type = request.headers.get('Content-Type')
        print(f"📡 Received content-type: {content_type}")

        if 'application/json' in content_type:
            data = request.get_json(force=True)
        else:
            raw_body = request.data.decode('utf-8')
            print("📦 Raw POST body:", raw_body)
            
            # Parse manually if needed (basic example):
            data = {}
            for line in raw_body.strip().splitlines():
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    data[key.strip()] = value.strip()
        
        signal = data.get("signal")
        price = data.get("price")
        symbol = data.get("symbol")
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = f"{now} - Signal: {signal} | Symbol: {symbol} | Price: {price}\n"
        print(log_entry)

        with open(LOG_FILE, "a") as f:
            f.write(log_entry)

        return jsonify({"status": "received", "data": data})
    
    except Exception as e:
        print("❌ Webhook error:", str(e))
        return jsonify({"error": str(e)}), 500

