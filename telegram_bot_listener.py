#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from bitfinex_wallets_reader import get_wallets, get_funding_ust_values
from bitfinex_funding_credits import get_funding_credits
from bitfinex_funding_loan import get_funding_loans
from bitfinex_state import get_frr_history
from bitfinex_orderbook import get_orderbook, get_top5_rates  # <- 新增匯入

TELEGRAM_TOKEN = os.getenv("TG_BOT_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ 未設定 TG_BOT_TOKEN，請放在 .env 或環境變數")

# ✅ /start 指令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot 已啟動，可輸入：\n"
        "📌 查詢餘額\n"
        "📌 查詢放貸\n"
        "📌 查詢利率"
    )

# ✅ 處理一般文字訊息
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # -----------------------------
    # 查詢餘額
    # -----------------------------
    if text == "查詢餘額":
        await update.message.reply_text("📡 正在查詢 Bitfinex 餘額...")
        try:
            wallets = get_wallets()
            values = get_funding_ust_values(wallets)

            if not values:
                await update.message.reply_text("❗ 沒找到 UST funding 餘額")
            else:
                await update.message.reply_text(f"✅ 目前餘額：{values[0]}")

        except Exception as e:
            await update.message.reply_text(f"❌ API 錯誤：\n{e}")

    # -----------------------------
    # 查詢放貸
    # -----------------------------
    elif text == "查詢放貸":
        await update.message.reply_text("📡 正在查詢放貸中，請稍候...")
        try:
            credits = get_funding_credits("fUST")
            loans = get_funding_loans("fUST")
            frr = get_frr_history("fUST")

            msg = (
                "📌 **fUST 放貸狀況**\n\n"
                f"🔹 變動利率：{credits['count']} 筆\n"
                f"🔸 固定利率：{loans['count']} 筆\n\n"
            )

            msg += "📍 變動利率明細：\n"
            for c in credits["items"]:
                msg += f"- {c['amount']} UST @ {frr['daily_frr_percent']}%, 年化: {frr['annual_frr_percent']}% / {c['remaining_time']}\n"

            msg += "\n📍 固定利率明細：\n"
            for l in loans["items"]:
                rate = l["rate"]
                annual = round(rate * 365, 3)
                msg += f"- {l['amount']} UST @ {rate}%, 年化:{annual}% / {l['remaining_time']}\n"

            await update.message.reply_text(msg)

        except Exception as e:
            await update.message.reply_text(f"❌ 查詢失敗：\n{e}")

    # -----------------------------
    # 新增查詢利率
    # -----------------------------
    elif text == "查詢利率":
        await update.message.reply_text("📡 正在查詢利率前五名，請稍候...")
        try:
            # 取得整理過的 orderbook
            orderbook = get_orderbook("fUST", "P1", 25)
            top5 = get_top5_rates(orderbook)

            frr = get_frr_history("fUST")

            msg = f"📊 查詢訂單簿：市場frr : {frr['daily_frr_percent']}%, 年化: {frr['annual_frr_percent']}% \n\n"
            for i, t in enumerate(top5, start=1):
                msg += (
                    f"{i}. 利率: {t['annual_rate_percent']:6.2f}% , "
                    f"期限: {t['period']:03d}天 , "
                    f"金額: {t['amount']:8.2f} UST\n"
                )

            await update.message.reply_text(msg)

        except Exception as e:
            await update.message.reply_text(f"❌ 查詢利率失敗：\n{e}")

    # -----------------------------
    # 其他文字
    # -----------------------------
    else:
        await update.message.reply_text(
            "🤖 我聽不懂，可以輸入：\n"
            "📌 查詢餘額\n"
            "📌 查詢放貸\n"
            "📌 查詢利率"
        )

# ✅ 主程式
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Telegram Bot 已啟動，等待訊息中...")
    app.run_polling()


if __name__ == "__main__":
    main()
