keys_db = 'app_fi_zelf_alchemy_keys_db'

def fz_fetcher(current_user, db, User, GasamApp, json_data, files_data):

    if json_data['js_function_sub'] == 'api':
        return fz_fetcher_api(current_user, db, User, GasamApp, json_data, files_data)
    if json_data['js_function_sub'] == 'selectPair':
        return fz_fetcher_fetch_pair(current_user, db, User, GasamApp, json_data, files_data)


def fz_fetcher_api(current_user, db, User, GasamApp, json_data, files_data):
    global keys_db
    def get_or_update_env_db(current_user, db, env_key, json_data, db_name):
        from sqlalchemy import text

        if env_key in json_data:
            env_value = json_data[env_key].strip()
        else:
            env_value = None

        if env_value:

            # Check if the user_id already exists
            existing_record = db.session.execute(
                text(f"SELECT * FROM {db_name} WHERE env_key = :env_key"),
                {"env_key": env_key}
            ).fetchone()

            if existing_record:

                db.session.execute(
                    text(
                        f"UPDATE {db_name} SET env_value = :env_value WHERE env_key = :env_key"),
                    {"env_value": env_value, "env_key": env_key}
                )
            else:
                # User does not exist, insert a new record
                db.session.execute(
                    text(
                        f"INSERT INTO {db_name} (user_id, env_key, env_value) VALUES (:user_id, "
                        ":env_key, :env_value)"),
                    {"user_id": current_user.id, "env_key": env_key, "env_value": env_value}
                )

            db.session.commit()

        results = db.session.execute(
            text(f"SELECT env_value FROM {db_name} WHERE env_key=:env_key"),
            {"env_key": env_key})
        return results.scalar()

    if current_user.role == 'admin':
        kc_api_key = get_or_update_env_db(current_user, db, 'KC_API_KEY', json_data, keys_db)
        kc_api_secret = get_or_update_env_db(current_user, db, 'KC_API_SECRET', json_data, keys_db)
        kc_api_passphrase = get_or_update_env_db(current_user, db, 'KC_API_PASSPHRASE', json_data, keys_db)

        return {
            'KC_API_KEY': kc_api_key,
            'KC_API_SECRET': kc_api_secret,
            'KC_API_PASSPHRASE': kc_api_passphrase
        }
    else:
        return {
            'KC_API_KEY': '',
            'KC_API_SECRET': '',
            'KC_API_PASSPHRASE': ''
        }


def fz_fetcher_fetch_pair(current_user, db, User, GasamApp, json_data, files_data):
    from sqlalchemy import text
    from datetime import datetime, timedelta
    import pytz
    global keys_db

    def insert_data_into_db(db, db_name, data, pair_id):
        try:
            # Erase all records from the table
            db.session.execute(text(f"DELETE FROM {db_name}"))
            db.session.commit()

            for record in data:
                db.session.execute(
                    text(
                        f"INSERT INTO {db_name} (pair_id, time, open, high, low, close, volume, notes) VALUES "
                        "(:pair_id, :time, :open, :high, :low, :close, :volume, :notes)"
                    ),
                    {
                        "pair_id": pair_id,
                        "time": record["time"],
                        "open": record["open"],
                        "high": record["high"],
                        "low": record["low"],
                        "close": record["close"],
                        "volume": record["volume"],
                        "notes": '',
                    },
                )
            db.session.commit()
            return {"status": "good"}
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}



    KC_API_KEY = get_env_value_from_env_or_db(db, keys_db, 'KC_API_KEY')
    KC_API_SECRET = get_env_value_from_env_or_db(db, keys_db, 'KC_API_SECRET')
    KC_API_PASSPHRASE = get_env_value_from_env_or_db(db, keys_db, 'KC_API_PASSPHRASE')

    end_time = datetime.now(pytz.UTC)
    days_go_back = 744 # 2+ YEARS OF DATA
    start_time = end_time - timedelta(days=days_go_back)
    candle_data = []

    # ATTENTION - MAXIMUM AMOUNT OF DATA THAT CAN BE FETCHED IS 1500 DATA POINTS.
    # I WOULD HAVE TO GO THROUGH CYCLES TO FETCH 17520 DATA POINTS
    interim_end = datetime.now(pytz.UTC)
    interim_start = interim_end - timedelta(days=62)
    while start_time <= interim_start:
        candle_data += fetch_kucoin_data(json_data['pair'],
                                        interim_start,
                                        interim_end,
                                        '1hour',
                                        KC_API_KEY,
                                        KC_API_SECRET, KC_API_PASSPHRASE)[::-1]
        interim_end = interim_start
        interim_start = interim_start - timedelta(days=62)

    candle_data = candle_data[::-1]

    #INSERT INTO DATABASE
    status = insert_data_into_db(db, 'app_fi_zelf_alchemy_testPair_db', candle_data, json_data['pair'])

    if status['status'] == 'good':
        status['status'] = (f'Old Data erased. New data {json_data["pair"]} 1hour for {days_go_back} days inserted. {len(candle_data)} records are '
                  f'locked and loaded.')
        status['ready_to_feed'] = True
    else:
        status['ready_to_feed'] = False

    return status


def fz_fetcher_fetch_kucoin_coin_price(db, timestamp, pair):
    from datetime import datetime, timedelta
    import pytz
    global keys_db

    KC_API_KEY = get_env_value_from_env_or_db(db, keys_db, 'KC_API_KEY')
    KC_API_SECRET = get_env_value_from_env_or_db(db, keys_db, 'KC_API_SECRET')
    KC_API_PASSPHRASE = get_env_value_from_env_or_db(db, keys_db, 'KC_API_PASSPHRASE')

    start = datetime.fromtimestamp(timestamp, pytz.UTC)
    end = start + timedelta(hours=1)

    data = fetch_kucoin_data(
        symbol=pair,
        start_time=start,
        end_time=end,
        interval='1hour',
        API_KEY=KC_API_KEY,
        API_SECRET=KC_API_SECRET,
        API_PASSPHRASE=KC_API_PASSPHRASE
    )

    return data


