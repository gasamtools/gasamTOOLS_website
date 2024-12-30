fz_feeder_cycle_last_candle = []
sent_chart_data = False

def fz_feeder(current_user, db, db_names, User, GasamApp, json_data, files_data):
    if json_data['js_function_sub'] == 'main':
        return fz_feeder_main(current_user, db, db_names, User, GasamApp, json_data, files_data)


def fz_feeder_main(current_user, db, db_names, User, GasamApp, json_data, files_data):
    from sqlalchemy import text
    from .fz_crystal import printSignals, printAlchemyFeed
    from .fz_charts import export_data_chart_1
    from .algo_engine.signal_engine import signal_id
    from .algo_engine.vault_engine import vault_id

    # GET TOTAL AMOUNT OF CANDLES FROM DB used for fastForward and to determine if test is complete
    total_candles = db.session.execute(
        text(f"SELECT COUNT(*) FROM {db_names['testPair_db']}")
    ).scalar()  # Use .scalar() to get a single value

    fastForwardmultiplier = 100 # USED FOR fastForward MODE
    start_cycle_range_days = 250 # USED TO FEED INITIAL DATA SO SMA50

    feederCycle = int(json_data['feederCycle']) # FETCH feederCycle FROM JS/FRONT END
    if json_data['command'] == 'fastForward':
        feederCycle += fastForwardmultiplier
        feeder_cycle_range_candles = (start_cycle_range_days * 24) + feederCycle
    elif json_data['command'] == 'allForward':
        feederCycle = total_candles - (start_cycle_range_days * 24)
        feeder_cycle_range_candles = total_candles
    else:
        feederCycle += 1
        feeder_cycle_range_candles = (start_cycle_range_days * 24) + feederCycle

    # FETCH DATA FROM testPair DB AND TRANSFORM TO HOURLY CANDLES
    hourly_candles = get_hourly_candles_within_range_from_db(db, db_names['testPair_db'], feeder_cycle_range_candles)[0]
    pair = get_hourly_candles_within_range_from_db(db, db_names['testPair_db'], feeder_cycle_range_candles)[1]

    # FEEDING DATA TO ALGO ENGINE
    algo_engine_data, bank_spot_values_data, bank_futures_values_data = handle_algo_engine_command(db, db_names,
        json_data, hourly_candles, pair,feederCycle=feederCycle, fastForwardmultiplier=fastForwardmultiplier)

    # FETCHING DATA FROM CRYSTAL ENGINE
    printSignals_data = printSignals(db, db_names, json_data)

    # GENERATE STATUS FOR ALCHEMY FEED
    printAlchemyFeed_data = printAlchemyFeed(json_data['command'], feederCycle, hourly_candles, total_candles, fastForwardmultiplier)

    # PRINT CANDLES ON TradingVIew CHART
    daily_candles = transform_candles(hourly_candles, '1day')

    # SEND CHART DATA TO GOOGLE SHEET IF THE END OF TEST
    global sent_chart_data
    # to_feed = export_data_chart_1(db, db_names['charts_1_db'], db_names['trade_db'], f'{signal_id}_{vault_id}_{pair}')
    # printAlchemyFeed_data['status'] += to_feed

    if printAlchemyFeed_data['end_of_test'] and not sent_chart_data:
        to_feed = export_data_chart_1(db, db_names['charts_1_db'], db_names['trade_db'], f'{signal_id}_{vault_id}_{pair}')
        printAlchemyFeed_data['status'] += to_feed
        sent_chart_data = True

    return_data = {
        'candles': daily_candles,
        'last_hour_timestamp': hourly_candles[-1]['time'],
        'pair': pair,
        'alchemyFeed': printAlchemyFeed_data['status'],
        'feederCycle': feederCycle,
        'end_of_test': printAlchemyFeed_data['end_of_test'],
        'to_postman': algo_engine_data['to_postman'],
        'to_crystal': algo_engine_data['to_crystal'],
        'printSignals': printSignals_data,
        'bank_spot_values_data': bank_spot_values_data,
        'bank_futures_values_data': bank_futures_values_data,
    }

    return return_data

def get_hourly_candles_within_range_from_db(db, testPair_db, feeder_cycle_range_candles):
    from sqlalchemy import text
    # GET CANDLES WITHIN THE SPECIFIC RANGE
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

    return [hourly_candles, pair]


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


def process_algo_engine(db, db_names, json_data, hourly_candles, pair, cycle_range=None):
    """
    Process algorithm engine data based on command type and cycle range.

    Args:
        db: Database connection
        signal_db: Signal database connection
        trade_db: Trade database connection
        bank_db: Bank database connection
        futures_db: Futures database connection
        signal_trade_db: Signal trade database connection
        json_data: Dictionary containing command and other parameters
        hourly_candles: List of hourly candle data
        pair: Trading pair
        cycle_range: Optional range for cycling through candles

    Returns:
        Dictionary containing algorithm engine data
    """
    from .algo_engine.algo_engine import algo_engine
    from .fz_charts import gather_data_chart_1, record_data_chart_1
    global fz_feeder_cycle_last_candle

    algo_engine_data = {
        'to_postman': '',
        'to_crystal': ''
    }

    # If no cycle range is provided, process once
    if cycle_range is None:
        cycle_range = [0]

    for i in cycle_range:
        # Calculate candle slice based on command type
        if json_data.get('command') == 'allForward':
            candle_slice = hourly_candles[0:(i - len(cycle_range))]
        elif json_data.get('command') == 'fastForward':
            candle_slice = hourly_candles[0:(-len(cycle_range) + i)]
        else:
            candle_slice = hourly_candles

        # Transform candles for different timeframes
        candle_formats = {
            '1day': transform_candles(candle_slice, '1day'),
            '1week': transform_candles(candle_slice, '1week'),
            '1month': transform_candles(candle_slice, '1month')
        }

        # Get the latest candle timestamp
        fz_feeder_cycle_last_candle = candle_slice[-1]

        # Process algo engine data
        algo_engine_data_cycle = algo_engine(
            db, db_names,
            json_data, candle_formats, pair, 'run_engine'
        )

        # Accumulate results if in a cycle
        if cycle_range != [0]:
            algo_engine_data['to_postman'] += algo_engine_data_cycle['to_postman']
            algo_engine_data['to_crystal'] += algo_engine_data_cycle['to_crystal']
        else:
            algo_engine_data = algo_engine_data_cycle

        # Get bank values
        bank_spot_values_data = algo_engine(db, db_names,
            {}, fz_feeder_cycle_last_candle['time'], {}, 'get_bank_spot_values'
        )

        bank_futures_values_data = algo_engine(db, db_names,
            {}, fz_feeder_cycle_last_candle['time'], {}, 'get_bank_futures_values'
        )

        # GATHER AND RECORD DATA FOR CHART 1
        charts_1_data = gather_data_chart_1(
            timestamp=fz_feeder_cycle_last_candle['time'],
            candle=fz_feeder_cycle_last_candle['open'],
            bank=bank_futures_values_data
        )
        record_data_chart_1(db, db_names, charts_1_data)


    return (algo_engine_data, bank_spot_values_data, bank_futures_values_data)


# Usage example:
def handle_algo_engine_command(
        db, db_names,
        json_data, hourly_candles, pair,
        feederCycle=None, fastForwardmultiplier=None
):
    """
    Handle different algorithm engine commands.

    Args:
        ... (same as process_algo_engine)
        feederCycle: Cycle length for allForward command
        fastForwardmultiplier: Multiplier for fastForward command
    """
    if json_data['command'] == 'allForward':
        cycle_range = range(0, feederCycle)
    elif json_data['command'] == 'fastForward':
        cycle_range = range(0, fastForwardmultiplier)
    else:
        cycle_range = None

    return process_algo_engine(db, db_names, json_data, hourly_candles, pair, cycle_range)





