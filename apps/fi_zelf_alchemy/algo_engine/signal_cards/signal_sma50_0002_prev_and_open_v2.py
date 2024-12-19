#signal_sma50_0002_prev_and_open_v2
# assigns trend only when entire candle is not touching MA. otherwise it is 'between'
# confirms the trend change only when previous candle and current candle are both of the same trend
# re-activates trend it has the same start time and trend_type

from ._common_functions import *

def signal_sma50_0002_prev_and_open_v2(db, signal_db, candle_formats, pair):
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

    # FETCH ALL RECORDED SIGNALS FROM DB
    all_record_proxies_1day = fetch_all_from_db(db, signal_db, pair, '1day', 'SMA50')
    all_record_proxies_1week = fetch_all_from_db(db, signal_db, pair, '1week', 'SMA50')
    all_record_proxies_1month = fetch_all_from_db(db, signal_db, pair, '1month', 'SMA50')

    # FETCH ACTIVE RECORDED SIGNALS FROM DB
    active_record_proxies_1day = fetch_active_from_db(db, signal_db, pair, '1day', 'SMA50')
    active_record_proxies_1week = fetch_active_from_db(db, signal_db, pair, '1week', 'SMA50')
    active_record_proxies_1month = fetch_active_from_db(db, signal_db, pair, '1month', 'SMA50')

    # COMPARE NEW vs RECORDED SIGNALS AND RECORD NEW SIGNALS IF NOT RECORDED
    # UPDATE to_postman, to_crystal

    data_1day = compare_and_update_db(db, signal_db, new_proxy_1day, all_record_proxies_1day, active_record_proxies_1day)
    to_postman += data_1day['to_postman']
    to_crystal += data_1day['to_crystal']
    data_1week = compare_and_update_db(db, signal_db, new_proxy_1week, all_record_proxies_1week, active_record_proxies_1week)
    to_postman += data_1week['to_postman']
    to_crystal += data_1week['to_crystal']
    data_1month = compare_and_update_db(db, signal_db, new_proxy_1month, all_record_proxies_1month, active_record_proxies_1month)
    to_postman += data_1month['to_postman']
    to_crystal += data_1month['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal,
        'new_1day': new_1day #send data to fz_crystal.py via signal_engine.py
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

            if ma_value < candle_data[i]['low']:
                ma_data[i]['ma_marker'] = 'bull'
            elif ma_value > candle_data[i]['high']:
                ma_data[i]['ma_marker'] = 'bear'
            else:
                ma_data[i]['ma_marker'] = 'between'

    return ma_data


def convert_to_proxy(trading_pair: str, interval: str, signal_type: str, signal_data, candles_data):
    # trading_pair, interval, signal_type, is_trend_valid, trend_type, sdp_0-'trend start
    reversed_signal_data = signal_data[::-1]
    reversed_candles_data = candles_data[::-1]

    if 'ma_marker' not in reversed_signal_data[0]:
        return {'no_signal': True}

    trend_start = 0
    trend_type = False
    trend_confirmed = False
    possible_trend_start = False
    for index, candle in enumerate(reversed_signal_data):
        if 'ma_marker' in candle and candle['ma_marker'] != 'between':
            if not trend_type:
                trend_type = candle['ma_marker']
                if 'ma_marker' in reversed_signal_data[index+1] and reversed_signal_data[index+1]['ma_marker'] == trend_type:
                    trend_confirmed = True
                if not trend_confirmed:
                    trend_type = False

        if trend_type:
            if 'ma_marker' in candle and candle['ma_marker'] != trend_type:
                if candle['ma_marker'] == 'between':
                    if not possible_trend_start:
                        possible_trend_start = reversed_signal_data[index-1]['time']
                else:
                    if possible_trend_start:
                        trend_start = possible_trend_start
                    else:
                        trend_start = reversed_signal_data[index-1]['time']
                    break
            else:
                possible_trend_start = False

    if trend_type:
        return {
            'trading_pair': trading_pair,
            'interval': interval,
            'signal_type': signal_type,
            'is_trend_valid': True,
            'trend_type': trend_type,
            'sdp_0': trend_start,
            'tp_entrance_1': reversed_candles_data[0]['close']

        }
    else:
        return {'no_signal': True}


def compare_and_update_db(db, signal_db, new_proxy, all_record_proxies, active_record_proxy):
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''
    print(new_proxy)
    if 'no_signal' in new_proxy:
        return {
            'to_postman': to_postman,
            'to_crystal': to_crystal
        }

    elif not active_record_proxy:
        print('went here')
        insert_into_db_data = insert_into_signal_db(db, signal_db, new_proxy)
        to_postman += insert_into_db_data['to_postman']
        to_crystal += insert_into_db_data['to_crystal']
        return {
            'to_postman': to_postman,
            'to_crystal': to_crystal
        }
    else:
        records_dont_match = True
        for record in all_record_proxies:
            if int(new_proxy['sdp_0']) == int(record['sdp_0']) and new_proxy['trend_type'] == record['trend_type']:
                records_dont_match = False
                if record['id'] != active_record_proxy['id']:
                    reactivate_signal_data = reactivate_signal(db, signal_db, record)
                    to_postman += reactivate_signal_data['to_postman']
                    to_crystal += reactivate_signal_data['to_crystal']

                    sdp_1 = fz_feeder_cycle_last_candle['time']
                    flag_signal_data = flag_signal(db, signal_db, active_record_proxy, int(sdp_1))
                    to_postman += flag_signal_data['to_postman']
                    to_crystal += flag_signal_data['to_crystal']

        if records_dont_match:
            if int(new_proxy['sdp_0']) >= int(active_record_proxy['sdp_0']):
                sdp_1 = new_proxy['sdp_0']
            else:
                sdp_1 = fz_feeder_cycle_last_candle['time']
            flag_signal_data = flag_signal(db, signal_db, active_record_proxy, int(sdp_1))
            to_postman += flag_signal_data['to_postman']
            to_crystal += flag_signal_data['to_crystal']

            insert_into_db_data = insert_into_signal_db(db, signal_db, new_proxy)
            to_postman += insert_into_db_data['to_postman']
            to_crystal += insert_into_db_data['to_crystal']


        return {
            'to_postman': to_postman,
            'to_crystal': to_crystal
        }
