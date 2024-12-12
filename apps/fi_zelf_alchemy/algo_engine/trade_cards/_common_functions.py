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


def bank_has_enough_funds(db, bank_db, currency, required_amount):
    query = text(f"""
        SELECT amount 
        FROM {bank_db}
        WHERE currency = :currency
    """)
    result = db.session.execute(query, {"currency": currency}).scalar()

    # Check if the result exists and is greater than or equal to the required amount
    if result is None:
        return False  # No record for USDT
    return result >= required_amount


def update_bank_balances(db, bank_db, deduct_currency, deduct_amount, add_currency, add_amount):
    # Deduct from USDT
    deduct_query = text(f"""
        UPDATE {bank_db}
        SET amount = amount - :deduct_amount
        WHERE currency = :currency AND amount >= :deduct_amount
    """)
    deduct_result = db.session.execute(deduct_query, {"currency": deduct_currency, "deduct_amount": deduct_amount})

    # Check if deduction succeeded
    if deduct_result.rowcount == 0:
        raise ValueError(f"Insufficient {deduct_currency} funds or {deduct_currency} does not exist.")

    # Check if BTC exists
    add_currency_check_query = text(f"""
        SELECT amount
        FROM {bank_db}
        WHERE currency = :currency
    """)
    add_currency_exists = db.session.execute(add_currency_check_query, {"currency": add_currency}).scalar()

    if add_currency_exists is None:
        # Insert new BTC record
        add_currency_insert_query = text(f"""
            INSERT INTO {bank_db} (currency, amount)
            VALUES (:currency, :amount)
        """)
        db.session.execute(add_currency_insert_query, {"currency": add_currency, "amount": add_amount})
    else:
        # Update BTC record
        add_currency_update_query = text(f"""
            UPDATE {bank_db}
            SET amount = amount + :add_amount
            WHERE currency = :currency
        """)
        db.session.execute(add_currency_update_query, {"currency": add_currency, "add_amount": add_amount})

    # Commit the transaction
    db.session.commit()


def fetch_bank_currency_balance(db, bank_db, currency):
    check_currency_amount_query = text(f"""
            SELECT amount
            FROM {bank_db}
            WHERE currency = :currency
        """)
    check_currency_amount = db.session.execute(check_currency_amount_query, {"currency": currency}).fetchone()

    if check_currency_amount is None:
        return 0
    else:
        return check_currency_amount[0]


def place_new_order(
        db=None,
        signal_db=None,
        trade_db=None,
        bank_db=None,
        signal_trade_db=None,
        trade_id=None,
        signal=None,
        price=None,
        amount_in=None,
        trade_type=None,  #spot, futures
        trade_position=None,  #long/short
        trade_action=None,  #buy/sell
        trade_entry=None,  # limit, market, stop limit
        trade_entry_stop=None,  # stoploss trigger price
        currency_buy=None,
        currency_sell=None,
        tdp_0=None
):
    from datetime import datetime
    from ...fz_fetcher import fz_fetcher_send_placed_order
    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''

    # CHECK IF BANK HAS ENOUGH FUNDS
    if not bank_has_enough_funds(db, bank_db, currency_sell, amount_in):
        return {
            'to_postman': 'Cannot place trade order - not enough funds!',
            'to_crystal': '<p>Cannot place trade order - not enough funds!</p>'
        }

    try:
        # FIND AMOUNT OUT
        if trade_action == 'buy':
            amount_out = amount_in / price
        elif trade_action == 'sell':
            amount_out = amount_in * price

        #PREPARE TRADE DATA
        trade_data = {
            "trade_id": trade_id,
            "is_active": True,
            "trade_type": trade_type,
            "trade_position": trade_position,
            "trade_action": trade_action,
            "trade_entry": trade_entry,
            "trade_entry_stop": trade_entry_stop,
            "trade_status": "placed",
            "date_placed": int(datetime.now().timestamp()),
            "currency_buy": currency_buy,
            "currency_sell": currency_sell,
            "amount_buy": amount_out,
            "amount_sell": amount_in,
            "price": price,
            'tdp_0': tdp_0
        }

        # SEND placed order REQUEST TO EXCHANGE / return True/False
        if fz_fetcher_send_placed_order(trade_data):

            # INSERT TRADE RECORD
            trade_query = text(f"""
                    INSERT INTO {trade_db} (
                        trade_id, is_active, trade_type, trade_position, trade_action, 
                        trade_entry, trade_entry_stop, trade_status, date_placed,
                        currency_buy, currency_sell, amount_buy, amount_sell, price, tdp_0
                    ) VALUES (
                        :trade_id, :is_active, :trade_type, :trade_position, :trade_action,
                        :trade_entry, :trade_entry_stop, :trade_status, :date_placed,
                        :currency_buy, :currency_sell, :amount_buy, :amount_sell, :price, :tdp_0
                    ) RETURNING trade_id, id
                """)
            trade_result = db.session.execute(trade_query, trade_data).fetchone()
            trade_id = trade_result[0]
            record_id = trade_result[1]

            # TIE TRADE TO SIGNAL
            if 'id' in signal:
                try:
                    association_query = text(f"""
                            INSERT INTO {signal_trade_db} (signal_id, trade_id)
                            VALUES (:signal_id, :trade_id)
                        """)
                    db.session.execute(association_query, {"signal_id": signal['id'], "trade_id": trade_id})
                    db.session.commit()

                except Exception as e:
                    print(str(e))

            note_time = timestamp_to_time_UTC(fz_feeder_cycle_last_candle['time'])
            to_postman += (
                f'{note_time} TRADE: id#{record_id} NEW {trade_type} {trade_entry} {trade_action} ORDER PLACED! '
                f'{amount_out} {currency_buy} with {amount_in} of {currency_sell} for {price}')

            to_crystal += (
                f'<p>{note_time} TRADE: id#{record_id} NEW {trade_type} {trade_entry} {trade_action} ORDER #{record_id} PLACED! '
                f'{amount_out} {currency_buy} with {amount_in} of {currency_sell} for {price}</p>')


        else:
            print(f"Error sending data to exchange via fz_fetcher_send_placed_order")

    except Exception as e:
        db.session.rollback()  # Rollback if there is any error
        print(f"Error inserting into DB: {e}")

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


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


