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


def get_funding_credits(symbol="fUSD", raw=False):

    endpoint = f"auth/r/funding/credits/{symbol}"
    headers = {"Content-Type": "application/json", **_build_auth_headers(endpoint)}
    response = requests.post(f"{API}/{endpoint}", headers=headers)

    if response.status_code != 200:
        raise Exception(f"❌ API error: {response.status_code}\n{response.text}")

    data = response.json()
    if raw:
        return data

    results = []
    now_ms = int(datetime.now().timestamp() * 1000)

    for row in data:
        daily_rate = row[11] if len(row) > 11 and row[11] is not None else 0
        period = row[12] if len(row) > 12 else None   # days
        create_ts = row[3] if len(row) > 3 else None  # creation time (ms)

        # -----------------------------
        # ✅ 計算剩餘天數
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
            "remaining_time": remain_str  # ⭐ 只顯示天數
        })

    return {
        "count": len(results),
        "items": results
    }


# 測試
if __name__ == "__main__":
    resp = get_funding_credits("fUST")
    print(json.dumps(resp, indent=2, ensure_ascii=False))
