from bitfinex_wallets_reader import get_wallets
from bitfinex_orderbook import get_orderbook
from bitfinex_rate_selector import find_max_apr

# 流程1

# 檢查餘額 
wallets = get_wallets()
print("📡 取得 Bitfinex 錢包資料...\n")
print(wallets)

# 取得訂單簿
orderbook = get_orderbook("fUST", "P1", 25)
print("📡 取得 Bitfinex Orderbook ...\n")
print(orderbook)

# 檢查是否需要掛單，並取得相關參數
    # (金額 > $150 & 好的利率)
best = find_max_apr(orderbook)
print("最高 APR：", best)

# 執行掛單


# 流程2
# 發現高利率 -> # 取消所有掛單 -> # 檢查餘額 -> # 執行掛單


