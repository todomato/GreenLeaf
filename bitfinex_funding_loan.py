#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bitfinex Funding Loans API Wrapper
----------------------------------------
取得 **已確認借出的固定利率放貸訂單**，包含剩餘天數

Docs:
https://docs.bitfinex.com/reference/rest-auth-funding-loans
"""

import os
import json
import hmac
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load .env
load_dotenv()

API = "https://api.bitfinex.com/v2"
API_KEY = os.getenv("BFX_API_KEY")
API_SECRET = os.getenv("BFX_API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError("❌ Missing BFX_API_KEY or BFX_API_SECRET in .env")

def _build_auth_headers(endpoint, payload=None):
    nonce = str(round(datetime.now().timestamp() * 1000))
    message = f"/api/v2/{endpoint}{nonce}"

    if payload is not None:
        message += json.dumps(payload)

    sig = hmac.new(
        API_SECRET.encode(),
        message.encode(),
        hashlib.sha384
    ).hexdigest()

    return {
        "bfx-apikey": API_KEY,
        "bfx-nonce": nonce,
        "bfx-signature": sig
    }

def get_funding_loans(symbol="fUST", raw=False):
    """
    ✅ 取得固定利率 funding loans
    回傳格式：
    {
        "count": int,
        "items": [
            {
                "id": ...,
                "symbol": ...,
                "amount": ...,
                "rate_daily": ...,
                "rate_annual": ...,
                "period": ...,
                "status": ...,
                "remaining_time": "X 天"
            }
        ]
    }
    """

    endpoint = f"auth/r/funding/loans/{symbol}"

    headers = {
        "Content-Type": "application/json",
        **_build_auth_headers(endpoint)
    }

    response = requests.post(f"{API}/{endpoint}", headers=headers)

    if response.status_code != 200:
        raise Exception(f"❌ API Error {response.status_code}: {response.text}")

    data = response.json()

    if raw:
        return {
            "count": len(data),
            "items": data
        }

    results = []
    now_ms = int(datetime.now().timestamp() * 1000)

    for row in data:
        daily_rate = row[11] if len(row) > 11 and row[11] is not None else 0
        period = row[12] if len(row) > 12 else None
        create_ts = row[3] if len(row) > 3 else None

        # -----------------------------
        # 計算剩餘天數
        # -----------------------------
        if create_ts and period:
            elapsed_days = (now_ms - create_ts) / 1000 / 86400
            remaining_days = period - elapsed_days
            if remaining_days > 0:
                remain_str = f"{int(remaining_days)}天"
            else:
                remain_str = "已到期"
        else:
            remain_str = None

        results.append({
            "id": row[0],
            "symbol": row[1],
            "amount": row[5],
            "rate": daily_rate,
            "rate_annual": round(daily_rate * 365 * 100, 4),
            "period": period,
            "status": row[10] if len(row) > 10 else None,
            "created_timestamp": create_ts,
            "remaining_time": remain_str
        })

    return {
        "count": len(results),
        "items": results
    }


# ✅ 測試用
if __name__ == "__main__":
    resp = get_funding_loans("fUST")
    print("總筆數:", resp["count"])
    print(json.dumps(resp["items"], indent=2, ensure_ascii=False))
