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
# کاربران در حالت جستجو
# =========================

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
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 به ربات قیمت ارزهای دیجیتال خوش آمدید.\n\n"
        "📊 قیمت لحظه‌ای ارزها\n"
        "🎁 اطلاعات Telegram Gifts\n"
        "⭐ قیمت بر اساس Stars",
        reply_markup=main_keyboard()
    )


# =========================
# دریافت اطلاعات Telegram Gifts
# =========================

async def get_telegram_gifts():

    try:

        bot = Bot(TOKEN)

        gifts = await bot.get_available_gifts()

        if not gifts.gifts:

            return (
                "❌ <b>Giftای در دسترس نیست.</b>"
            )

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

            gift_id = getattr(
                gift,
                "id",
                "نامشخص"
            )

            star_count = getattr(
                gift,
                "star_count",
                0
            )

            sticker = getattr(
                gift,
                "sticker",
                None
            )

            # اطلاعات استیکر
            if sticker:

                emoji = getattr(
                    sticker,
                    "emoji",
                    "🎁"
                )

                sticker_type = "✅ موجود"

                sticker_id = getattr(
                    sticker,
                    "file_id",
                    "نامشخص"
                )

            else:

                emoji = "🎁"
                sticker_type = "❌ موجود نیست"
                sticker_id = "ندارد"

            # اطلاعات بیشتر در صورت وجود
            remaining_count = getattr(
                gift,
                "remaining_count",
                None
            )

            total_count = getattr(
                gift,
                "total_count",
                None
            )

            text += (
                f"{emoji} "
                f"<b>Gift #{number}</b>\n"
                f"🆔 ID: "
                f"<code>{gift_id}</code>\n"
                f"⭐ قیمت: "
                f"<b>{star_count}</b> Stars\n"
                f"🖼 استیکر: "
                f"{sticker_type}\n"
            )

            if sticker_id != "نامشخص":
                text += (
                    f"🆔 Sticker ID: "
                    f"<code>{sticker_id}</code>\n"
                )

            if remaining_count is not None:
                text += (
                    f"📦 موجودی باقی‌مانده: "
                    f"<b>{remaining_count}</b>\n"
                )

            if total_count is not None:
                text += (
                    f"📊 تعداد کل: "
                    f"<b>{total_count}</b>\n"
                )

            text += (
                "━━━━━━━━━━━━━━━━━━\n"
            )

        text += (
            "\n🔄 <i>اطلاعات مستقیماً "
            "از Telegram دریافت شد.</i>\n"
            "⭐ قیمت‌ها بر اساس Telegram Stars هستند."
        )

        return text

    except Exception as e:

        print(
            "Gift Error:",
            repr(e)
        )
        return (
            "❌ <b>خطا در دریافت Giftها</b>\n\n"
            "لطفاً چند لحظه بعد دوباره امتحان کنید."
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
                "❌ دریافت اطلاعات این ارز ممکن نیست.",
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
            "Price Error:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ خطا در دریافت قیمت.",
            reply_markup=main_keyboard()
        )


# =========================
# مدیریت تمام پیام‌ها
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
            "مثال:\n\n"
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

        search_users.discard(user_id)

        await update.message.reply_text(
            "ℹ️ <b>راهنمای ربات</b>\n\n"
            "💰 <b>قیمت رمز ارز</b>\n"
            "نام ارز را وارد کنید تا قیمت آن نمایش داده شود.\n\n"
            "⭐ <b>ارزهای محبوب</b>\n"
            "قیمت ارزهای محبوب را مشاهده کنید.\n\n"
            "🎁 <b>قیمت گیفت تلگرام</b>\n"
            "Giftهای قابل ارسال و قیمت آن‌ها "
            "بر اساس Stars نمایش داده می‌شوند.",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

        return


    # =========================
    # Telegram Gifts
    # =========================

    if text == "🎁 قیمت گیفت تلگرام":

        search_users.discard(user_id)

        loading = await update.message.reply_text(
            "⏳ در حال دریافت اطلاعات Giftها از Telegram..."
        )

        gifts_text = await get_telegram_gifts()

        # حذف پیام Loading
        try:

            await loading.delete()

        except Exception:
            pass
        # ارسال اطلاعات
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

        search_users.discard(user_id)

        await update.message.reply_text(
            "👤 <b>پنل مدیریت</b>\n\n"
            "🚧 این بخش در نسخه بعدی فعال می‌شود.",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

        return


    # =========================
    # اگر در حالت جستجو نیست
    # =========================

    if user_id not in search_users:

        return


    # =========================
    # جستجوی دستی ارز
    # =========================

    symbol = text.upper().replace(
        " ",
        ""
    )

    if not symbol.endswith("USDT"):

        symbol += "USDT"


    # =========================
    # دریافت قیمت
    # =========================

    data = get_price(symbol)

    if data is None:

        await update.message.reply_text(
            "❌ ارز پیدا نشد.\n\n"
            "مثلاً این موارد را امتحان کنید:\n"
            "BTC\n"
            "ETH\n"
            "TON"
        )

        search_users.discard(user_id)

        return


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
            "Search Price Error:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ خطا در نمایش اطلاعات ارز.",
            reply_markup=main_keyboard()
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

    # /start
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

    print(
        "🤖 Bot Started..."
    )

    app.run_polling()


# =========================
# Main
# =========================

if __name__ == "__main__":
    main()



