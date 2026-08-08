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


# ==========================================
# کاربران در حالت جستجوی ارز
# ==========================================

search_users = set()


# ==========================================
# ارزهای محبوب
# ==========================================

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


# ==========================================
# START
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 <b>به ربات قیمت ارزهای دیجیتال خوش آمدید.</b>\n\n"
        "💰 قیمت رمز ارز\n"
        "⭐ ارزهای محبوب\n"
        "🎁 قیمت گیفت تلگرام\n\n"
        "📊 اطلاعات از سرویس‌های مربوطه دریافت می‌شود.",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


# ==========================================
# ارسال Giftهای Telegram
# ==========================================

async def send_telegram_gifts(update: Update):

    try:

        bot = Bot(TOKEN)

        # دریافت Giftها
        gifts = await bot.get_available_gifts()

        if not gifts.gifts:

            await update.message.reply_text(
                "❌ در حال حاضر Giftای در دسترس نیست."
            )

            return

        # پیام اولیه
        await update.message.reply_text(
            "🎁 <b>Telegram Gifts</b>\n\n"
            f"📦 تعداد Giftها: "
            f"<b>{len(gifts.gifts)}</b>\n"
            "⭐ قیمت‌ها بر اساس Telegram Stars هستند.",
            parse_mode="HTML"
        )

        # ارسال تک‌تک Giftها
        for number, gift in enumerate(
            gifts.gifts,
            start=1
        ):

            sticker = gift.sticker

            # --------------------------
            # اگر Sticker وجود نداشت
            # --------------------------

            if sticker is None:

                await update.message.reply_text(
                    f"🎁 <b>Gift #{number}</b>\n\n"
                    f"🆔 ID: <code>{gift.id}</code>\n"
                    f"⭐ قیمت: "
                    f"<b>{gift.star_count}</b> Stars\n\n"
                    "🖼 استیکر در دسترس نیست.",
                    parse_mode="HTML"
                )

                continue

            # --------------------------
            # اطلاعات Gift
            # --------------------------

            caption = (
                f"🎁 <b>Gift #{number}</b>\n\n"
                f"🆔 ID: <code>{gift.id}</code>\n"
                f"⭐ قیمت: "
                f"<b>{gift.star_count}</b> Stars"
            )

            # --------------------------
            # ارسال Sticker
            # --------------------------

            try:

                await update.message.reply_sticker(
                    sticker=sticker.file_id
                )

            except Exception as sticker_error:

                print(
                    "Sticker Error:",
                    repr(sticker_error)
                )

                await update.message.reply_text(
                    "🖼 ارسال استیکر این Gift ممکن نبود."
                )

            # --------------------------
            # ارسال اطلاعات
            # --------------------------

            await update.message.reply_text(
                caption,
                parse_mode="HTML"
            )

        # پایان
        await update.message.reply_text(
            "✅ <b>لیست Giftها به پایان رسید.</b>",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

    except Exception as e:

        print(
            "GIFT ERROR:",
            repr(e)
        )
        await update.message.reply_text(
            "❌ خطا در دریافت Giftهای Telegram.\n\n"
            "جزئیات خطا در Railway Logs ثبت شده است.",
            reply_markup=main_keyboard()
        )


# ==========================================
# نمایش قیمت ارز
# ==========================================

async def send_coin_price(
    update: Update,
    symbol: str
):

    try:

        data = get_price(symbol)

        if data is None:

            await update.message.reply_text(
                "❌ اطلاعات این ارز پیدا نشد.",
                reply_markup=main_keyboard()
            )

            return

        change = float(
            data["change"]
        ) * 100

        price = float(
            data["price"]
        )

        message = (
            f"💰 <b>{data['symbol']}</b>\n\n"
            f"💵 قیمت: "
            f"<b>{price:,.6f}</b> USDT\n\n"
            f"📈 تغییرات: "
            f"<b>{change:.2f}%</b>\n\n"
            f"⬆️ بیشترین: "
            f"{data['high']}\n\n"
            f"⬇️ کمترین: "
            f"{data['low']}\n\n"
            f"📊 حجم معاملات: "
            f"{data['volume']}"
        )

        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=coins_keyboard()
        )

    except Exception as e:

        print(
            "PRICE ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ خطا در دریافت قیمت ارز.",
            reply_markup=main_keyboard()
        )


