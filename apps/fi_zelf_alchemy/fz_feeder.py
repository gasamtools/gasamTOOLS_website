fz_feeder_cycle_timestamp = 0
fz_feeder_cycle_last_candle = []

def fz_feeder(current_user, db, User, GasamApp, json_data, files_data, testPair_db, signal_db, trade_db, bank_db, signal_trade_db,):
    if json_data['js_function_sub'] == 'main':
        return fz_feeder_main(current_user, db, User, GasamApp, json_data, files_data, testPair_db, signal_db, trade_db, bank_db, signal_trade_db,)


def fz_feeder_main(current_user, db, User, GasamApp, json_data, files_data, testPair_db, signal_db, trade_db, bank_db, signal_trade_db,):
    from sqlalchemy import text
    from datetime import datetime
    from .algo_engine.algo_engine import algo_engine
    from .fz_crystal import printSignals
    import pytz
    global fz_feeder_cycle_timestamp
    global fz_feeder_cycle_last_candle

    def transform_candles(daily_data, interval):
        def get_period_start(timestamp, interval):
            import pytz
            from datetime import datetime, timedelta

            date = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
            if interval == '1week':
                start = date - timedelta(days=date.weekday())
            elif interval == '1month':
                start = date.replace(day=1)
            else:
                start = date  # For daily or other intervals, use the date as is
            return int(start.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

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

    feederCycle = int(json_data['feederCycle'])

    total_candles = db.session.execute(
        text(f"SELECT COUNT(*) FROM {testPair_db}")
    ).scalar()  # Use .scalar() to get a single value

    fastForwardmultiplier = 100
    if json_data['command'] == 'fastForward':
        feederCycle += fastForwardmultiplier
    else:
        feederCycle += 1

    start_cycle_range_days = 250
    feeder_cycle_range_candles = (start_cycle_range_days * 24) + feederCycle

    if json_data['command'] == 'allForward':
        feeder_cycle_range_candles = total_candles
        feederCycle = total_candles - (start_cycle_range_days * 24)


    existing_records = db.session.execute(
        text(f"SELECT * FROM {testPair_db} ORDER BY record_id ASC LIMIT {feeder_cycle_range_candles}")
    )

    records = existing_records.fetchall()
    pair = records[0][1]
    hourly_candles = []
    for record in records:
        hourly_candles.append({
            "time": record[2],
            "open": record[3],
            "high": record[4],
            "low": record[5],
            "close": record[6],
            "volume": record[7]
        })

    # FEEDING DATA TO ALGO ENGINE
    if json_data['command'] == 'allForward':
        algo_engine_data = {
            'to_postman': '',
            'to_crystal': ''
        }
        for i in range(0, (total_candles-(start_cycle_range_days * 24))):
            print(f'{i} of {total_candles-(start_cycle_range_days * 24)}')
            candle_formats = {
                '1day': transform_candles(hourly_candles[0:(-total_candles+(start_cycle_range_days * 24)+i)], '1day'),
                '1week': transform_candles(hourly_candles[0:(-total_candles+(start_cycle_range_days * 24)+i)], '1week'),
                '1month': transform_candles(hourly_candles[0:(-total_candles+(start_cycle_range_days * 24)+i)], '1month'),
            }
            
            # ASSIGN CURRENT LATEST CANDLE TIMESTAMP
            adjusted_hourly_candles = hourly_candles[0:(-total_candles+(start_cycle_range_days * 24)+i)]
            fz_feeder_cycle_timestamp = adjusted_hourly_candles[-1]['time']
            fz_feeder_cycle_last_candle = adjusted_hourly_candles[-1]


            # SEND DATA TO ALGO ENGINE
            algo_engine_data_cycle = algo_engine(db, signal_db, trade_db, bank_db, signal_trade_db, json_data, candle_formats, pair, 'run_engine')
            algo_engine_data['to_postman'] += algo_engine_data_cycle['to_postman']
            algo_engine_data['to_crystal'] += algo_engine_data_cycle['to_crystal']

    elif json_data['command'] == 'fastForward':
        algo_engine_data = {
            'to_postman': '',
            'to_crystal': ''
        }
        for i in range(0, fastForwardmultiplier):
            candle_formats = {
                '1day': transform_candles(hourly_candles[0:(-fastForwardmultiplier+i)], '1day'),
                '1week': transform_candles(hourly_candles[0:(-fastForwardmultiplier+i)], '1week'),
                '1month': transform_candles(hourly_candles[0:(-fastForwardmultiplier+i)], '1month'),
            }

            # ASSIGN CURRENT LATEST CANDLE TIMESTAMP
            adjusted_hourly_candles = hourly_candles[0:(-fastForwardmultiplier+i)]
            fz_feeder_cycle_timestamp = adjusted_hourly_candles[-1]['time']
            fz_feeder_cycle_last_candle = adjusted_hourly_candles[-1]


            # SEND DATA TO ALGO ENGINE
            algo_engine_data_cycle = algo_engine(db, signal_db, trade_db, bank_db, signal_trade_db, json_data, candle_formats, pair, 'run_engine')
            algo_engine_data['to_postman'] += algo_engine_data_cycle['to_postman']
            algo_engine_data['to_crystal'] += algo_engine_data_cycle['to_crystal']
    else:
        candle_formats = {
            '1day': transform_candles(hourly_candles, '1day'),
            '1week': transform_candles(hourly_candles, '1week'),
            '1month': transform_candles(hourly_candles, '1month')
        }

        # ASSIGN CURRENT LATEST CANDLE TIMESTAMP
        fz_feeder_cycle_timestamp = hourly_candles[-1]['time']
        fz_feeder_cycle_last_candle = hourly_candles[-1]

        # SEND DATA TO ALGO ENGINE
        algo_engine_data = algo_engine(db, signal_db, trade_db, bank_db, signal_trade_db, json_data, candle_formats, pair, 'run_engine')


    # FETCHING DATA FROM CRYSTAL ENGINE
    printSignals_data = printSignals(db, signal_db, trade_db, signal_trade_db, json_data)

    # SEND STATUS
    status = ''
    utc_timezone = pytz.UTC
    if json_data['command'] == 'allForward':
        for i in range(0, (total_candles-(start_cycle_range_days * 24))):
            dt_utc = datetime.fromtimestamp(hourly_candles[-total_candles+(start_cycle_range_days * 24) + i]['time'], utc_timezone)
            formatted_time = f"{dt_utc.strftime('%y-%m-%d %H')}:00 UTC"
            status += f"<p>candles up to {formatted_time}</p>"
    elif json_data['command'] == 'fastForward':
        for i in range(0, fastForwardmultiplier):
            dt_utc = datetime.fromtimestamp(hourly_candles[-fastForwardmultiplier + i]['time'], utc_timezone)
            formatted_time = f"{dt_utc.strftime('%y-%m-%d %H')}:00 UTC"
            status += f"<p>candles up to {formatted_time}</p>"
    else:
        dt_utc = datetime.fromtimestamp(hourly_candles[-1]['time'], utc_timezone)
        formatted_time = f"{dt_utc.strftime('%y-%m-%d %H')}:00 UTC"
        status = f"<p>candles up to {formatted_time}</p>"

    if len(hourly_candles) == total_candles:
        end_of_test = True
        status += f"<p>TEST COMPLETE</p>"
    else:
        end_of_test = False

    daily_candles = transform_candles(hourly_candles, '1day')


    return_data = {
        'candles': daily_candles,
        'last_hour_timestamp': hourly_candles[-1]['time'],
        'pair': pair,
        'status': status,
        'feederCycle': feederCycle,
        'end_of_test': end_of_test,
        'to_postman': algo_engine_data['to_postman'],
        'to_crystal': algo_engine_data['to_crystal'],
        'printSignals': printSignals_data
    }

    #print(return_data)

    return return_data
