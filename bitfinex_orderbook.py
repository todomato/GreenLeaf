#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bitfinex Order Book Reader
--------------------------
官方文件：https://docs.bitfinex.com/reference/rest-public-book

此程式會呼叫 Bitfinex 公開 API `/v2/book/:symbol/:precision`
以取得指定交易對的即時 order book。

用法：
    python3 bitfinex_orderbook.py

可修改以下變數：
    SYMBOL     - 交易對 (例如 "tBTCUSD", "tETHUSD")
    PRECISION  - 精度 ("P0", "P1", "P2", "P3", "R0")
    LEN        - 返回的最大深度 (例如 25, 50, 100)
"""

import requests
import json
import copy

# === 可調參數 ===
SYMBOL = "fUST"   # BTC/USD
PRECISION = "P1"     # 精度 (越小越細)
LEN = 25             # 返回前幾筆

# === 主程式 ===
API = "https://api.bitfinex.com/v2"
endpoint = f"book/{SYMBOL}/{PRECISION}?len={LEN}"

print(f"📡 正在取得 Bitfinex Order Book: {SYMBOL} ({PRECISION}, len={LEN})")

response = requests.get(f"{API}/{endpoint}")

if response.status_code != 200:
    print(f"❌ 請求失敗，狀態碼 {response.status_code}")
    print(response.text)
else:
    data = response.json()
    print(f"✅ 成功取得 {len(data)} 筆資料\n")

    # 根據 precision，資料結構不同
    # P0~P3: [PRICE, COUNT, AMOUNT]
    # R0: [ORDER_ID, PRICE, AMOUNT]
    #print("📊 前幾筆 Order Book：")
    #print(json.dumps(data[:5], indent=2))

    # 整理
    def unique_by_index(data, idx):
        """
        取每個 data 中第 idx 個元素不重複的第一筆
        """
        result = []
        seen = set()
        
        for item in data:
            if len(item) <= idx:
                continue
            key = item[idx]
            if key not in seen:
                result.append(item)
                seen.add(key)
        return result

    def add_annual_rate_percent(data, rate_idx=0):
        """
        將 data 中第 rate_idx 個元素（日利率）轉成年利率百分比，
        並新增一欄
        """
        result = copy.deepcopy(data)
        
        for item in result:
            if len(item) > rate_idx:
                daily_rate = item[rate_idx]
                annual_rate = daily_rate * 365 
                item.append(round(annual_rate * 100, 2))  # 新增一欄年化百分比
        return result

    def process_data(data, unique_idx=1, rate_idx=0):
        """
        綜合處理：去重 + 日利率轉年化百分比（保留日利率）
        """
        unique_data = unique_by_index(data, unique_idx)
        final_data = add_annual_rate_percent(unique_data, rate_idx)
        return final_data

    # ===== 處理 =====
    processed = process_data(data, unique_idx=1, rate_idx=0)

    # ===== 輸出 =====
    print("📊 輸出整理 Order Book：")
    print(json.dumps(processed, indent=2))
