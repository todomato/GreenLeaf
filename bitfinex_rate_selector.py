#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bitfinex APR Selector
---------------------
給定以下格式的陣列：
[
    [daily_rate, period, something, amount, annual_rate_percent],
    ...
]

功能：
    找出 annual_rate_percent (index 4) 最大的那一筆 array
    並回傳該 array

使用方法（在其他檔案）：
    from bitfinex_rate_selector import find_max_apr
    best = find_max_apr(data)
"""

def find_max_apr(data, max_days=None):
    """
    傳入：
        data: list of lists
        max_days: (int | None) 例如 30，表示只考慮 period <= 30 的資料

    回傳：
        年化率最高的那筆 array (符合 max_days 條件)
        如果沒有符合條件則回傳 None
    """
    if not data or not isinstance(data, list):
        raise ValueError("❌ find_max_apr(data) 需要傳入非空的 list")

    best_item = None
    best_apr = float("-inf")

    for item in data:
        if len(item) < 5:
            continue  # 沒有年化率欄位

        period = item[1]
        apr = item[4]

        # ✅ 如果有指定 max_days，就要過濾
        if max_days is not None and period > max_days:
            continue

        if apr > best_apr:
            best_apr = apr
            best_item = item

    return best_item



# ---------------------------------------------------------
# 測試用（直接執行）
# ---------------------------------------------------------
if __name__ == "__main__":
    sample_data = [
        [0.0003965, 20, 1, -2026983.51368533, 14.47],
        [0.0003287, 120, 2, -3705002.31490664, 12.0],
        [0.0002021, 59, 1, -198984.73163536, 7.38],
        [0.0001865, 15, 1, -150447.89574246, 6.81],
        [0.000182, 30, 3, -15000, 6.64],
        [0.000161, 3, 1, -262924.99245563, 5.88],
        [0.0001515, 109, 1, -235121.40850379, 5.53],
        [0.0001511, 29, 1, -450000, 5.52],
        [0.0001485, 2, 1, -554.32162038, 5.42],
    ]

    best = find_max_apr(sample_data)
    print("📌 年化率最高的一筆：")
    print(best)
