from sqlalchemy import text


def fetch_flagged_signals(db, signal_db, pair):
    check_query = text(f"SELECT * FROM {signal_db} WHERE is_flagged = :is_flagged AND trading_pair = :trading_pair")
    flagged_signals = db.session.execute(check_query, {"is_flagged": True, "trading_pair": pair}).mappings().fetchall()
    return flagged_signals


def fetch_flagged_trades(db, trade_db, pair):
    # SQL query to fetch flagged trades with specific currencies
    currencies = pair.split('-')

    check_query = text(f"""
        SELECT * 
        FROM {trade_db} 
        WHERE 
            is_flagged = :is_flagged 
            AND currency_buy IN ('{currencies[0]}', '{currencies[1]}') 
            AND currency_sell IN ('{currencies[0]}', '{currencies[1]}') 
    """)

    # Execute the query
    flagged_trades = db.session.execute(check_query, {"is_flagged": True}).mappings().fetchall()

    return flagged_trades


def fetch_stoplimit_trades(db, trade_db, pair):
    currencies = pair.split('-')
    check_query = text(f"""
        SELECT * 
        FROM {trade_db} 
        WHERE 
            trade_entry = :trade_entry 
            AND is_active = :is_active
            AND currency_buy IN ('{currencies[0]}', '{currencies[1]}') 
            AND currency_sell IN ('{currencies[0]}', '{currencies[1]}') 
    """)
    stoplimit_trades = db.session.execute(check_query,
                                          {"trade_entry": 'stop-limit', "is_active": True}).mappings().fetchall()
    return stoplimit_trades


def unflag_and_deactivate_signals(db, signal_db, pair, flagged_signals):
    to_postman, to_crystal = '', ''
    if len(flagged_signals) > 0:
        update_query = text(
            f"UPDATE {signal_db} SET is_active = :is_active, is_flagged = :new_is_flagged WHERE is_flagged = :current_is_flagged AND trading_pair = :trading_pair"
        )
        result = db.session.execute(update_query, {
            "is_active": False,
            "new_is_flagged": None,
            "current_is_flagged": True,
            "trading_pair": pair
        })
        rows_affected = result.rowcount
        db.session.commit()

    #     to_postman += f"vault_take_trade | Found {len(flagged_signals)} flagged signals and updated {rows_affected} rows"
    #     to_crystal += f"<p>vault_take_trade | Found {len(flagged_signals)} flagged signals and updated {rows_affected} rows</p>"
    # else:
    #     to_postman += "vault_take_trade | No flagged signals found"
    #     to_crystal += "<p>vault_take_trade | No flagged signals found</p>"

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


def unflag_and_deactivate_trade(db, trade_db, flagged_trade):
    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''
    if flagged_trade and flagged_trade['is_active']:
        update_query = text(
            f"UPDATE {trade_db} SET is_active = :is_active, is_flagged = :new_is_flagged WHERE id = :id"
        )
        result = db.session.execute(update_query, {
            "is_active": False,
            "new_is_flagged": None,
            "id": flagged_trade['id']
        })

        db.session.commit()

        note_time = timestamp_to_time_UTC(fz_feeder_cycle_last_candle['time'])
        to_postman += (
            f"{note_time} TRADE: id#{flagged_trade['id']} Flagged {flagged_trade['trade_status']} Trade @{flagged_trade['price']}"
            f" | {flagged_trade['currency_buy']}-{flagged_trade['currency_sell']} is deactivated. ")
        to_crystal += (
            f"<p>{note_time} TRADE: id#{flagged_trade['id']} Flagged {flagged_trade['trade_status']} Trade @{flagged_trade['price']}"
            f" | {flagged_trade['currency_buy']}-{flagged_trade['currency_sell']} is deactivated</p>")
    # else:
    #     to_postman += "vault_take_trade | No flagged trades found"
    #     to_crystal += "<p>vault_take_trade | No flagged trades found</p>"

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


def fetch_not_traded_signals(db, signal_db, signal_trade_db, pair):
    check_query = text(f"""
        SELECT s.*
        FROM {signal_db} s
        WHERE 
            s.is_active = :is_active 
            AND (s.is_flagged != :is_flagged OR s.is_flagged IS NULL)
            AND s.trading_pair = :trading_pair
            AND NOT EXISTS (
                SELECT 1 
                FROM {signal_trade_db} a
                WHERE a.signal_id = s.id
            )
    """)

    query_params = {
        "is_active": True,
        "is_flagged": True,
        "trading_pair": pair
    }
    not_traded_signals = db.session.execute(check_query, query_params).mappings().fetchall()

    if not not_traded_signals:
        not_traded_signals = []

    return not_traded_signals


def get_new_trade_id(db, trade_db):
    max_trade_id_query = text(f"SELECT MAX(trade_id) FROM {trade_db}")
    max_trade_id = db.session.execute(max_trade_id_query).scalar()
    new_trade_id = 1 if max_trade_id is None else max_trade_id + 1
    return new_trade_id


def fetch_active_placed_trades_from_trade_db(db, trade_db):
    from sqlalchemy import text

    # Define the query to fetch active trades
    query = text(f"SELECT * FROM {trade_db} WHERE is_active = :is_active")

    # Define the parameter
    query_params = {"is_active": True}

    # Execute the query
    active_trades = db.session.execute(query, query_params).mappings().fetchall()
    placed_active_trades = [trade for trade in active_trades if trade['trade_status'] == 'placed']

    return placed_active_trades


def update_trade_in_trade_db(
        db=None,
        trade_db=None,
        record_id=None,
        update_data=None):
    from sqlalchemy import text
    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''

    formatted_list = [f"{key} = :{key}" for key in update_data]
    formatted_string = ', '.join(formatted_list)

    try:
        # Define the query to update the trade
        update_query = text(f"""
            UPDATE {trade_db}
            SET {formatted_string}
            WHERE id = :id
        """)

        # Define the parameters for the query
        query_params = update_data | {"id": record_id}

        db.session.execute(update_query, query_params)
        db.session.commit()

        note_time = timestamp_to_time_UTC(fz_feeder_cycle_last_candle['time'])
        to_postman += f'{note_time} TRADE: id#{record_id} UPDATED: {update_data} '
        to_crystal += f'{note_time} <p>TRADE: id#{record_id} UPDATED: {update_data} </p>'
    except ValueError as e:
        print(str(e))

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


def update_bank_balances_and_trade_db(db, bank_db, futures_db, trade_db, trade):
    from ._common_functions_spot import update_bank_balances_spot
    from ._common_functions_futures import update_bank_balances_futures

    to_postman, to_crystal = '', ''

    # print(trade)
    # UPDATE BANK RECORDS
    if trade['trade_type'] == 'spot':
        try:
            update_bank_balances_spot(db=db, bank_db=bank_db, deduct_currency=trade['currency_sell'],
                                      deduct_amount=trade['amount_sell'], add_currency=trade['currency_buy'],
                                      add_amount=trade['amount_buy'])
            # print("Bank balances updated successfully.")
        except ValueError as e:
            print(str(e))
    elif trade['trade_type'] == 'futures':
        try:
            update_bank_balances_futures(db=db, futures_db=futures_db, trade=trade)

        except ValueError as e:
            print(str(e))

    popped_id = trade.pop('id', None)
    update_trade_in_trade_db_data = update_trade_in_trade_db(db=db, trade_db=trade_db, record_id=popped_id,
                                                             update_data=trade)
    to_postman += update_trade_in_trade_db_data['to_postman']
    to_crystal += update_trade_in_trade_db_data['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


def is_difference_at_least_n_percent(a, b, n):
    difference_percentage = abs(a - b) / min(a, b) * 100
    return difference_percentage >= n


def subtract_n_percent(value, n):
    return value - (value * (n / 100))


def add_n_percent(value, n):
    return value + (value * (n / 100))


def timestamp_to_time_UTC(timestamp):
    import pytz
    from datetime import datetime
    utc_timezone = pytz.UTC
    dt_utc = datetime.fromtimestamp(int(timestamp), utc_timezone)
    formatted_time = f"{dt_utc.strftime('%y-%m-%d %H')}:00 UTC"
    return formatted_time


def get_trade_ids_by_signal(db, signal_trade_db, signal_id):
    # Query to fetch trade IDs connected to the given signal ID
    query = text(f"""
        SELECT trade_id
        FROM {signal_trade_db}
        WHERE signal_id = :signal_id
    """)

    # Execute the query
    result = db.session.execute(query, {"signal_id": signal_id}).fetchall()

    # Extract trade IDs from the result
    trade_ids = [row[0] for row in result]

    # Commit the session to ensure consistency (optional)
    db.session.commit()

    return trade_ids


def get_trades_by_trade_id(db, trade_db, trade_ids):
    trades = []
    for trade_id in trade_ids:
        query = text(f"""
            SELECT *
            FROM {trade_db}
            WHERE trade_id = :trade_id
        """)

        # Execute the query
        result = db.session.execute(query, {"trade_id": trade_id}).mappings().fetchall()

        # Extract trade IDs from the result
        trades += [row for row in result]

        # Commit the session to ensure consistency (optional)
    db.session.commit()

    return trades


def get_trades_by_signal(db, signal_trade_db, trade_db, signal_id):
    trade_ids = get_trade_ids_by_signal(db, signal_trade_db, signal_id)
    trades_of_signal = get_trades_by_trade_id(db, trade_db, trade_ids)
    return trades_of_signal


def move_stoplimit_up_n_percent(db, trade_db, data, trigger_n, n):
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''

    if is_difference_at_least_n_percent(fz_feeder_cycle_last_candle['close'],
                                        data['trade_entry_stop'], trigger_n):
        update_data = {
            'trade_entry_stop': add_n_percent(data['trade_entry_stop'], n),
            'price': add_n_percent(data['price'], n),
            'amount_buy': data['amount_sell'] * add_n_percent(data['price'], n),
            'tdp_0': fz_feeder_cycle_last_candle['time']
        }

        update_trade_in_trade_db_data = update_trade_in_trade_db(
            db=db,
            trade_db=trade_db,
            record_id=data['id'],
            update_data=update_data)
        to_postman += update_trade_in_trade_db_data['to_postman']
        to_crystal += update_trade_in_trade_db_data['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }
