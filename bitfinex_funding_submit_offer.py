# https://docs.bitfinex.com/reference/rest-auth-info-funding
"""
發送訂單

"""

from datetime import datetime
import os,time
import json
import hmac
import hashlib
import requests
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

API = "https://api.bitfinex.com/v2"

API_KEY = os.getenv("BFX_API_KEY")
API_SECRET = os.getenv("BFX_API_SECRET")
print(API_KEY)
print(API_SECRET)

if not API_KEY or not API_SECRET:
    raise ValueError("❌ 無法讀取 API_KEY 或 API_SECRET，請確認 .env 檔內容")

def _build_authentication_headers(endpoint, payload=None):
    nonce = str(round(datetime.now().timestamp() * 1_000))
    message = f"/api/v2/{endpoint}{nonce}"

    if payload is not None:
        message += json.dumps(payload)

    signature = hmac.new(
        key=API_SECRET.encode("utf8"),
        msg=message.encode("utf8"),
        digestmod=hashlib.sha384
    ).hexdigest()

    return {
        "bfx-apikey": API_KEY,
        "bfx-nonce": nonce,
        "bfx-signature": signature
    }

def get_wallets():
    endpoint = "auth/w/funding/offer/submit"

    # 動態
    payload = {
        "type": "FRRDELTAVAR",
        "symbol": "fUST",
        "amount": "302.83",
        "rate": "0",
        "period": 20,
        "flags": 0
    } 

    # 自訂
    # payload = {
    #     "type": "LIMIT",
    #     "symbol": "fUST",
    #     "amount": "150",
    #     "rate": "0.0003673",
    #     "period": 20,
    #     "flags": 0
    # } 

    headers = {
        "Content-Type": "application/json",
        **_build_authentication_headers(endpoint, payload)
    }

    print("💰 正在讀取 Bitfinex 送單資訊 ...")
    response = requests.post(f"{API}/{endpoint}", headers=headers, json=payload)

    try:
        data = response.json()
        print("✅ 回應內容：")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("⚠️ 無法解析伺服器回應:", e)
        print(response.text)

if __name__ == "__main__":
    get_wallets()
