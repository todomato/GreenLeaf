#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bitfinex Funding Balance Telegram Alert
----------------------------------------
使用方式：
    python3 telegram_balance_alert.py

功能：
1. 呼叫 bitfinex_wallets_reader.get_wallets()
2. 篩選 funding/UST 餘額
3. 若有任一餘額 > 150，發送 Telegram 通知
"""

import os
import requests
from dotenv import load_dotenv
from bitfinex_wallets_reader import get_wallets, get_funding_ust_values

# ---------------------------------------------------------
# 讀取 .env
# ---------------------------------------------------------
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TG_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("❌ TG_BOT_TOKEN 或 TG_CHAT_ID 未設定，請確認 .env")

# ---------------------------------------------------------
# 發送 Telegram 訊息
# ---------------------------------------------------------
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    requests.post(url, json=payload)

# ---------------------------------------------------------
# 主流程
# ---------------------------------------------------------
def check_funding_balance(threshold=1):
    wallets = get_wallets()
    values = get_funding_ust_values(wallets)

    if not values:
        print("⚠️ 找不到任何 funding/UST 資料")
        return

    for v in values:
        if v > threshold:
            msg = f"🚨 Funding UST 餘額警告：{v} (> {threshold})"
            print(msg)
            send_telegram_message(msg)
        else:
            print(f"✅ {v} 小於 {threshold}，不通知")

# ---------------------------------------------------------
# 可直接執行
# ---------------------------------------------------------
if __name__ == "__main__":
    check_funding_balance()
