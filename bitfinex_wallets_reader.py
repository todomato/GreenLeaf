#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bitfinex Wallets Reader (.env 版本)
----------------------------------------
此模組可被其他 python 檔案 import：
    from bitfinex_wallets_reader import get_wallets

會呼叫 Bitfinex API `/v2/auth/r/wallets`
回傳錢包資料（list）
"""

from datetime import datetime
import os
import json
import hmac
import hashlib
import requests
from dotenv import load_dotenv


# ---------------------------------------------------------
# 讀取 .env
# ---------------------------------------------------------
load_dotenv()

API = "https://api.bitfinex.com/v2"

API_KEY = os.getenv("BFX_API_KEY")
API_SECRET = os.getenv("BFX_API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError("❌ 無法讀取 API_KEY 或 API_SECRET，請確認 .env 檔內容")


# ---------------------------------------------------------
# 產生認證標頭
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# 主功能：取得錢包資料（給外部使用）
# ---------------------------------------------------------
def get_wallets():
    """
    呼叫 Bitfinex `/auth/r/wallets` API
    並直接回傳 Python list
    """
    endpoint = "auth/r/wallets"

    headers = {
        "Content-Type": "application/json",
        **_build_authentication_headers(endpoint)
    }

    response = requests.post(f"{API}/{endpoint}", headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"❌ API 錯誤：{response.status_code}\n{response.text}"
        )

    try:
        return response.json()
    except:
        raise Exception("❌ 無法解析 API JSON 回應")


# ---------------------------------------------------------
# 可以直接執行（測試用）
# ---------------------------------------------------------
if __name__ == "__main__":
    print("📡 取得 Bitfinex 錢包資料...\n")
    wallets = get_wallets()
    print(json.dumps(wallets, indent=2))
