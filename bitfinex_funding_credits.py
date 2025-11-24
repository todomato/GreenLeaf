#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bitfinex Funding Credits API (callable version)
https://docs.bitfinex.com/reference/rest-auth-funding-credits
------------------------------------------------------------
外部可呼叫，用於取得變動利率放貸訂單
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

if not API_KEY or not API_SECRET:
    raise ValueError("❌ 沒找到 API_KEY / API_SECRET，請確認 .env 是否正確設定")


# -------------------------------------------------
# 建立簽章 headers
# -------------------------------------------------
def _build_auth_headers(endpoint, payload=None):
    nonce = str(round(datetime.now().timestamp() * 1000))
    message = f"/api/v2/{endpoint}{nonce}"

    if payload is not None:
        message += json.dumps(payload)

    signature = hmac.new(
        API_SECRET.encode("utf8"),
        message.encode("utf8"),
        hashlib.sha384
    ).hexdigest()

    return {
        "bfx-apikey": API_KEY,
        "bfx-nonce": nonce,
        "bfx-signature": signature
    }


# -------------------------------------------------
# ✅ 外部可呼叫的 API function
# -------------------------------------------------
def get_funding_credits(symbol="fUSD", raw=False):
    """
    取得變動利率 funding credits 訂單

    參數:
        symbol (str): e.g., "fUSD", "fUST"
        raw (bool): 如果想取得原始 API JSON，設 True

    回傳:
        list of dicts:
        [
            {
                "id": int,
                "symbol": str,
                "amount": float,
                "rate": float,
                "period": int,
                "status": str
            }
        ]
    """

    endpoint = f"auth/r/funding/credits/{symbol}"

    headers = {
        "Content-Type": "application/json",
        **_build_auth_headers(endpoint)
    }

    response = requests.post(f"{API}/{endpoint}", headers=headers)

    if response.status_code != 200:
        raise Exception(f"❌ API error: {response.status_code}\n{response.text}")

    data = response.json()

    if raw:
        return data  # 原始回傳

    results = []
    for row in data:
        results.append({
            "id": row[0],
            "symbol": row[1],
            "amount": row[5],
            "rate": row[15],   # 日利率 (小數)
            "period": row[16], # 天數
            "status": row[10]
        })

    return {
        "count": len(results),
        "items": results
    }


# -------------------------------------------------
# 測試用：只有直接執行才會跑
# -------------------------------------------------
if __name__ == "__main__":
    print("📡 測試取得 fUSD funding credits ...\n")
    resp = get_funding_credits("fUST")
    print("總筆數:", resp["count"])
    print(json.dumps(resp["items"], indent=2, ensure_ascii=False))

    
