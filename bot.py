from telegram import Update
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


# ==================================================
# کاربران در حالت جستجوی ارز
# ==================================================

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
# /start
# ==================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "👋 <b>به ربات قیمت ارزهای دیجیتال خوش آمدید.</b>\n\n"
        "💰 قیمت رمز ارز\n"
        "⭐ ارزهای محبوب\n"
        "🎁 قیمت گیفت تلگرام\n"
        "ℹ️ راهنما",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


# ==================================================
# نمایش Giftهای Telegram
# ==================================================

async def show_gifts(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        # دریافت Giftها از Telegram
        gifts = await context.bot.get_available_gifts()

        if not gifts.gifts:

            await update.message.reply_text(
                "❌ در حال حاضر Giftای موجود نیست.",
                reply_markup=main_keyboard()
            )

            return

        # پیام اولیه
        await update.message.reply_text(
            "🎁 <b>Telegram Gifts</b>\n\n"
            f"📦 تعداد Giftها: <b>{len(gifts.gifts)}</b>\n"
            "⭐ قیمت‌ها بر اساس Telegram Stars",
            parse_mode="HTML"
        )

        # ==================================================
        # نمایش تک تک Giftها
        # ==================================================

        for index, gift in enumerate(
            gifts.gifts,
            start=1
        ):

            sticker = gift.sticker

            # ------------------------------------------
            # اطلاعات اصلی
            # ------------------------------------------

            message = (
                f"🎁 <b>Gift #{index}</b>\n\n"
                f"🆔 ID: <code>{gift.id}</code>\n"
                f"⭐ قیمت: <b>{gift.star_count} Stars</b>"
            )

            # ------------------------------------------
            # تعداد کل
            # ------------------------------------------

            total_count = getattr(
                gift,
                "total_count",
                None
            )

            if total_count is not None:

                message += (
                    f"\n📊 تعداد کل: "
                    f"<b>{total_count}</b>"
                )

            # ------------------------------------------
            # تعداد باقی مانده
            # ------------------------------------------

            remaining_count = getattr(
                gift,
                "remaining_count",
                None
            )

            if remaining_count is not None:

                message += (
                    f"\n📦 باقی‌مانده: "
                    f"<b>{remaining_count}</b>"
                )

            # ------------------------------------------
            # هزینه ارتقا
            # ------------------------------------------

            upgrade_star_count = getattr(
                gift,
                "upgrade_star_count",
                None
            )

            if upgrade_star_count is not None:

                message += (
                    f"\n⬆️ هزینه ارتقا: "
                    f"<b>{upgrade_star_count} Stars</b>"
                )
                # ------------------------------------------
            # Sticker موجود نیست
            # ------------------------------------------

            if sticker is None:

                await update.message.reply_text(
                    message +
                    "\n\n🖼 تصویر: ❌ موجود نیست",
                    parse_mode="HTML"
                )

                continue

            # ------------------------------------------
            # Emoji
            # ------------------------------------------

            emoji = getattr(
                sticker,
                "emoji",
                None
            )

            if emoji:

                message += (
                    f"\n😀 Emoji: {emoji}"
                )

            # ------------------------------------------
            # نوع Sticker
            # ------------------------------------------

            sticker_type = getattr(
                sticker,
                "type",
                None
            )

            if sticker_type:

                message += (
                    f"\n🎞 نوع: "
                    f"<code>{sticker_type}</code>"
                )

            # ==================================================
            # روش اول: ارسال خود Sticker
            # ==================================================

            image_sent = False

            try:

                await update.message.reply_sticker(
                    sticker=sticker.file_id
                )

                image_sent = True

                message += (
                    "\n🖼 نمایش: "
                    "✅ Sticker"
                )

            except Exception as error:

                print(
                    f"[Gift {gift.id}] "
                    f"Sticker Error: {repr(error)}"
                )

            # ==================================================
            # روش دوم: ارسال Thumbnail
            # ==================================================

            if not image_sent:

                thumbnail = getattr(
                    sticker,
                    "thumbnail",
                    None
                )

                if thumbnail is not None:

                    try:

                        await update.message.reply_photo(
                            photo=thumbnail.file_id
                        )

                        image_sent = True

                        message += (
                            "\n🖼 نمایش: "
                            "✅ Thumbnail"
                        )

                    except Exception as error:

                        print(
                            f"[Gift {gift.id}] "
                            f"Thumbnail Error: {repr(error)}"
                        )

            # ==================================================
            # اگر هیچ تصویری ارسال نشد
            # ==================================================

            if not image_sent:

                message += (
                    "\n🖼 نمایش: "
                    "❌ امکان ارسال تصویر وجود ندارد"
                )

            # ==================================================
            # ارسال اطلاعات Gift
            # ==================================================

            try:

                await update.message.reply_text(
                    message,
                    parse_mode="HTML"
                )

            except Exception as error:

                print(
                    f"[Gift {gift.id}] "
                    f"Message Error: {repr(error)}"
                )

        # ==================================================
        # پایان
        # ==================================================

        await update.message.reply_text(
            "✅ <b>نمایش تمام Giftها تمام شد.</b>",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

    except Exception as error:

        print(
            "========== GIFTS ERROR =========="
        )
        print(
            repr(error)
        )

        print(
            "================================"
        )

        await update.message.reply_text(
            "❌ خطا در دریافت Giftهای Telegram.\n\n"
            "جزئیات خطا در Railway Logs ثبت شده است.",
            reply_markup=main_keyboard()
        )


# ==================================================
# نمایش قیمت ارز
# ==================================================

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

        price = float(
            data["price"]
        )

        change = float(
            data["change"]
        ) * 100

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

    except Exception as error:

        print(
            "PRICE ERROR:",
            repr(error)
        )

        await update.message.reply_text(
            "❌ خطا در دریافت قیمت.",
            reply_markup=main_keyboard()
        )


# ==================================================
# مدیریت پیام‌های متنی
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
            "⭐ <b>یک ارز را انتخاب کنید:</b>",
            parse_mode="HTML",
            reply_markup=coins_keyboard()
        )

        return


    # ==================================================
    # انتخاب ارز محبوب
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
            "مثال:\n"
            "BTC\n"
            "ETH\n"
            "TON\n\n"
            "یا:\n"
            "BTCUSDT",
            parse_mode="HTML"
        )

        return


    # ==================================================
    # Gift
    # ==================================================

    if text == "🎁 قیمت گیفت تلگرام":

        search_users.discard(user_id)

        loading = await update.message.reply_text(
            "⏳ در حال دریافت Giftهای Telegram..."
        )

        await show_gifts(
            update,
            context
        )

        try:

            await loading.delete()

        except Exception:
            pass

        return
    # ==================================================
    # راهنما
    # ==================================================

    if text == "ℹ️ راهنما":

        search_users.discard(user_id)

        await update.message.reply_text(
            "ℹ️ <b>راهنمای ربات</b>\n\n"
            "💰 قیمت رمز ارز\n"
            "قیمت ارز موردنظر را دریافت کنید.\n\n"
            "⭐ ارزهای محبوب\n"
            "قیمت ارزهای محبوب را ببینید.\n\n"
            "🎁 قیمت گیفت تلگرام\n"
            "Giftهای موجود Telegram و قیمت Stars آنها.",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

        return


    # ==================================================
    # پنل مدیریت
    # ==================================================

    if text == "👤 پنل مدیریت":

        search_users.discard(user_id)

        await update.message.reply_text(
            "👤 <b>پنل مدیریت</b>\n\n"
            "🚧 این بخش در نسخه بعدی اضافه می‌شود.",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

        return


    # ==================================================
    # اگر در حالت جستجو نیست
    # ==================================================

    if user_id not in search_users:

        return


    # ==================================================
    # جستجوی دستی
    # ==================================================

    symbol = text.upper().replace(
        " ",
        ""
    )

    if not symbol.endswith("USDT"):

        symbol += "USDT"


    data = get_price(symbol)

    if data is None:

        await update.message.reply_text(
            "❌ ارز پیدا نشد.\n\n"
            "مثلاً BTC یا ETH را امتحان کنید.",
            reply_markup=main_keyboard()
        )

        search_users.discard(user_id)

        return


    try:

        price = float(
            data["price"]
        )

        change = float(
            data["change"]
        ) * 100

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

    except Exception as error:

        print(
            "SEARCH ERROR:",
            repr(error)
        )

        await update.message.reply_text(
            "❌ خطا در نمایش قیمت.",
            reply_markup=main_keyboard()
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

    print("🤖 Bot Started...")

    app.run_polling()


# ==================================================
# اجرای اصلی
# ==================================================

if __name__ == "__main__":
    main()