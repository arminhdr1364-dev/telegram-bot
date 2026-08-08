from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN
from keyboards import (
    main_keyboard,
    coins_keyboard,
    market_keyboard
)
from binance_api import (
    get_price,
    get_top_gainers,
    get_top_losers,
    get_top_volume,
    get_top_coins,
)
from binance_api import get_price, get_candles
from chart import create_chart


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
        "📊 بازار\n"
        "🎁 قیمت گیفت تلگرام\n"
        "ℹ️ راهنما",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


# ==================================================
# فرمت حجم
# ==================================================

def format_volume(value):

    try:

        value = float(value)

        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"

        if value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"

        if value >= 1_000:
            return f"{value / 1_000:.2f}K"

        return f"{value:.2f}"

    except Exception:

        return str(value)


# ==================================================
# فرمت قیمت
# ==================================================

def format_price(price):

    try:

        price = float(price)

        if price >= 1000:
            return f"{price:,.2f}"

        if price >= 1:
            return f"{price:,.4f}"

        return f"{price:,.8f}"

    except Exception:

        return str(price)
async def show_gifts(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        # دریافت Giftها از Telegram
        result = await context.bot.get_available_gifts()

        print("========== GIFTS ==========")
        print(result)
        print("============================")

        if not result.gifts:

            await update.message.reply_text(
                "❌ در حال حاضر Giftای موجود نیست."
            )

            return

        # تعداد Giftها
        await update.message.reply_text(
            f"🎁 <b>Telegram Gifts</b>\n\n"
            f"📦 تعداد Giftها: <b>{len(result.gifts)}</b>\n"
            f"⭐ قیمت‌ها بر اساس Telegram Stars",
            parse_mode="HTML"
        )

        # نمایش Giftها
        for index, gift in enumerate(
            result.gifts,
            start=1
        ):

            # --------------------------
            # اطلاعات Gift
            # --------------------------

            text = (
                f"🎁 <b>Gift #{index}</b>\n\n"
                f"🆔 ID: <code>{gift.id}</code>\n"
                f"⭐ قیمت: <b>{gift.star_count} Stars</b>"
            )

            # --------------------------
            # اطلاعات تعداد
            # --------------------------

            total_count = getattr(
                gift,
                "total_count",
                None
            )

            remaining_count = getattr(
                gift,
                "remaining_count",
                None
            )

            if total_count is not None:

                text += (
                    f"\n📊 تعداد کل: "
                    f"<b>{total_count}</b>"
                )

            if remaining_count is not None:

                text += (
                    f"\n📦 باقی‌مانده: "
                    f"<b>{remaining_count}</b>"
                )

            # --------------------------
            # دکمه Portals
            # --------------------------

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🛒 مشاهده / خرید در Portals",
                        url="https://t.me/portals"
                    )
                ]
            ])

            # --------------------------
            # ارسال اطلاعات
            # --------------------------

            await update.message.reply_text(
                text,
                parse_mode="HTML",
                reply_markup=keyboard
            )

            # --------------------------
            # ارسال استیکر Gift
            # --------------------------

            try:

                sticker = gift.sticker

                if sticker:

                    await update.message.reply_sticker(
                        sticker=sticker.file_id
                    )

                    print(
                        f"✅ Sticker sent: {gift.id}"
                    )

                else:

                    print(
                        f"⚠️ No sticker: {gift.id}"
                    )

            except Exception as error:

                print(
                    f"❌ Sticker error "
                    f"{gift.id}: {repr(error)}"
                )

        # --------------------------
        # پایان
        # --------------------------

        await update.message.reply_text(
            "✅ نمایش تمام Giftها تمام شد.",
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
            "================================="
        )

        await update.message.reply_text(
            "❌ خطا در دریافت Giftهای Telegram.\n\n"
            "لطفاً Logs ربات را بررسی کنید.",
            reply_markup=main_keyboard()
        )


# ==================================================
# منوی بازار
# ==================================================

async def market_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "📊 <b>بازار ارزهای دیجیتال</b>\n\n"
        "🔥 بیشترین رشد 24 ساعته\n"
        "📉 بیشترین ریزش 24 ساعته\n"
        "💰 بیشترین حجم معاملات\n"
        "🏆 ارزهای برتر\n\n"
        "یکی از گزینه‌ها را انتخاب کن.",
        parse_mode="HTML",
        reply_markup=market_keyboard()
)


# ==================================================
# بیشترین رشد
# ==================================================

async def show_gainers(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "⏳ در حال دریافت اطلاعات بازار..."
    )

    data = get_top_gainers(10)

    if not data:

        await update.message.reply_text(
            "❌ اطلاعات بازار دریافت نشد."
        )

        return

    text = (
        "🔥 <b>بیشترین رشد 24 ساعته</b>\n\n"
    )

    for i, coin in enumerate(data, 1):

        text += (
            f"{i}. <b>{coin['symbol']}</b>\n"
            f"💵 {format_price(coin['price'])} USDT\n"
            f"📈 +{coin['change']:.2f}%\n"
            f"📊 حجم: "
            f"{format_volume(coin['volume'])}\n\n"
        )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


# ==================================================
# بیشترین ریزش
# ==================================================

