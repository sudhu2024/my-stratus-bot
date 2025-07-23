# Stratus Trade Terminal - Backend Bot Engine
# Version 1.2 - Self-Hosted Edition

import os
import threading
import time
import requests
import logging
from flask import Flask, jsonify, request

# --- CONFIGURATION (Will be set on the Heroku server) ---
API_KEY = os.environ.get('API_KEY', 'default_api_key')
API_SECRET = os.environ.get('API_SECRET', 'default_api_secret')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'default_tg_token')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'default_chat_id')

# --- Strategy Parameters ---
MAX_DAILY_LOSSES = 3

# --- BOT STATE (This is the bot's live memory) ---
bot_state = {
    "is_running": False, # Start in a paused state
    "status_message": "Bot is currently idle.",
    "daily_losses": 0,
    "realized_pnl_today": 0,
    "active_trades": []
}

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CORE BOT FUNCTIONS ---

def send_telegram_alert(message):
    logging.info(f"Sending Telegram Alert: {message}")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logging.error(f"Could not send Telegram message: {e}")

def trading_loop():
    logging.info("Trading thread started.")
    while True:
        if bot_state["is_running"]:
            bot_state["status_message"] = "Scanning markets for opportunities..."
            # Placeholder for your actual trading strategy logic
            logging.info("Scanning markets...")
            time.sleep(15)
        else:
            bot_state["status_message"] = "Bot is paused. No new trades will be initiated."
            time.sleep(5)

# --- API SERVER (This allows the app to talk to the bot) ---

app = Flask(__name__)

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "is_running": bot_state["is_running"],
        "status_message": bot_state["status_message"],
        "realized_pnl_today": bot_state["realized_pnl_today"],
        "daily_losses": bot_state["daily_losses"],
        "max_daily_losses": MAX_DAILY_LOSSES,
        "active_trades": bot_state["active_trades"]
    })

@app.route('/api/control/start', methods=['POST'])
def start_bot():
    if not bot_state["is_running"]:
        bot_state["is_running"] = True
        send_telegram_alert("✅ Bot has been ACTIVATED remotely.")
        logging.info("Bot started via API call.")
    return jsonify({"message": "Bot started successfully."})

@app.route('/api/control/stop', methods=['POST'])
def stop_bot():
    if bot_state["is_running"]:
        bot_state["is_running"] = False
        send_telegram_alert("🛑 Bot has been DEACTIVATED remotely.")
        logging.info("Bot stopped via API call.")
    return jsonify({"message": "Bot stopped successfully."})

if __name__ == "__main__":
    trader_thread = threading.Thread(target=trading_loop, daemon=True)
    trader_thread.start()
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
