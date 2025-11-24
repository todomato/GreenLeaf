#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bitfinex Active Funding Credits with APR
----------------------------------------
自動篩選 ACTIVE 放貸，並計算日利率 / 年化利率百分比
"""

from datetime import datetime
import os
import json
import hmac
import hashlib
import requests
from dotenv import load_dotenv

# -----------------------------
# 載入 .env
# -----------------------------
load_dotenv()

API = "https://api.bitfinex.com/v2"

API_KEY = os.getenv("BFX_API_KEY")
API_SECRET = os.getenv("BFX_API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError("❌ 無法讀取 API_KEY 或 API_SECRET，請確認 .env 檔內容")

# -----------------------------
# 認證 headers
# -----------------------------
def _build_authentication_headers(endpoint, payload=None):
    nonce = str(round(datetime.now().timestamp() * 1000))
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

# -----------------------------
# 取得 funding credits history
# -----------------------------
def get_funding_credits(symbol="fUST", limit=50):
    """
    取得放貸紀錄並計算日利率/年化率

    回傳：
        list of dicts:
        [
            {
                "rate": float,                # 日利率
                "annual_rate_percent": float, # 年化百分比
                "period": int,                # 放貸天數
                "amount": float,              # 放貸金額
                "status": str                 # ACTIVE / CLOSE
            },
            ...
        ]
    """
    endpoint = f"auth/r/funding/credits/{symbol}/hist"

    payload = {"limit": limit}

    headers = {
        "Content-Type": "application/json",
        **_build_authentication_headers(endpoint, payload)
    }

    response = requests.post(f"{API}/{endpoint}", headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"❌ API 錯誤: {response.status_code}\n{response.text}")

    data = response.json()
    results = []

    for item in data:
        # item[10] 是 status
        status = item[10]
        if status != "ACTIVE":
            continue

        rate = item[15]       # 日利率
        period = item[16]     # 天數
        amount = item[5]      # 放貸金額
        annual_rate_percent = round(rate * 365 * 100, 2)

        results.append({
            "rate": rate,
            "annual_rate_percent": annual_rate_percent,
            "period": period,
            "amount": amount,
            "status": status
        })

    return results

# -----------------------------
# 測試用
# -----------------------------
if __name__ == "__main__":
    symbol = "fUSD"
    print(f"📡 取得 {symbol} ACTIVE 放貸紀錄...")
    active_credits = get_funding_credits(symbol=symbol, limit=500)
    print(json.dumps(active_credits, indent=2))