def update_bank_balances_and_trade_db(db, bank_db, trade_db, trade):
    to_postman, to_crystal = '', ''
    # UPDATE BANK RECORDS
    try:
        update_bank_balances(
            db=db,
            bank_db=bank_db,
            deduct_currency=trade['currency_sell'],
            deduct_amount=trade['amount_sell'],
            add_currency=trade['currency_buy'],
            add_amount=trade['amount_buy']
        )
        # print("Bank balances updated successfully.")
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


def place_stop_loss(db, signal_db, trade_db, bank_db, signal_trade_db, base_price, data, percent):
    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''

    # Subtract % of the value
    stop_price = subtract_n_percent(base_price, percent)

    # check available funds and place 100% for stop loss
    currency_sell_balance = fetch_bank_currency_balance(db, bank_db, data['currency_buy'])

    place_stop_loss_order_data = place_new_order(
        db=db,
        signal_db=signal_db,
        trade_db=trade_db,
        bank_db=bank_db,
        signal_trade_db=signal_trade_db,
        trade_id=data['trade_id'],
        signal='',
        price=stop_price,
        amount_in=currency_sell_balance,
        trade_type='spot',  # spot, futures
        trade_position='long',  # long/short
        trade_action='sell',  # buy/sell
        trade_entry='stop-limit',
        trade_entry_stop=stop_price,
        currency_buy=data['currency_sell'],
        currency_sell=data['currency_buy'],
        tdp_0=fz_feeder_cycle_last_candle['time']
    )

    return {
        'to_postman': place_stop_loss_order_data['to_postman'],
        'to_crystal': place_stop_loss_order_data['to_crystal']
    }


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


def place_buy_stop_limit(db, signal_db, trade_db, bank_db, signal_trade_db, base_price, data, percent):
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''

    # add % to the value
    stop_price = add_n_percent(base_price, percent)

    # check available funds and place 100% for stop loss
    currency_buy_balance = fetch_bank_currency_balance(db, bank_db, data['currency_buy'])

    place_stop_loss_order_data = place_new_order(
        db=db,
        signal_db=signal_db,
        trade_db=trade_db,
        bank_db=bank_db,
        signal_trade_db=signal_trade_db,
        trade_id=data['trade_id'],
        signal='',
        price=stop_price,
        amount_in=currency_buy_balance,
        trade_type='spot',  # spot, futures
        trade_position='long',  # long/short
        trade_action='buy',  # buy/sell
        trade_entry='stop-limit',
        trade_entry_stop=stop_price,
        currency_buy=data['currency_sell'],
        currency_sell=data['currency_buy'],
        tdp_0=fz_feeder_cycle_last_candle['time']
    )

    return {
        'to_postman': place_stop_loss_order_data['to_postman'],
        'to_crystal': place_stop_loss_order_data['to_crystal']
    }

