#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from bitfinex_wallets_reader import get_wallets, get_funding_ust_values

TELEGRAM_TOKEN = os.getenv("TG_BOT_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ 未設定 TG_BOT_TOKEN，請放在 .env 或環境變數")

# ✅ /start 指令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot 已啟動，有什麼需要嗎？輸入：查詢餘額")

# ✅ 處理一般文字訊息
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "查詢餘額":
        await update.message.reply_text("📡 正在查詢 Bitfinex 餘額...")

        try:
            wallets = get_wallets()
            values = get_funding_ust_values(wallets)

            if not values:
                await update.message.reply_text("❗ 沒找到 UST funding 餘額")
            else:
                await update.message.reply_text(f"✅ 目前餘額：{values}")

        except Exception as e:
            await update.message.reply_text(f"❌ API 錯誤：\n{e}")

    else:
        await update.message.reply_text("🤖 我聽不懂，可以輸入：查詢餘額")

# ✅ 主程式
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Telegram Bot 已啟動，等待訊息中...")
    app.run_polling()

if __name__ == "__main__":
    main()
