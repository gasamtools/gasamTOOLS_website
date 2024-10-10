import requests
import time
import base64
import hmac
import hashlib
from datetime import datetime, timedelta

def get_kucoin_signature(timestamp, method, endpoint, API_SECRET, body=''):
    string_to_sign = timestamp + method + endpoint + body
    signature = base64.b64encode(
        hmac.new(API_SECRET.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha256).digest()
    )
    return signature.decode('utf-8')


def fetch_kucoin_data(symbol, start_time, end_time, interval, API_KEY, API_SECRET, API_PASSPHRASE):
    import pytz

    base_url = "https://api.kucoin.com"
    endpoint = f"/api/v1/market/candles"

    # Convert start_time and end_time to UTC
    start_time_utc = start_time.astimezone(pytz.UTC)
    end_time_utc = end_time.astimezone(pytz.UTC)

    # If interval is weekly, we fetch daily data and aggregate it ourselves
    api_interval = '1day' if interval == '1week' or interval == '1month' else interval

    params = f"symbol={symbol}&startAt={int(start_time_utc.timestamp())}&endAt={int(end_time_utc.timestamp())}&type={api_interval}"

    timestamp = str(int(time.time()))
    signature = get_kucoin_signature(timestamp, 'GET', f"{endpoint}?{params}", API_SECRET)

    headers = {
        "KC-API-KEY": API_KEY,
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": timestamp,
        "KC-API-PASSPHRASE": API_PASSPHRASE,
        "KC-API-KEY-VERSION": "2"
    }

    url = f"{base_url}{endpoint}?{params}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get("code") == "200000" and "data" in data:
            valid_data = []
            for candle in data["data"]:
                if all(candle) and len(candle) == 7:
                    candle_time = int(float(candle[0]))
                    # Convert candle time to UTC
                    candle_time_utc = datetime.fromtimestamp(candle_time, tz=pytz.UTC)
                    valid_data.append({
                        "time": int(candle_time_utc.timestamp()),
                        "open": float(candle[1]),
                        "high": float(candle[3]),
                        "low": float(candle[4]),
                        "close": float(candle[2]),
                        "volume": float(candle[5])
                    })

            valid_data.reverse()  # Reverse to get chronological order

            if interval in ['1week', '1month']:
                return aggregate_candles(valid_data, interval)
            else:
                return valid_data
        else:
            print(f"API returned unexpected data structure: {data}")
            return []
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []


def get_period_start(timestamp, interval):
    import pytz

    date = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
    if interval == '1week':
        start = date - timedelta(days=date.weekday())
    elif interval == '1month':
        start = date.replace(day=1)
    else:
        start = date  # For daily or other intervals, use the date as is
    return int(start.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())



def aggregate_candles(daily_data, interval):
    aggregated_data = {}
    for candle in daily_data:
        period_start = get_period_start(candle['time'], interval)
        if period_start not in aggregated_data:
            aggregated_data[period_start] = {
                "time": period_start,
                "open": candle['open'],
                "high": candle['high'],
                "low": candle['low'],
                "close": candle['close'],
                "volume": candle['volume']
            }
        else:
            aggregated_data[period_start]['high'] = max(aggregated_data[period_start]['high'], candle['high'])
            aggregated_data[period_start]['low'] = min(aggregated_data[period_start]['low'], candle['low'])
            aggregated_data[period_start]['close'] = candle['close']
            aggregated_data[period_start]['volume'] += candle['volume']

    return list(aggregated_data.values())