# ==========================================
# مدیریت پیام‌ها
# ==========================================

async def search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.message is None:
        return

    text = update.message.text.strip()

    user_id = update.effective_user.id


    # ======================================
    # بازگشت
    # ======================================

    if text == "🔙 بازگشت":

        search_users.discard(user_id)

        await update.message.reply_text(
            "🏠 به منوی اصلی برگشتید.",
            reply_markup=main_keyboard()
        )

        return


    # ======================================
    # ارزهای محبوب
    # ======================================

    if text == "⭐ ارزهای محبوب":

        search_users.discard(user_id)

        await update.message.reply_text(
            "⭐ <b>یک ارز را انتخاب کنید:</b>",
            parse_mode="HTML",
            reply_markup=coins_keyboard()
        )

        return


    # ======================================
    # انتخاب ارز محبوب
    # ======================================

    if text in coins:

        search_users.discard(user_id)

        await send_coin_price(
            update,
            coins[text]
        )

        return


    # ======================================
    # قیمت رمز ارز
    # ======================================

    if text == "💰 قیمت رمز ارز":

        search_users.add(user_id)

        await update.message.reply_text(
            "🔍 <b>نماد ارز را وارد کنید:</b>\n\n"
            "مثال:\n"
            "BTC\n"
            "ETH\n"
            "TON\n\n"
            "یا:\n"
            "BTCUSDT",
            parse_mode="HTML"
        )

        return


    # ======================================
    # راهنما
    # ======================================

    if text == "ℹ️ راهنما":

        search_users.discard(user_id)

        await update.message.reply_text(
            "ℹ️ <b>راهنمای ربات</b>\n\n"
            "💰 قیمت رمز ارز\n"
            "قیمت ارز موردنظر را دریافت کنید.\n\n"
            "⭐ ارزهای محبوب\n"
            "قیمت ارزهای محبوب را مشاهده کنید.\n\n"
            "🎁 قیمت گیفت تلگرام\n"
            "Giftهای قابل ارسال Telegram و قیمت آنها "
            "بر اساس Stars نمایش داده می‌شوند.",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

        return


    # ======================================
    # Telegram Gifts
    # ======================================

    if text == "🎁 قیمت گیفت تلگرام":
        search_users.discard(user_id)

        await update.message.reply_text(
            "⏳ در حال دریافت Giftها از Telegram..."
        )

        await send_telegram_gifts(update)

        return


    # ======================================
    # پنل مدیریت
    # ======================================

    if text == "👤 پنل مدیریت":

        search_users.discard(user_id)

        await update.message.reply_text(
            "👤 <b>پنل مدیریت</b>\n\n"
            "🚧 این بخش در نسخه بعدی اضافه می‌شود.",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

        return


    # ======================================
    # اگر در حالت جستجو نیست
    # ======================================

    if user_id not in search_users:

        return


    # ======================================
    # جستجوی دستی ارز
    # ======================================

    symbol = text.upper().replace(
        " ",
        ""
    )

    if not symbol.endswith("USDT"):

        symbol += "USDT"


    data = get_price(symbol)


    # ======================================
    # ارز پیدا نشد
    # ======================================

    if data is None:

        await update.message.reply_text(
            "❌ ارز پیدا نشد.\n\n"
            "مثلاً:\n"
            "BTC\n"
            "ETH\n"
            "TON"
        )

        search_users.discard(user_id)

        return


    # ======================================
    # نمایش قیمت
    # ======================================

    try:

        change = float(
            data["change"]
        ) * 100

        price = float(
            data["price"]
        )

        message = (
            f"💰 <b>{data['symbol']}</b>\n\n"
            f"💵 قیمت: "
            f"<b>{price:,.6f}</b> USDT\n\n"
            f"📈 تغییرات: "
            f"<b>{change:.2f}%</b>\n\n"
            f"⬆️ بیشترین: "
            f"{data['high']}\n\n"
            f"⬇️ کمترین: "
            f"{data['low']}\n\n"
            f"📊 حجم معاملات: "
            f"{data['volume']}"
        )

        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

    except Exception as e:

        print(
            "SEARCH ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ خطا در نمایش قیمت.",
            reply_markup=main_keyboard()
        )

    search_users.discard(user_id)


# ==========================================
# اجرای ربات
# ==========================================

def main():

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    # دستور /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
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


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":
    main()



