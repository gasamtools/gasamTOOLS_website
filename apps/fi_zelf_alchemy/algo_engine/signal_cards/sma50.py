from ._common_functions import *

def sma50(db, signal_db, candle_formats, pair):
    to_postman, to_crystal = '', ''

    # ANALYZE NEW SIGNALS
    # GET SMA data
    new_1day = calculate_moving_average_series_data(candle_formats['1day'], 50)
    new_1week = calculate_moving_average_series_data(candle_formats['1week'], 50)
    new_1month = calculate_moving_average_series_data(candle_formats['1month'], 50)

    # GET SMA proxy data
    new_proxy_1day = convert_to_proxy(pair, '1day', 'SMA50', new_1day, candle_formats['1day'])
    new_proxy_1week = convert_to_proxy(pair, '1week', 'SMA50', new_1week, candle_formats['1week'])
    new_proxy_1month = convert_to_proxy(pair, '1month', 'SMA50', new_1month, candle_formats['1month'])

    # FETCH RECORDED SIGNALS FROM DB
    record_proxy_1day = fetch_from_db(db, signal_db, pair, '1day', 'SMA50')
    record_proxy_1week = fetch_from_db(db, signal_db, pair, '1week', 'SMA50')
    record_proxy_1month = fetch_from_db(db, signal_db, pair, '1month', 'SMA50')

    # COMPARE NEW vs RECORDED SIGNALS AND RECORD NEW SIGNALS IF NOT RECORDED
    # UPDATE to_postman, to_crystal

    data_1day = compare_and_update_db(db, signal_db, new_proxy_1day, record_proxy_1day)
    to_postman += data_1day['to_postman']
    to_crystal += data_1day['to_crystal']
    data_1week = compare_and_update_db(db, signal_db, new_proxy_1week, record_proxy_1week)
    to_postman += data_1week['to_postman']
    to_crystal += data_1week['to_crystal']
    data_1month = compare_and_update_db(db, signal_db, new_proxy_1month, record_proxy_1month)
    to_postman += data_1month['to_postman']
    to_crystal += data_1month['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


def calculate_moving_average_series_data(candle_data, ma_length):
    ma_data = []

    for i in range(len(candle_data)):
        if i < ma_length:
            # Add whitespace data points until MA can be calculated
            ma_data.append({'time': candle_data[i]['time']})
        else:
            # Calculate the moving average
            sum_close = 0
            for j in range(ma_length):
                sum_close += candle_data[i - j]['close']
            ma_value = sum_close / ma_length
            ma_data.append({'time': candle_data[i]['time'], 'value': ma_value})

            if ma_value <= candle_data[i]['low']:
                ma_data[i]['ma_marker'] = 'bull'
            else:
                ma_data[i]['ma_marker'] = 'bear'

    return ma_data


def convert_to_proxy(trading_pair: str, interval: str, signal_type: str, signal_data, candles_data):
    # trading_pair, interval, signal_type, is_trend_valid, trend_type, sdp_0-'trend start
    reversed_signal_data = signal_data[::-1]
    reversed_candles_data = candles_data[::-1]

    if 'ma_marker' in reversed_signal_data[0]:
        trend_type = reversed_signal_data[0]['ma_marker']
    else:
        return {'no_signal': True}

    trend_start = 0
    for candle in reversed_signal_data:
        if 'ma_marker' in candle and candle['ma_marker'] != trend_type:
            trend_start = candle['time']
            break

    return {
        'trading_pair': trading_pair,
        'interval': interval,
        'signal_type': signal_type,
        'is_trend_valid': True,
        'trend_type': trend_type,
        'sdp_0': trend_start,
        'tp_entrance_1': reversed_candles_data[0]['close']

    }


def compare_and_update_db(db, signal_db, new_proxy, record_proxy):
    to_postman, to_crystal = '', ''

    if 'no_signal' in new_proxy:
        # print('no_signal')
        return {
            'to_postman': to_postman,
            'to_crystal': to_crystal
        }

    elif not record_proxy:
        insert_into_db_data = insert_into_signal_db(db, signal_db, new_proxy)
        to_postman += insert_into_db_data['to_postman']
        to_crystal += insert_into_db_data['to_crystal']
        # print('not record_proxy')
        return {
            'to_postman': to_postman,
            'to_crystal': to_crystal
        }
    else:
        if int(new_proxy['sdp_0']) == int(record_proxy['sdp_0']):
            # print("new_proxy['sdp_0'] == record_proxy['sdp_0']")
            return {
                'to_postman': to_postman,
                'to_crystal': to_crystal
            }
        else:
            # print("recording new signal")
            # print(f"{new_proxy['sdp_0']} VS {record_proxy['sdp_0']}")
            flag_signal_data = flag_signal(db, signal_db, record_proxy, new_proxy['sdp_0'])
            to_postman += flag_signal_data['to_postman']
            to_crystal += flag_signal_data['to_crystal']

            insert_into_db_data = insert_into_signal_db(db, signal_db, new_proxy)
            to_postman += insert_into_db_data['to_postman']
            to_crystal += insert_into_db_data['to_crystal']

            return {
                'to_postman': to_postman,
                'to_crystal': to_crystal
            }
