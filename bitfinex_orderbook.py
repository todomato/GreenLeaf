#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
取得訂單簿
--------------------------
官方文件：
https://docs.bitfinex.com/reference/rest-public-book

此檔案拆成可供 import 的模組：
    from bitfinex_orderbook import get_orderbook, get_top5_rates
"""

import requests
import json
import copy


API = "https://api.bitfinex.com/v2"


# ---------------------------------------------------------
# 工具方法
# ---------------------------------------------------------

def unique_by_index(data, idx):
    """取每個 data 中第 idx 個元素不重複的第一筆"""
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
    data 中第 rate_idx 個元素（日利率）轉成年利率百分比
    並新增一欄 annual_rate_percent
    """
    result = copy.deepcopy(data)
    
    for item in result:
        if len(item) > rate_idx:
            daily_rate = item[rate_idx]
            annual_rate = daily_rate * 365
            item.append(round(annual_rate * 100, 2))  # 新增：年化（％）
    return result


def process_data(data, unique_idx=1, rate_idx=0):
    """整合：去重 + 年化"""
    unique_data = unique_by_index(data, unique_idx)
    final_data = add_annual_rate_percent(unique_data, rate_idx)
    return final_data


# ---------------------------------------------------------
# 主要 API 函式（給其他檔案呼叫）
# ---------------------------------------------------------

def get_orderbook(symbol="fUST", precision="P1", length=25):
    """
    呼叫 Bitfinex Orderbook + 自動整理資料
    回傳 Python list
    """
    endpoint = f"book/{symbol}/{precision}?len={length}"
    url = f"{API}/{endpoint}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"API 錯誤：{response.status_code} - {response.text}")

    raw = response.json()
    processed = process_data(raw, unique_idx=1, rate_idx=0)
    return processed   # ← 給 main.py 用


# ---------------------------------------------------------
# 新增函式：取得前五筆利率最高
# ---------------------------------------------------------

def get_top5_rates(orderbook):
    """
    從整理過的 orderbook 取得前五筆年化利率最高的資料
    回傳 list of dict:
        {
            "annual_rate_percent": ...,
            "period": ...,
            "amount": ...
        }
    """
    # 排序：按年化利率降序
    sorted_data = sorted(orderbook, key=lambda x: x[4], reverse=True)
    top5 = sorted_data[:5]

    # 提取需要欄位
    result = []
    for item in top5:
        result.append({
            "annual_rate_percent": item[4],
            "period": item[1],
            "amount": round(abs(item[3]))
        })
    return result


# ---------------------------------------------------------
# 可直接執行測試
# ---------------------------------------------------------

if __name__ == "__main__":
    print("📡 測試取得 Bitfinex Orderbook ...")
    data = get_orderbook("fUST", "P1", 25)
    print("📊 整理後 Orderbook：")
    print(json.dumps(data, indent=2))

    print("\n🔥 前五筆利率最高：")
    top5 = get_top5_rates(data)
    print(json.dumps(top5, indent=2))
