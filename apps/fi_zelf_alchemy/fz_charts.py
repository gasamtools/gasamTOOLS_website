hodl = False
from sqlalchemy.sql import text


def gather_data_chart_1(**input_data):
    global hodl
    from .algo_engine.signal_engine import signal_data_for_crystal
    from .algo_engine.vault_engine import fund_futures_ini_usdt_value

    if not hodl:
        hodl = fund_futures_ini_usdt_value / float(input_data['candle'])

    charts_1_data = {}
    if is_midnight_utc(input_data['timestamp']):

        charts_1_data['timestamp'] = input_data['timestamp']
        charts_1_data['candle'] = input_data['candle']
        charts_1_data['sma'] = signal_data_for_crystal['SMA50'][-1]['value']
        charts_1_data['bot'] = input_data['bank']['total']
        charts_1_data['hodl'] = hodl * float(input_data['candle'])

    print(f'charts_1_data {charts_1_data}')
    return charts_1_data


def recordDataToDB(db, charts_db, data):
    print(data)
    return



def is_midnight_utc(unix_timestamp):
    from datetime import datetime, time
    import pytz
    # Convert Unix timestamp to UTC datetime
    dt = datetime.fromtimestamp(unix_timestamp, tz=pytz.UTC)
    return dt.hour == 0 and dt.minute == 0

