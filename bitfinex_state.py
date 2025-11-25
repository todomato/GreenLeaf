#https://docs.bitfinex.com/reference/rest-public-funding-stats

import requests

API_BASE = "https://api-pub.bitfinex.com/v2"
def get_frr_history(symbol="fUSD", limit=50):
    """
    取得 Funding Flash Return Rate (FRR) 歷史資料

    symbol: 例如 "fUSD", "fBTC"
    limit: 回傳資料筆數
    """
    endpoint = f"/funding/stats/{symbol}/hist"
    params = {
        "limit": limit
    }
    url = API_BASE + endpoint
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    # 解析結果
    results = []
    for row in data:
        mts = row[0]
        frr_rate = row[3]  # index 3 是 FRR (rate)
        avg_period = row[4]  # index 4 是平均天數
        funding_amount = row[7]  # index 7 是提供資金總額
        used = row[8]  # index 8 是已使用金額

        annual_rate_percent = frr_rate * 365 * 100

        results.append({
            "timestamp": mts,
            "frr": frr_rate,
            "annual_rate_percent": annual_rate_percent,
            "avg_period": avg_period,
            "amount_provided": funding_amount,
            "amount_used": used
        })

    return results


if __name__ == "__main__":
    hist = get_frr_history("fUST", 1)
    for item in hist:
        print(item)
