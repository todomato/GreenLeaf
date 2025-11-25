from bitfinex_wallets_reader import get_wallets
from bitfinex_wallets_reader import get_funding_ust_values
from bitfinex_orderbook import get_orderbook
from bitfinex_rate_selector import find_max_apr
from bitfinex_funding_submit_offer import submit_funding_order

# -----------------------------
# 流程1：檢查餘額
# -----------------------------
wallets = get_wallets()
balance = get_funding_ust_values(wallets)

if not balance:
    raise ValueError("❌ 找不到 funding UST 餘額資料")

current_balance = balance[0]
print("📡 取得 Bitfinex 餘額資料:", current_balance)

# -----------------------------
# 流程2：取得訂單簿
# -----------------------------
orderbook = get_orderbook("fUST", "P1", 25)
print("📡 取得 Bitfinex Orderbook ...\n")

# -----------------------------
# 流程3：找到最高 APR
# -----------------------------
bestRate = find_max_apr(orderbook, 30)
print("最高 APR:", bestRate)

# -----------------------------
# 流程4：批次掛單
# -----------------------------
if current_balance > 150 and bestRate:
    print("✅ 執行批次掛單")

    rate = bestRate[0]
    period = bestRate[1]

    batch_size = 200
    remaining = current_balance

    offer_results = []
    batch_list = []

    # -----------------------------
    # 先切成 200 的分段
    # -----------------------------
    while remaining > 0:
        if remaining > batch_size:
            batch_list.append(batch_size)
            remaining -= batch_size
        else:
            batch_list.append(remaining)
            remaining = 0

    # -----------------------------
    # 處理「最後一筆 <150」→ 併入上一筆
    # -----------------------------
    if batch_list[-1] < 150 and len(batch_list) > 1:
        batch_list[-2] += batch_list[-1]
        batch_list.pop()  # 移除最後一筆（已併入）

    # -----------------------------
    # 逐筆掛單
    # -----------------------------
    for amount in batch_list:
        print(f"📌 掛單中: {amount} UST @ rate={rate}, period={period}")
        api_result = submit_funding_order(amount=amount, rate=rate, period=period)
        offer_results.append(api_result)

    print("\n==============================")
    print("📦 批次掛單完成")
    print("==============================")

    # -----------------------------
    # 輸出結果
    # -----------------------------
    for idx, result in enumerate(offer_results):
        status = result[6]        # SUCCESS
        description = result[7]   # 說明
        print(f"第 {idx+1} 筆 | 狀態: {status} | 說明: {description}")

else:
    print("⚠️ 不符合掛單條件")



# 流程2
# 發現高利率 -> # 取消所有掛單 -> # 檢查餘額 -> # 執行掛單


