def fz_feeder(current_user, db, User, GasamApp, json_data, files_data, testPair_db):
    if json_data['js_function_sub'] == 'main':
        return fz_feeder_main(current_user, db, User, GasamApp, json_data, files_data, testPair_db)


def fz_feeder_main(current_user, db, User, GasamApp, json_data, files_data, testPair_db):
    from sqlalchemy import text
    from datetime import datetime
    from .algo_engine.algo_engine import algo_engine
    import pytz

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

    fastForwardmultiplier = 100
    if json_data['command'] == 'fastForward':
        feederCycle += fastForwardmultiplier
    else:
        feederCycle += 1

    start_cycle_range_days = 250
    feeder_cycle_range_candles = (start_cycle_range_days * 24) + feederCycle


    total_candles = db.session.execute(
        text(f"SELECT COUNT(*) FROM {testPair_db}")
    ).scalar()  # Use .scalar() to get a single value

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
    if json_data['command'] == 'fastForward':
        for i in range(0, fastForwardmultiplier):
            candle_formats = {
                '1day': transform_candles(hourly_candles[0:(-fastForwardmultiplier+i)], '1day'),
                '1week': transform_candles(hourly_candles[0:(-fastForwardmultiplier+i)], '1week'),
                '1month': transform_candles(hourly_candles[0:(-fastForwardmultiplier+i)], '1month'),
            }
            algo_engine_data = algo_engine(db, json_data, candle_formats, pair, 'run_engine')
    else:
        candle_formats = {
            '1day': transform_candles(hourly_candles, '1day'),
            '1week': transform_candles(hourly_candles, '1week'),
            '1month': transform_candles(hourly_candles, '1month')
        }
        algo_engine_data = algo_engine(db, json_data, candle_formats, pair, 'run_engine')

    # SEND SATUS
    status = ''
    utc_timezone = pytz.UTC
    if json_data['command'] == 'fastForward':
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
    }

    #print(return_data)

    return return_data
