#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bitfinex Wallets Reader (.env 版本)
----------------------------------------
此程式會呼叫 Bitfinex API `/v2/auth/r/wallets`
以取得帳戶的錢包與餘額資訊。

使用前請：
1️⃣ 安裝套件：
    pip install python-dotenv requests

2️⃣ 在同資料夾下建立 `.env` 檔：
    BFX_API_KEY=你的API_KEY
    BFX_API_SECRET=你的API_SECRET

3️⃣ 執行：
    python3 bitfinex_wallets_reader.py
"""

from datetime import datetime
import os
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
    endpoint = "auth/r/wallets"
    payload = {}  # 此端點不需 payload

    headers = {
        "Content-Type": "application/json",
        **_build_authentication_headers(endpoint)
    }

    print("💰 正在讀取 Bitfinex 錢包資訊 ...")
    response = requests.post(f"{API}/{endpoint}", headers=headers)

    try:
        data = response.json()
        print("✅ 回應內容：")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("⚠️ 無法解析伺服器回應:", e)
        print(response.text)

if __name__ == "__main__":
    get_wallets()
