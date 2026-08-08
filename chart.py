import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from datetime import datetime


def create_chart(candles, symbol):

    if not candles:
        return None

    # KuCoin داده‌ها را از جدید به قدیم می‌دهد
    candles = list(reversed(candles))

    times = []
    prices = []

    for candle in candles:

        timestamp = int(candle[0])

        # KuCoin timestamp بر حسب ثانیه است
        date = datetime.fromtimestamp(timestamp)

        # قیمت بسته شدن
        close_price = float(candle[2])

        times.append(date)
        prices.append(close_price)

    # ساخت نمودار
    plt.figure(figsize=(10, 5))

    plt.plot(
        times,
        prices,
        linewidth=2
    )

    plt.title(
        f"{symbol} Price Chart"
    )

    plt.xlabel(
        "Time"
    )

    plt.ylabel(
        "Price (USDT)"
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.xticks(
        rotation=45
    )

    plt.tight_layout()

    # ذخیره نمودار
    filename = "chart.png"

    plt.savefig(
        filename,
        dpi=150
    )

    plt.close()

    return filename