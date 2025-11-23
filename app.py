from flask import Flask
import requests
import os

app = Flask(__name__)

# ================== CONFIG ==================
# Yaha apna Telegram bot token & chat id भरो
TELEGRAM_TOKEN = "8590259094:AAGuWFFM7rUBG-zzCqDJhxPZNfPWL5-mdkI"
CHAT_ID = "5469777349"

# Tumhari Shein link:
SHEIN_URL = "https://www.sheinindia.in/c/sverse-5939-37961?query=%3Arelevance%3Agenderfilter%3AMen&gridColumns=5&customerType=Existing"

# 0 items hone par page par jo texts dikhte hain:
ZERO_TEXT_1 = "No products found for these filters"  # mobile view text
ZERO_TEXT_2 = "0 Items Found"                        # desktop view text

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}
STATE_FILE = "state.txt"
# =============================================


def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.get(url, params={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        print("Telegram status:", r.status_code)
    except Exception as e:
        print("Telegram error:", e)


def read_last_state():
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            v = f.read().strip()
            if v == "True":
                return True
            if v == "False":
                return False
    except:
        pass
    return None


def write_last_state(value: bool):
    try:
        with open(STATE_FILE, "w") as f:
            f.write("True" if value else "False")
    except Exception as e:
        print("State write error:", e)


def check_stock():
    try:
        r = requests.get(SHEIN_URL, headers=HEADERS, timeout=15)
        print("HTTP status:", r.status_code)
        if r.status_code != 200:
            return None

        html = r.text

        # Dono view ke zero text check karo
        if (ZERO_TEXT_1 in html) or (ZERO_TEXT_2 in html):
            return False   # 0 items
        else:
            return True    # kuch item hai

    except Exception as e:
        print("Req error:", e)
        return None


@app.route("/")
def home():
    return "Shein checker running ✅"


@app.route("/check")
def check_route():
    # Ye function cron se call hoga
    current = check_stock()
    last = read_last_state()
    print("Last:", last, "Current:", current)

    if current is None:
        return "Check error", 500

    if last is None:
        # Pehli baar run
        write_last_state(current)
        send_telegram(f"SHEIN cloud checker started. Current stock: {current}")
        return f"Initial set: {current}", 200

    # Agar pehle OUT OF STOCK tha aur ab IN STOCK
    if last is False and current is True:
        send_telegram("🔥 SHEIN CLOUD: STOCK AA GAYA! ✅")

    # Agar status change hua (True↔False)
    if last != current:
        send_telegram(f"SHEIN status changed: {last} → {current}")

    write_last_state(current)
    return f"Checked. Stock={current}", 200


if __name__ == "__main__":
    # Local test ke liye
    app.run(host="0.0.0.0", port=5000)