def fz_fetcher_send_placed_order(order_data):
    global keys_db
    # FUNCTION WILL BE WRITTEN FOR THE WORKHORSE

    return True

def fz_fetcher_update_orders(db, bank_db, trade_data): #ALCHEMY FUNCTION, can be dirty
    from .fz_feeder import fz_feeder_cycle_last_candle
    import pytz
    from datetime import datetime
    global keys_db

    # FUNCTION WILL BE RE-WRITTEN FOR THE WORKHORSE
    updated_trade_data = []

    now = datetime.now(pytz.UTC)
    date_filled = int(now.timestamp())

    for trade in trade_data:
        # print(trade)
        if trade['trade_entry'] == 'limit':

            updated_trade_data.append(
                {
                    'id': trade['id'],
                    'trade_id': trade['trade_id'],
                    'trade_status': 'filled',
                    'trade_type': trade['trade_type'],
                    'trade_position': trade['trade_position'],
                    'is_flagged': True,
                    'date_filled': date_filled,
                    'currency_sell': trade['currency_sell'],
                    'amount_sell': trade['amount_sell'],
                    'currency_buy': trade['currency_buy'],
                    'amount_buy': trade['amount_buy'],
                    'price': trade['price'],
                    'tdp_1': fz_feeder_cycle_last_candle['time']
                })
        elif trade['trade_entry'] == 'stop-limit':
            scan_since = trade['tdp_0']
            scan_until = fz_feeder_cycle_last_candle['time']
            trade_entry_stop = trade['trade_entry_stop']
            if check_if_reached_stop_limit(db, scan_since, scan_until, trade_entry_stop, trade):
                updated_trade_data.append(
                    {
                        'id': trade['id'],
                        'trade_id': trade['trade_id'],
                        'trade_status': 'filled',
                        'trade_type': trade['trade_type'],
                        'trade_position': trade['trade_position'],
                        'is_flagged': True,
                        'date_filled': date_filled,
                        'currency_sell': trade['currency_sell'],
                        'amount_sell': trade['amount_sell'],
                        'currency_buy': trade['currency_buy'],
                        'amount_buy': trade['amount_buy'],
                        'price': trade['price'],
                        'tdp_1': fz_feeder_cycle_last_candle['time']
                    })

    return updated_trade_data

def fetch_kucoin_data(symbol, start_time, end_time, interval, API_KEY, API_SECRET, API_PASSPHRASE):
    import pytz
    import requests
    import time
    from datetime import datetime, timedelta

    def get_kucoin_signature(timestamp, method, endpoint, API_SECRET, body=''):
        import base64
        import hmac
        import hashlib

        string_to_sign = timestamp + method + endpoint + body
        signature = base64.b64encode(
            hmac.new(API_SECRET.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha256).digest()
        )
        return signature.decode('utf-8')

    base_url = "https://api.kucoin.com"
    endpoint = f"/api/v1/market/candles"

    # Convert start_time and end_time to UTC
    start_time_utc = start_time.astimezone(pytz.UTC)
    end_time_utc = end_time.astimezone(pytz.UTC)

    api_interval = interval
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

            return valid_data

        else:
            print(f"API returned unexpected data structure: {data}")
            return []
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []


def get_env_value_from_env_or_db(db, db_name, env_key):
    import os
    from sqlalchemy import text
    if os.getenv(env_key):
        env_value = os.getenv(env_key)
    else:
        results = db.session.execute(
            text(f"SELECT env_value FROM {db_name} WHERE env_key=:env_key"),
            {"env_key": env_key})
        env_value = results.scalar()

    return env_value


def check_if_reached_stop_limit(db, scan_since, scan_until, trade_entry_stop, trade):
    from sqlalchemy.sql import text

    # Define your query parameters
    query_params = {
        "scan_since": scan_since,  # Replace with your value for scan_since
        "scan_until": scan_until  # Replace with your value for scan_until
    }

    # SQL query
    query = text("""
        SELECT high, low, time
        FROM app_fi_zelf_alchemy_testPair_db
        WHERE time > :scan_since AND time <= :scan_until
    """)

    # Execute the query
    results = db.session.execute(query, query_params).fetchall()

    # Process the results
    for row in results:
        # print(row)
        high = row[0]
        low = row[1]
        # trade_type = db.Column(db.String(100), nullable=False)  # spot, futures
        # trade_position = db.Column(db.String(100), nullable=False) # long/short

        # if trade['trade_position'] == 'short':
        #     if trade['trade_action'] == 'buy':
        #         if low <= trade_entry_stop:
        #             print(f'TRUE low {low} <= trade_entry_stop {trade_entry_stop}')
        #             return True
        #     elif trade['trade_action'] == 'sell':
        #         if trade_entry_stop <= high:
        #             print(f'TRUE trade_entry_stop {trade_entry_stop} <= high {high}')
        #             return True
        # else:
        #     if trade['trade_action'] == 'sell':
        #         if low <= trade_entry_stop:
        #             print(f'TRUE low {low} <= trade_entry_stop {trade_entry_stop}')
        #             return True
        #     elif trade['trade_action'] == 'buy':
        #         if trade_entry_stop <= high:
        #             print(f'TRUE trade_entry_stop {trade_entry_stop} <= high {high}')
        #             return True
        if low <= trade_entry_stop <= high:
                print(f'TRUE low {low} <= trade_entry_stop {trade_entry_stop} <= high {high}')
                return True
    return False


