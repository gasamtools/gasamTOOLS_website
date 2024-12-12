from ._common_functions import *

def litmus(db, signal_db, candle_formats, pair):
    from sqlalchemy import text
    from datetime import datetime, timezone, timedelta
    to_postman, to_crystal = '', ''

    last_candle_of_cycle = candle_formats['1day'][-1]

    existing_litmus = fetch_active_from_db(db, signal_db, pair, '1day', 'litmus')
    if not existing_litmus:

        new_proxy = {
            "trading_pair": pair,
            "interval": '1day',
            "signal_type": 'litmus',
            "is_trend_valid": True,
            "trend_type": 'bull',
            "sdp_0": last_candle_of_cycle['time'],
            "tp_entrance_1": last_candle_of_cycle['close']
        }
        insert_into_db_data = insert_into_signal_db(db, signal_db, new_proxy)
        to_postman += insert_into_db_data['to_postman']
        to_crystal += insert_into_db_data['to_crystal']

    last_record_of_db_data = db.session.execute(
        text(f"SELECT * FROM app_fi_zelf_alchemy_testPair_db ORDER BY record_id DESC LIMIT 1")
    ).mappings().first()
    last_record_of_db_data_day_ts = datetime.fromtimestamp(last_record_of_db_data['time'], tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    if last_candle_of_cycle['time'] == last_record_of_db_data_day_ts:
        flag_signal_data = flag_signal(db, signal_db, existing_litmus, last_record_of_db_data_day_ts)
        to_postman += flag_signal_data['to_postman']
        to_crystal += flag_signal_data['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }