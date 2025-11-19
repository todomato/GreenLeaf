# 參考綠葉API文件
# https://docs.bitfinex.com/reference/rest-auth-info-funding


https://api.bitfinex.com/v2/auth/r/summary
https://api.bitfinex.com/v2/auth/r/ledgers/{Currency}/hist
Ledgers


# 功能1 : 啟用掛單
1. 取消當前所有掛單
2. 查詢帳戶餘額
    3. 有餘額
        4. 查詢目前利率 (2~30天的最高利率)
        5. 依輸入條件掛單 (分批掛單，每筆金額，150~300元)

# 功能2 : 取消掛單
1. 取消當前所有掛單

# 功能3 : 定期檢查餘額
1. 每5分鐘檢查餘額
    2.有餘額
        3. 啟用"功能1"

# 紀錄介面
1. 基本資料:總金額、餘額
2. 每日利息、每日年化、總資金年化
3. 每日快照

# Tel 提醒功能
1. 還款提醒
2. 放款成功提醒
3. 高利提醒
