import requests


BASE_URL = "https://api.kucoin.com"


# ==================================================
# قیمت یک ارز
# ==================================================

def get_price(symbol):

    try:

        symbol = symbol.upper().replace("/", "-")

        if "-" not in symbol:

            if symbol.endswith("USDT"):
                symbol = symbol.replace(
                    "USDT",
                    "-USDT"
                )

        url = (
            f"{BASE_URL}"
            f"/api/v1/market/stats"
            f"?symbol={symbol}"
        )

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code != 200:
            return None

        result = response.json()

        if result.get("code") != "200000":
            return None

        data = result["data"]

        return {
            "symbol": symbol,
            "price": data["last"],
            "change": data["changeRate"],
            "high": data["high"],
            "low": data["low"],
            "volume": data["vol"],
        }

    except Exception as e:

        print(
            "GET PRICE ERROR:",
            repr(e)
        )

        return None


# ==================================================
# دریافت کل بازار
# ==================================================

def get_market():

    try:

        url = (
            f"{BASE_URL}"
            "/api/v1/market/allTickers"
        )

        response = requests.get(
            url,
            timeout=15
        )

        if response.status_code != 200:
            print(
                "MARKET HTTP ERROR:",
                response.status_code
            )
            return []

        result = response.json()

        if result.get("code") != "200000":

            print(
                "MARKET API ERROR:",
                result
            )

            return []

        data = result.get("data", {})

        tickers = data.get(
            "ticker",
            []
        )

        market = []

        for item in tickers:

            symbol = item.get(
                "symbol",
                ""
            )

            # فقط جفت‌های USDT
            if not symbol.endswith(
                "-USDT"
            ):
                continue

            try:

                price = float(
                    item.get(
                        "last",
                        0
                    )
                )

                change = float(
                    item.get(
                        "changeRate",
                        0
                    )
                ) * 100

                volume = float(
                    item.get(
                        "volValue",
                        0
                    )
                )

                high = float(
                    item.get(
                        "high",
                        0
                    )
                )

                low = float(
                    item.get(
                        "low",
                        0
                    )
                )

                market.append({

                    "symbol": symbol,

                    "price": price,

                    "change": change,

                    "volume": volume,

                    "high": high,

                    "low": low,

                })

            except (
                ValueError,
                TypeError
            ):

                continue

        return market

    except Exception as e:

        print(
            "GET MARKET ERROR:",
            repr(e)
        )

        return []


# ==================================================
# بیشترین رشد
# ==================================================

def get_top_gainers(limit=10):

    market = get_market()

    market.sort(
        key=lambda x: x["change"],
        reverse=True
    )

    return market[:limit]


# ==================================================
# بیشترین ریزش
# ==================================================
def get_top_losers(limit=10):

    market = get_market()

    market.sort(
        key=lambda x: x["change"]
    )

    return market[:limit]


# ==================================================
# بیشترین حجم معاملات
# ==================================================

def get_top_volume(limit=10):

    market = get_market()

    market.sort(
        key=lambda x: x["volume"],
        reverse=True
    )

    return market[:limit]


# ==================================================
# ده ارز برتر بر اساس حجم
# ==================================================

def get_top_coins(limit=10):

    market = get_market()

    market.sort(
        key=lambda x: x["volume"],
        reverse=True
    )

    return market[:limit]
