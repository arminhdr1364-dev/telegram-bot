from telegram import ReplyKeyboardMarkup

def main_keyboard():

    keyboard = [
        ["💰 قیمت رمز ارز", "⭐ ارزهای محبوب"],
        ["🎁 قیمت گیفت تلگرام", "📈 بازار"],
        ["🔔 هشدار قیمت", "❤️ علاقه‌مندی‌ها"],
        ["👤 پنل مدیریت", "⚙️ تنظیمات"],
        ["ℹ️ راهنما"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )
def coins_keyboard():
    keyboard = [
        ["🟠 BTC", "🔵 ETH"],
        ["🟣 SOL", "⚫ BNB"],
        ["🟢 XRP", "🟡 DOGE"],
        ["💎 TON", "🔴 TRX"],
        ["🔙 بازگشت"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )