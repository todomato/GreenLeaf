#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bitfinex Public API – Funding Flash Return Rate (FRR)
https://docs.bitfinex.com/reference/rest-public-funding-stats
"""

import requests

API_BASE = "https://api-pub.bitfinex.com/v2"

def get_frr_history(symbol="fUST", limit=1):
    """
    取得 Funding Flash Return Rate (FRR) 歷史資料（只取第一筆）
    """

    endpoint = f"/funding/stats/{symbol}/hist"
    params = {"limit": limit}

    url = API_BASE + endpoint
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    if not data:
        return None

    row = data[0]  # 只取第一筆

    mts = row[0]            # timestamp (ms)
    frr_rate = row[3]       # FRR 日利率 (rate per day)
    avg_period = row[4]     # 平均借款天數
    funding_amount = row[7] # 可用資金
    used = row[8]           # 已使用資金

    # 四捨五入到小數點第二位
    daily_rate_percent = round(frr_rate * 100 * 365, 4)
    annual_rate_percent = round(daily_rate_percent * 365, 3)

    result = {
        "timestamp": mts,
        "daily_frr_percent": daily_rate_percent,
        "annual_frr_percent": annual_rate_percent,
        "avg_period": avg_period,
        "amount_provided": funding_amount,
        "amount_used": used
    }

    return result


# 測試用
if __name__ == "__main__":
    hist = get_frr_history("fUST")
    print(hist)
    print(hist["daily_frr_percent"])
