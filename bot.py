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


# ==================================================
# ارزهای محبوب
# ==================================================

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


# ==================================================
# START
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 <b>به ربات قیمت ارزهای دیجیتال خوش آمدید.</b>\n\n"
        "💰 قیمت رمز ارز\n"
        "⭐ ارزهای محبوب\n"
        "🎁 قیمت گیفت تلگرام",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


# ==================================================
# ارسال Giftها
# ==================================================

async def send_telegram_gifts(update: Update):

    try:

        bot = Bot(TOKEN)

        gifts = await bot.get_available_gifts()

        if not gifts.gifts:

            await update.message.reply_text(
                "❌ در حال حاضر Giftای موجود نیست."
            )

            return

        await update.message.reply_text(
            "🎁 <b>Telegram Gifts</b>\n\n"
            f"📦 تعداد: <b>{len(gifts.gifts)}</b>\n"
            "⭐ قیمت‌ها بر اساس Telegram Stars هستند.",
            parse_mode="HTML"
        )

        for number, gift in enumerate(
            gifts.gifts,
            start=1
        ):

            # ==========================================
            # اطلاعات Gift
            # ==========================================

            gift_id = gift.id
            stars = gift.star_count
            sticker = gift.sticker

            caption = (
                f"🎁 <b>Gift #{number}</b>\n\n"
                f"🆔 ID: <code>{gift_id}</code>\n"
                f"⭐ قیمت: <b>{stars} Stars</b>"
            )

            # ==========================================
            # اگر Sticker ندارد
            # ==========================================

            if sticker is None:

                await update.message.reply_text(
                    caption +
                    "\n🖼 تصویر در دسترس نیست.",
                    parse_mode="HTML"
                )

                continue

            # ==========================================
            # اطلاعات Sticker
            # ==========================================

            file_id = sticker.file_id

            is_animated = getattr(
                sticker,
                "is_animated",
                False
            )

            is_video = getattr(
                sticker,
                "is_video",
                False
            )

            # ==========================================
            # ارسال Sticker
            # ==========================================

            sent = False

            try:

                # استیکر معمولی
                if not is_animated and not is_video:

                    await update.message.reply_sticker(
                        sticker=file_id
                    )

                    sent = True

                # استیکر ویدیویی
                elif is_video:

                    await update.message.reply_video(
                        video=file_id
                    )

                    sent = True

                # استیکر متحرک
                elif is_animated:

                    await update.message.reply_animation(
                        animation=file_id
                    )

                    sent = True

            except Exception as e:

                print(
                    f"Gift {gift_id} send error:",
                    repr(e)
                )
                # ==========================================
            # اطلاعات Gift
            # ==========================================

            if sent:

                await update.message.reply_text(
                    caption,
                    parse_mode="HTML"
                )

            else:

                await update.message.reply_text(
                    caption +
                    "\n🖼 ارسال تصویر این Gift ممکن نبود.",
                    parse_mode="HTML"
                )

        # ==========================================
        # پایان
        # ==========================================

        await update.message.reply_text(
            "✅ <b>نمایش Giftها تمام شد.</b>",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

    except Exception as e:

        print(
            "GIFT ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ خطا در دریافت Giftها.\n\n"
            "لطفاً Railway Logs را بررسی کنید.",
            reply_markup=main_keyboard()
        )


# ==================================================
# قیمت ارز
# ==================================================

async def send_coin_price(
    update: Update,
    symbol: str
):

    try:

        data = get_price(symbol)

        if data is None:

            await update.message.reply_text(
                "❌ اطلاعات این ارز پیدا نشد."
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
            f"💵 قیمت: <b>{price:,.6f}</b> USDT\n\n"
            f"📈 تغییرات: <b>{change:.2f}%</b>\n\n"
            f"⬆️ بیشترین: {data['high']}\n\n"
            f"⬇️ کمترین: {data['low']}\n\n"
            f"📊 حجم معاملات: {data['volume']}"
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
            "❌ خطا در دریافت قیمت."
        )


# ==================================================
# مدیریت پیام‌ها
# ==================================================

async def search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.message is None:
        return

    text = update.message.text.strip()
    user_id = update.effective_user.id


    # ==================================================
    # بازگشت
    # ==================================================

    if text == "🔙 بازگشت":

        search_users.discard(user_id)

        await update.message.reply_text(
            "🏠 به منوی اصلی برگشتید.",
            reply_markup=main_keyboard()
        )

        return


    # ==================================================
    # ارزهای محبوب
    # ==================================================

    if text == "⭐ ارزهای محبوب":

        search_users.discard(user_id)

        await update.message.reply_text(
            "⭐ یک ارز را انتخاب کنید:",
            reply_markup=coins_keyboard()
        )

        return


    # ==================================================
    # انتخاب ارز
    # ==================================================

    if text in coins:

        search_users.discard(user_id)

        await send_coin_price(
            update,
            coins[text]
        )

        return


    # ==================================================
    # قیمت رمز ارز
    # ==================================================

    if text == "💰 قیمت رمز ارز":

        search_users.add(user_id)

        await update.message.reply_text(
            "🔍 <b>نماد ارز را وارد کنید:</b>\n\n"
            "BTC\n"
            "ETH\n"
            "TON",
            parse_mode="HTML"
        )

        return
    # ==================================================
    # راهنما
    # ==================================================

    if text == "ℹ️ راهنما":

        search_users.discard(user_id)

        await update.message.reply_text(
            "ℹ️ <b>راهنمای ربات</b>\n\n"
            "💰 قیمت رمز ارز\n"
            "⭐ ارزهای محبوب\n"
            "🎁 قیمت گیفت تلگرام",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

        return


    # ==================================================
    # Gift
    # ==================================================

    if text == "🎁 قیمت گیفت تلگرام":

        search_users.discard(user_id)

        loading = await update.message.reply_text(
            "⏳ در حال دریافت Giftها از Telegram..."
        )

        await send_telegram_gifts(update)

        try:
            await loading.delete()
        except Exception:
            pass

        return


    # ==================================================
    # پنل مدیریت
    # ==================================================

    if text == "👤 پنل مدیریت":

        await update.message.reply_text(
            "🚧 پنل مدیریت به‌زودی اضافه می‌شود.",
            reply_markup=main_keyboard()
        )

        return


    # ==================================================
    # حالت جستجو
    # ==================================================

    if user_id not in search_users:
        return


    symbol = text.upper().replace(
        " ",
        ""
    )

    if not symbol.endswith("USDT"):
        symbol += "USDT"


    data = get_price(symbol)

    if data is None:

        await update.message.reply_text(
            "❌ ارز پیدا نشد."
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
            f"💵 قیمت: <b>{price:,.6f}</b> USDT\n\n"
            f"📈 تغییرات: <b>{change:.2f}%</b>\n\n"
            f"⬆️ بیشترین: {data['high']}\n\n"
            f"⬇️ کمترین: {data['low']}\n\n"
            f"📊 حجم معاملات: {data['volume']}"
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
            "❌ خطا در نمایش قیمت."
        )

    search_users.discard(user_id)


# ==================================================
# اجرای ربات
# ==================================================

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



 





