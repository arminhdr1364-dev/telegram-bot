from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN
from keyboards import main_keyboard, coins_keyboard
from binance_api import get_price


# =========================
# تنظیمات
# =========================

search_users = set()


# =========================
# شروع ربات
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 به ربات قیمت ارزهای دیجیتال خوش آمدید.",
        reply_markup=main_keyboard()
    )


# =========================
# دریافت گیفت‌های تلگرام
# =========================

async def get_telegram_gifts():
    try:
        bot = Bot(TOKEN)

        gifts = await bot.get_available_gifts()

        if not gifts.gifts:
            return "❌ در حال حاضر گیفتی در دسترس نیست."

        text = "🎁 قیمت گیفت‌های تلگرام\n\n"

        for gift in gifts.gifts:
            text += (
                f"🎁 Gift ID: {gift.id}\n"
                f"⭐ قیمت: {gift.star_count} Stars\n\n"
            )

        return text

    except Exception as e:
        print("Gift Error:", e)
        return "❌ خطا در دریافت گیفت‌های تلگرام."


# =========================
# ارزهای محبوب
# =========================

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


# =========================
# نمایش قیمت ارز
# =========================

async def send_coin_price(update: Update, symbol: str):

    data = get_price(symbol)

    if data is None:
        await update.message.reply_text(
            "❌ دریافت اطلاعات این ارز ممکن نیست."
        )
        return

    try:
        change = float(data["change"]) * 100

        message = (
            f"💰 {data['symbol']}\n\n"
            f"💵 قیمت: {float(data['price']):,.6f} USDT\n\n"
            f"📈 تغییرات: {change:.2f}%\n\n"
            f"⬆️ بیشترین: {data['high']}\n\n"
            f"⬇️ کمترین: {data['low']}\n\n"
            f"📊 حجم معاملات: {data['volume']}"
        )

        await update.message.reply_text(
            message,
            reply_markup=coins_keyboard()
        )

    except Exception as e:
        print("Price Error:", e)

        await update.message.reply_text(
            "❌ خطا در نمایش اطلاعات ارز."
        )


# =========================
# جستجوی ارز و دکمه‌ها
# =========================

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message is None:
        return

    text = update.message.text.strip()
    user_id = update.effective_user.id

    # =========================
    # بازگشت
    # =========================

    if text == "🔙 بازگشت":

        search_users.discard(user_id)

        await update.message.reply_text(
            "🏠 به منوی اصلی برگشتید.",
            reply_markup=main_keyboard()
        )

        return

    # =========================
    # ارزهای محبوب
    # =========================

    if text == "⭐ ارزهای محبوب":

        search_users.discard(user_id)

        await update.message.reply_text(
            "⭐ یک ارز را انتخاب کنید:",
            reply_markup=coins_keyboard()
        )

        return

    # =========================
    # انتخاب ارز محبوب
    # =========================

    if text in coins:

        await send_coin_price(
            update,
            coins[text]
        )

        return

    # =========================
    # قیمت رمز ارز
    # =========================

    if text == "💰 قیمت رمز ارز":

        search_users.add(user_id)

        await update.message.reply_text(
            "🔍 نماد ارز را وارد کنید.\n\n"
            "مثال:\n"
            "BTC\n"
            "ETH\n"
            "TON\n\n"
            "یا:\n"
            "BTCUSDT"
        )

        return

    # =========================
    # راهنما
    # =========================

    if text == "ℹ️ راهنما":
        await update.message.reply_text(
            "ℹ️ راهنمای ربات\n\n"
            "💰 قیمت رمز ارز\n"
            "برای دریافت قیمت یک ارز، روی این گزینه بزنید "
            "و نماد ارز را ارسال کنید.\n\n"
            "⭐ ارزهای محبوب\n"
            "قیمت ارزهای محبوب را مشاهده کنید.\n\n"
            "🎁 قیمت گیفت تلگرام\n"
            "قیمت Giftها را بر اساس Telegram Stars مشاهده کنید."
        )

        return

    # =========================
    # گیفت تلگرام
    # =========================

    if text == "🎁 قیمت گیفت تلگرام":

        search_users.discard(user_id)

        await update.message.reply_text(
            "⏳ در حال دریافت قیمت گیفت‌ها از Telegram..."
        )

        gifts_text = await get_telegram_gifts()

        await update.message.reply_text(
            gifts_text,
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )

        return

    # =========================
    # پنل مدیریت
    # =========================

    if text == "👤 پنل مدیریت":

        search_users.discard(user_id)

        await update.message.reply_text(
            "🚧 پنل مدیریت در نسخه بعدی اضافه می‌شود.",
            reply_markup=main_keyboard()
        )

        return

    # =========================
    # اگر کاربر در حالت جستجو نیست
    # =========================

    if user_id not in search_users:
        return

    # =========================
    # جستجوی دستی
    # =========================

    symbol = text.upper().replace(" ", "")

    if not symbol.endswith("USDT"):
        symbol += "USDT"

    data = get_price(symbol)

    if data is None:

        await update.message.reply_text(
            "❌ ارز پیدا نشد.\n\n"
            "مثلاً BTC یا ETH را امتحان کنید."
        )

        search_users.discard(user_id)

        return

    try:

        change = float(data["change"]) * 100

        message = (
            f"💰 {data['symbol']}\n\n"
            f"💵 قیمت: {float(data['price']):,.6f} USDT\n\n"
            f"📈 تغییرات: {change:.2f}%\n\n"
            f"⬆️ بیشترین: {data['high']}\n\n"
            f"⬇️ کمترین: {data['low']}\n\n"
            f"📊 حجم معاملات: {data['volume']}"
        )

        await update.message.reply_text(
            message,
            reply_markup=main_keyboard()
        )

    except Exception as e:

        print("Search Price Error:", e)

        await update.message.reply_text(
            "❌ خطا در نمایش اطلاعات ارز."
        )

    search_users.discard(user_id)


# =========================
# اجرای ربات
# =========================

def main():

    app = Application.builder().token(TOKEN).build()

    # دستور /start
    app.add_handler(
        CommandHandler("start", start)
    )

    # پیام‌های متنی
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search
        )
    )

    print("🤖 Bot Started...")

    app.run_polling()


if __name__ == "__main__":
    main()




