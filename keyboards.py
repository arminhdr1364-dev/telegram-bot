from telegram import ReplyKeyboardMarkup


def main_keyboard():

    keyboard = [

        [
            "💰 قیمت رمز ارز",
            "⭐ ارزهای محبوب"
        ],

        [
            "📊 بازار",
            "🎁 قیمت گیفت تلگرام"
        ],

        [
            "ℹ️ راهنما",
            "👤 پنل مدیریت"
        ]

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )


def coins_keyboard():

    keyboard = [

        [
            "🟠 BTC",
            "🔵 ETH"
        ],

        [
            "🟣 SOL",
            "⚫ BNB"
        ],

        [
            "🟢 XRP",
            "🟡 DOGE"
        ],

        [
            "💎 TON",
            "🔴 TRX"
        ],

        [
            "🔙 بازگشت"
        ]

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )


def market_keyboard():

    keyboard = [

        [
            "🔥 بیشترین رشد",
            "📉 بیشترین ریزش"
        ],

        [
            "💰 بیشترین حجم",
            "🏆 ارزهای برتر"
        ],

        [
            "🔄 بروزرسانی بازار"
        ],

        [
            "🔙 بازگشت"
        ]

    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )
