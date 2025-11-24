#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bitfinex Funding Offers Reader / Order Executor
-----------------------------------------------
可被其他 Python 檔案 import：

from bitfinex_orders_api import get_funding_offers

功能：
1️⃣ 取得 fUST funding offers
2️⃣ 回傳 Python list
"""

from datetime import datetime
import os
import json
import hmac
import hashlib
import requests
from dotenv import load_dotenv

# ----------------------------
# 載入環境變數
# ----------------------------
load_dotenv()

API = "https://api.bitfinex.com/v2"

API_KEY = os.getenv("BFX_API_KEY")
API_SECRET = os.getenv("BFX_API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError("❌ 無法讀取 API_KEY 或 API_SECRET，請確認 .env 檔內容")

# ----------------------------
# 產生認證標頭
# ----------------------------
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

# ----------------------------
# 取得 funding offers
# ----------------------------
def get_funding_offers():
    """
    取得帳戶 fUST funding offers
    回傳 Python list
    """
    endpoint = "auth/r/funding/offers/fUST"

    headers = {
        "Content-Type": "application/json",
        **_build_authentication_headers(endpoint)
    }

    response = requests.post(f"{API}/{endpoint}", headers=headers)

    if response.status_code != 200:
        raise Exception(f"❌ API 錯誤：{response.status_code}\n{response.text}")

    try:
        return response.json()
    except Exception as e:
        raise Exception(f"❌ 無法解析 API JSON 回應: {e}")

# ----------------------------
# 可選：執行掛單
# ----------------------------
def submit_funding_order(amount, rate, period):
    """
    執行 fUST funding order
    amount: float, 貸款數量
    rate: float, 日利率
    period: int, 借貸天數

    回傳 API 回應
    """
    endpoint = "auth/w/order/submit"

    payload = {
        "type": "FUNDING OFFER",
        "symbol": "fUST",
        "amount": str(amount),
        "rate": str(rate),
        "period": period
    }

    headers = {
        "Content-Type": "application/json",
        **_build_authentication_headers(endpoint, payload)
    }

    response = requests.post(f"{API}/{endpoint}", json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"❌ API 錯誤：{response.status_code}\n{response.text}")

    try:
        return response.json()
    except Exception as e:
        raise Exception(f"❌ 無法解析 API JSON 回應: {e}")

# ----------------------------
# 測試用
# ----------------------------
if __name__ == "__main__":
    offers = get_funding_offers()
    print(json.dumps(offers, indent=2))
