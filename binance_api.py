import requests

BASE_URL = "https://api.kucoin.com"


def get_price(symbol):
    try:
        symbol = symbol.upper().replace("/", "-")

        if "-" not in symbol:
            if symbol.endswith("USDT"):
                symbol = symbol.replace("USDT", "-USDT")

        url = f"{BASE_URL}/api/v1/market/stats?symbol={symbol}"

        response = requests.get(url, timeout=10)

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
        print(e)
        return None