async def show_losers(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "⏳ در حال دریافت اطلاعات بازار..."
    )

    data = get_top_losers(10)

    if not data:

        await update.message.reply_text(
            "❌ اطلاعات بازار دریافت نشد."
        )

        return

    text = (
        "📉 <b>بیشترین ریزش 24 ساعته</b>\n\n"
    )

    for i, coin in enumerate(data, 1):
        text += (
            f"{i}. <b>{coin['symbol']}</b>\n"
            f"💵 {format_price(coin['price'])} USDT\n"
            f"📉 {coin['change']:.2f}%\n"
            f"📊 حجم: "
            f"{format_volume(coin['volume'])}\n\n"
        )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


# ==================================================
# بیشترین حجم
# ==================================================

async def show_volume(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "⏳ در حال دریافت اطلاعات بازار..."
    )

    data = get_top_volume(10)

    if not data:

        await update.message.reply_text(
            "❌ اطلاعات بازار دریافت نشد."
        )

        return

    text = (
        "💰 <b>بیشترین حجم معاملات</b>\n\n"
    )

    for i, coin in enumerate(data, 1):

        change = coin["change"]

        sign = "+" if change >= 0 else ""

        text += (
            f"{i}. <b>{coin['symbol']}</b>\n"
            f"💵 {format_price(coin['price'])} USDT\n"
            f"📈 {sign}{change:.2f}%\n"
            f"💰 حجم: "
            f"{format_volume(coin['volume'])}\n\n"
        )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


# ==================================================
# ارزهای برتر
# ==================================================

async def show_top_coins(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "⏳ در حال دریافت اطلاعات بازار..."
    )

    data = get_top_coins(10)

    if not data:

        await update.message.reply_text(
            "❌ اطلاعات بازار دریافت نشد."
        )

        return

    text = (
        "🏆 <b>10 ارز برتر بازار</b>\n\n"
    )

    for i, coin in enumerate(data, 1):

        change = coin["change"]

        sign = "+" if change >= 0 else ""

        text += (
            f"🏅 <b>{i}. {coin['symbol']}</b>\n"
            f"💵 قیمت: "
            f"{format_price(coin['price'])} USDT\n"
            f"📈 تغییر: "
            f"{sign}{change:.2f}%\n"
            f"📊 حجم: "
            f"{format_volume(coin['volume'])}\n\n"
        )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
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

        price = float(data["price"])

        change = float(data["change"]) * 100

        sign = "+" if change >= 0 else ""

        text = (
            f"💰 <b>{data['symbol']}</b>\n\n"
            f"💵 قیمت: "
            f"<b>{format_price(price)}</b> USDT\n\n"
            f"📈 تغییرات: "
            f"<b>{sign}{change:.2f}%</b>\n\n"
            f"⬆️ بیشترین: {data['high']}\n\n"
            f"⬇️ کمترین: {data['low']}\n\n"
            f"📊 حجم معاملات: "
            f"{data['volume']}"
        )

        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=coins_keyboard()
        )

    except Exception as error:

        print(
            "PRICE ERROR:",
            repr(error)
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
    # بازار
    # ==================================================

    if text in (
        "📊 بازار",
        "📈 بازار",
        "💹 بازار"
    ):

        search_users.discard(user_id)

        await market_menu(
            update,
            context
        )

        return


    # ==================================================
    # گزینه‌های بازار
    # ==================================================

    if text == "🔥 بیشترین رشد":

        await show_gainers(
            update,
            context
        )

        return


    if text == "📉 بیشترین ریزش":

        await show_losers(
            update,
            context
        )

        return


    if text == "💰 بیشترین حجم":

        await show_volume(
            update,
            context
        )

        return


    if text == "🏆 ارزهای برتر":

        await show_top_coins(
            update,
            context
        )

        return
    if text == "🔄 بروزرسانی بازار":

        await market_menu(
            update,
            context
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
            "BTC\n"
            "ETH\n"
            "TON\n\n"
            "یا BTCUSDT",
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
            "⭐ ارزهای محبوب\n"
            "📊 بازار\n"
            "🎁 قیمت گیفت تلگرام",
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

        return


    # ==================================================
    # پنل مدیریت
    # ==================================================

    if text == "👤 پنل مدیریت":

        await update.message.reply_text(
            "🚧 پنل مدیریت در نسخه بعدی اضافه می‌شود.",
            reply_markup=main_keyboard()
        )

        return


    # ==================================================
    # حالت جستجوی ارز
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


    await send_coin_price(
        update,
        symbol
    )

    search_users.discard(user_id)
    # ==================================================
# اجرای ربات
# ==================================================
async def send_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):

    symbol = "BTC-USDT"

    candles = get_candles(
        symbol,
        "1hour"
    )

    if not candles:
        await update.message.reply_text(
            "❌ دریافت اطلاعات نمودار ممکن نیست."
        )
        return

    chart_file = create_chart(
        candles,
        symbol
    )

    if not chart_file:
        await update.message.reply_text(
            "❌ ساخت نمودار ناموفق بود."
        )
        return

    with open(chart_file, "rb") as photo:

        await update.message.reply_photo(
            photo=photo,
            caption=f"📈 نمودار {symbol}\n⏱ بازه: 1 ساعت"
        )
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


