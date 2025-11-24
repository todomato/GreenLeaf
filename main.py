from bitfinex_wallets_reader import get_wallets
from bitfinex_wallets_reader import get_funding_ust_values
from bitfinex_orderbook import get_orderbook
from bitfinex_rate_selector import find_max_apr

# 流程1

# -----------------------------
# 流程1：檢查餘額
# -----------------------------
wallets = get_wallets()
balance = get_funding_ust_values(wallets)

if not balance:
    raise ValueError("❌ 找不到 funding UST 餘額資料")

current_balance = balance[0]
print("📡 取得 Bitfinex 餘額資料 : ", current_balance)

# -----------------------------
# 流程2：取得訂單簿
# -----------------------------
orderbook = get_orderbook("fUST", "P1", 25)
print("📡 取得 Bitfinex Orderbook ...\n")
# print(orderbook)

# -----------------------------
# 流程3：找到最高 APR
# -----------------------------
bestRate = find_max_apr(orderbook, 30)
print("最高 APR：", bestRate)

# -----------------------------
# 流程4：檢查條件並執行掛單
# -----------------------------
if current_balance > 150 and bestRate:
    print("✅ 執行掛單")
    # 可抓取掛單參數
    # daily_rate = bestRate[0]
    # period = bestRate[1]
    # amount = current_balance
    # price = ...  # 如果需要可以再計算或設定
else:
    print("⚠️ 不符合掛單條件")



# 流程2
# 發現高利率 -> # 取消所有掛單 -> # 檢查餘額 -> # 執行掛單


