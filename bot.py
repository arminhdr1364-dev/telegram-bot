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


search_users = set()


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
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 به ربات قیمت ارزهای دیجیتال خوش آمدید.\n\n"
        "💰 قیمت رمز ارز\n"
        "⭐ ارزهای محبوب\n"
        "🎁 قیمت گیفت تلگرام",
        reply_markup=main_keyboard()
    )


# =========================
# Telegram Gifts
# =========================

async def get_telegram_gifts():

    try:

        bot = Bot(TOKEN)

        gifts = await bot.get_available_gifts()

        if not gifts.gifts:

            return "❌ در حال حاضر Giftای موجود نیست."

        text = (
            "🎁 <b>Telegram Gifts</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
        )

        text += (
            f"📦 تعداد Giftها: "
            f"<b>{len(gifts.gifts)}</b>\n\n"
        )

        for number, gift in enumerate(
            gifts.gifts,
            start=1
        ):

            gift_id = gift.id
            stars = gift.star_count

            text += (
                f"🎁 <b>Gift #{number}</b>\n"
                f"🆔 ID: <code>{gift_id}</code>\n"
                f"⭐ قیمت: <b>{stars} Stars</b>\n"
            )

            # استیکر
            if gift.sticker:

                emoji = gift.sticker.emoji

                text += (
                    f"🖼 استیکر: "
                    f"{emoji or 'موجود'}\n"
                )

            else:

                text += (
                    "🖼 استیکر: موجود نیست\n"
                )

            text += (
                "━━━━━━━━━━━━━━━━━━\n"
            )

        text += (
            "\n🔄 اطلاعات مستقیماً از Telegram دریافت شد.\n"
            "⭐ قیمت‌ها بر اساس Telegram Stars هستند."
        )

        return text

    except Exception as e:

        print(
            "GIFT ERROR:",
            repr(e)
        )

        return (
            "❌ خطا در دریافت Giftهای Telegram.\n\n"
            "خطا در کنسول Railway ثبت شده است."
        )


# =========================
# نمایش قیمت ارز
# =========================

async def send_coin_price(
    update: Update,
    symbol: str
):

    try:

        data = get_price(symbol)

        if data is None:

            await update.message.reply_text(
                "❌ دریافت اطلاعات ارز ممکن نیست."
            )

            return

        change = float(data["change"]) * 100
        price = float(data["price"])

        message = (
            f"💰 {data['symbol']}\n\n"
            f"💵 قیمت: {price:,.6f} USDT\n\n"
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

        print(
            "PRICE ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ خطا در دریافت قیمت."
        )


# =========================
# مدیریت پیام‌ها
# =========================

async def search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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

        search_users.discard(user_id)

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
            "TON"
        )

        return


    # =========================
    # راهنما
    # =========================

    if text == "ℹ️ راهنما":

        await update.message.reply_text(
            "ℹ️ راهنمای ربات\n\n"
            "💰 قیمت رمز ارز\n"
            "برای دریافت قیمت، نماد ارز را ارسال کنید.\n\n"
            "⭐ ارزهای محبوب\n"
            "قیمت ارزهای محبوب را ببینید.\n\n"
            "🎁 قیمت گیفت تلگرام\n"
            "Giftهای قابل ارسال و قیمت Stars آنها نمایش داده می‌شود."
        )

        return


    # =========================
    # Telegram Gifts
    # =========================

    if text == "🎁 قیمت گیفت تلگرام":

        search_users.discard(user_id)

        loading = await update.message.reply_text(
            "⏳ در حال دریافت Giftها از Telegram..."
        )

        gifts_text = await get_telegram_gifts()

        try:
            await loading.delete()
        except Exception:
            pass

        await update.message.reply_text(
            gifts_text,
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

        return


    # =========================
    # پنل مدیریت
    # =========================

    if text == "👤 پنل مدیریت":

        await update.message.reply_text(
            "🚧 پنل مدیریت در نسخه بعدی اضافه می‌شود.",
            reply_markup=main_keyboard()
        )

        return


    # =========================
    # اگر حالت جستجو فعال نیست
    # =========================

    if user_id not in search_users:
        return


    # =========================
    # جستجوی ارز
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
        price = float(data["price"])

        message = (
            f"💰 {data['symbol']}\n\n"
            f"💵 قیمت: {price:,.6f} USDT\n\n"
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

        print(
            "SEARCH ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ خطا در نمایش قیمت."
        )

    search_users.discard(user_id)


# =========================
# اجرای ربات
# =========================

def main():

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )
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



