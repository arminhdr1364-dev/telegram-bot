from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN
from keyboards import main_keyboard, coins_keyboard
from binance_api import get_price
search_users = set()
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 به ربات قیمت ارزهای دیجیتال خوش آمدید.",
        reply_markup=main_keyboard()
    )
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "search":
        search_users.add(query.from_user.id)

        await query.message.reply_text(
            "🔍 نام ارز را وارد کنید.\n\nمثال:\nBTCUSDT\nETHUSDT\nTONUSDT"
        )

    elif query.data == "help":
        await query.message.reply_text(
            "نام هر ارز را به صورت BTCUSDT یا ETHUSDT ارسال کنید."
        )

    elif query.data == "gift":
        await query.message.reply_text(
            "🚧 بخش قیمت گیفت تلگرام به‌زودی اضافه می‌شود."
        )

    elif query.data == "admin":
        await query.message.reply_text(
            "🚧 پنل مدیریت در نسخه بعدی اضافه می‌شود."
        )
coins = {
    "🟠 BTC": "BTCUSDT",
    "🔵 ETH": "ETHUSDT",
    "🟣 SOL": "SOLUSDT",
    "⚫ BNB": "BNBUSDT",
    "🟢 XRP": "XRPUSDT",
    "🟡 DOGE": "DOGEUSDT",
    "💎 TON": "TONUSDT",
    "🔴 TRX": "TRXUSDT",
}

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    # بازگشت
    if text == "🔙 بازگشت":
        search_users.discard(update.effective_user.id)

        await update.message.reply_text(
            "🏠 به منوی اصلی برگشتید.",
            reply_markup=main_keyboard()
        )
        return

    # ارزهای محبوب
    if text == "⭐ ارزهای محبوب":
        await update.message.reply_text(
            "⭐ یک ارز را انتخاب کنید:",
            reply_markup=coins_keyboard()
        )
        return

    # انتخاب ارزهای محبوب
    if text in coins:

        data = get_price(coins[text])

        if data is None:
            await update.message.reply_text("❌ دریافت اطلاعات ممکن نیست.")
            return

        change = float(data["change"]) * 100

        await update.message.reply_text(
            f"""💰 {data['symbol']}

💵 قیمت: {float(data['price']):,.6f} USDT

📈 تغییرات: {change:.2f} %

⬆️ بیشترین: {data['high']}

⬇️ کمترین: {data['low']}

📊 حجم معاملات: {data['volume']}""",
            reply_markup=coins_keyboard()
        )
        return

    # جستجوی دستی
    if text == "💰 قیمت رمز ارز":
        search_users.add(update.effective_user.id)

        await update.message.reply_text(
            "🔍 نماد ارز را وارد کنید.\n\nمثال:\nBTC\nETH\nTON"
        )
        return

    # راهنما
    if text == "ℹ️ راهنما":
        await update.message.reply_text(
            "برای مشاهده قیمت، روی «💰 قیمت رمز ارز» بزنید."
        )
        return

    # گیفت
    if text == "🎁 قیمت گیفت تلگرام":
        await update.message.reply_text(
            "🚧 این بخش به زودی اضافه می‌شود."
        )
        return

    # پنل مدیریت
    if text == "👤 پنل مدیریت":
        await update.message.reply_text(
            "🚧 این بخش در نسخه بعدی اضافه می‌شود."
        )
        return

    # اگر در حالت جستجو نیست
    if update.effective_user.id not in search_users:
        return

    symbol = text.upper()

    if not symbol.endswith("USDT"):
        symbol += "USDT"

    data = get_price(symbol)

    if data is None:
        await update.message.reply_text("❌ ارز پیدا نشد.")
        search_users.discard(update.effective_user.id)
        return

    change = float(data["change"]) * 100

    await update.message.reply_text(
        f"""💰 {data['symbol']}

💵 قیمت: {float(data['price']):,.6f} USDT

📈 تغییرات: {change:.2f} %

⬆️ بیشترین: {data['high']}

⬇️ کمترین: {data['low']}

📊 حجم معاملات: {data['volume']}""",
        reply_markup=main_keyboard()
    )

    search_users.discard(update.effective_user.id)



app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))

print("🤖 Bot Started...")

app.run_polling()