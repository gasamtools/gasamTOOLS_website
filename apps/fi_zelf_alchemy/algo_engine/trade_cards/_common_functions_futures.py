from sqlalchemy import text
from._common_functions import *
from._common_functions_spot import *


def update_bank_balances_futures(db, futures_db, trade): # feeds filled trade

    # DEDUCT FUNDS

    if trade['currency_sell'] == "USDT": #deducting from USDT
        deduct_query = text(f"""
            UPDATE {futures_db}
            SET amount = amount - :deduct_amount,
                pnl = :pnl,
                trade_position = :trade_position
            WHERE currency = :currency
        """)
        db.session.execute(deduct_query, {"currency": trade['currency_sell'], "deduct_amount": trade['amount_sell'], "pnl": 0, "trade_position": None})
    else:
        delete_query = text(f"""
            DELETE FROM {futures_db}
            WHERE currency = :currency
        """)
        db.session.execute(delete_query, {"currency": trade['currency_sell']})

    # ADD FUNDS TO ADD_CURRENCY
    # Check if coin exists
    add_currency_check_query = text(f"""
            SELECT amount
            FROM {futures_db}
            WHERE currency = :currency
        """)
    add_currency_exists = db.session.execute(add_currency_check_query, {"currency": trade['currency_buy']}).scalar()

    if add_currency_exists is None:
        # Insert new BTC record
        add_currency_insert_query = text(f"""
            INSERT INTO {futures_db} (currency, amount, pnl, trade_id, trade_position)
            VALUES (:currency, :amount, :pnl, :trade_id, :trade_position)
        """)
        db.session.execute(add_currency_insert_query,
                           {"currency": trade['currency_buy'],
                            "amount": trade['amount_buy'],
                            "pnl": 0,
                            "trade_id": trade['trade_id'],
                            'trade_position': trade['trade_position']
                            })
    else:
        # Update BTC record
        if trade['currency_buy'] == "USDT":
            trade_id = 0
            trade_position = None
        else:
            trade_id = trade['trade_id']
            trade_position = trade['trade_position']

        add_currency_update_query = text(f"""
            UPDATE {futures_db}
            SET amount = amount + :add_amount,
                pnl = :pnl,
                trade_id = :trade_id,
                trade_position = :trade_position
            WHERE currency = :currency
        """)
        db.session.execute(add_currency_update_query,
                           {"currency": trade['currency_buy'],
                            "add_amount": trade['amount_buy'],
                            "pnl": 0,
                            'trade_id': trade_id,
                            "trade_position": trade_position
                            })

   # Commit the transaction
    db.session.commit()


def fetch_bank_currency_balance_futures(db, futures_db, trade_db, currency, price):
    # CHECK IF CURRENCY EXISTS IN DB
    check_currency_query = text(f"""
        SELECT EXISTS (
            SELECT 1
            FROM {futures_db}
            WHERE currency = :currency
        )
    """)
    currency_exists = db.session.execute(
        check_currency_query,
        {"currency": currency}
    ).scalar()

    # Handle the result
    if currency_exists:
        if currency == 'USDT':
            check_currency_amount_query = text(f"""
                    SELECT amount
                    FROM {futures_db}
                    WHERE currency = :currency
                """)
            original_amount_in = db.session.execute(check_currency_amount_query, {"currency": currency}).scalar()
        else:
            check_trade_id_by_currency_query = text(f"""
                    SELECT trade_id
                    FROM {futures_db}
                    WHERE currency = :currency
                """)
            trade_id = db.session.execute(check_trade_id_by_currency_query, {"currency": currency}).scalar()
            original_amount_in = get_original_buy_in_parameter_of_position_futures(db, trade_db, trade_id, 'amount_sell')

        check_currency_amount_query = text(f"""
                    SELECT pnl
                    FROM {futures_db}
                    WHERE currency = :currency
                """)
        pnl = db.session.execute(check_currency_amount_query, {"currency": currency}).scalar()
        # print(f'currency {currency} | (original_amount_in + pnl) / price | ({original_amount_in} + {pnl}) / {price}')

        if original_amount_in is None or pnl is None:
            return 0
        else:
            if currency == 'USDT':
                return original_amount_in
            else:
                return (original_amount_in + pnl) / price
    else:
        return 0


def place_new_order_futures(
        db=None,
        signal_db=None,
        trade_db=None,
        futures_db=None,
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
    # if not bank_futures_has_enough_funds(db, futures_db, currency_sell, amount_in, price):
    #     return {
    #         'to_postman': 'Cannot place trade order - not enough funds!',
    #         'to_crystal': '<p>Cannot place trade order - not enough funds!</p>'
    #     }

    try:
        # FIND AMOUNT OUT
        if trade_action == 'buy':
            amount_out = amount_in / price
        elif trade_action == 'sell':
            # GET CURRENT PNL
            query = text(f"""
                            SELECT pnl 
                            FROM {futures_db}
                            WHERE trade_id = :trade_id
                        """)
            pnl_amount = db.session.execute(query, {"trade_id": trade_id}).scalar()

            # GET ORIGINAL AMOUNT IN FOR THIS CONTRACT
            original_amount_in = get_original_buy_in_parameter_of_position_futures(db, trade_db, trade_id,'amount_sell' )

            # CALCULATE TOTAL AMOUNT OUT
            amount_out = float(original_amount_in) + float(pnl_amount)

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
                # First, check if the pair exists
                existing_association = db.session.execute(
                    text(f"""
                    SELECT 1 FROM {signal_trade_db} 
                    WHERE signal_id = :signal_id AND trade_id = :trade_id
                    """),
                    {"signal_id": signal['id'], "trade_id": trade_id}
                ).fetchone()

                # If the pair doesn't exist, insert
                if not existing_association:
                    try:
                        association_query = text(f"""
                            INSERT INTO {signal_trade_db} (signal_id, trade_id)
                            VALUES (:signal_id, :trade_id)
                        """)
                        db.session.execute(association_query, {"signal_id": signal['id'], "trade_id": trade_id})
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        print(str(e))

            note_time = timestamp_to_time_UTC(fz_feeder_cycle_last_candle['time'])
            to_postman += (
                f'{note_time} TRADE: id#{record_id} NEW {trade_type} {trade_position} {trade_entry} {trade_action} ORDER PLACED! '
                f'{amount_out} {currency_buy} with {amount_in} of {currency_sell} for {price}')

            to_crystal += (
                f'<p>{note_time} TRADE: id#{record_id} NEW {trade_type} {trade_position} {trade_entry} {trade_action} ORDER #{record_id} PLACED! '
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


def place_sl_order_futures(
        db=None,
        signal_db=None,
        trade_db=None,
        futures_db=None,
        signal_trade_db=None,
        trade_id=None,
        signal=None,
        price=None,
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

# CALCULATE AMOUNT IN AND AMOUNT OUT
    try:
        # GET ORIGINAL AMOUNT_IN and PRICE FOR THIS CONTRACT
        original_amount_in = get_original_buy_in_parameter_of_position_futures(db, trade_db, trade_id, 'amount_sell')
        original_amount_out = get_original_buy_in_parameter_of_position_futures(db, trade_db, trade_id, 'amount_buy')
        original_price_in = get_original_buy_in_parameter_of_position_futures(db, trade_db, trade_id, 'price')
        projected_value_usdt = float(original_amount_out) * float(price)

        # print(f'projected_price {price} | original_amount_in {original_amount_in} | original_price_in {original_price_in}')

        if trade_position == 'short':
            projected_pnl_amount = float(original_amount_in) - projected_value_usdt
        elif trade_position == 'long':
            projected_pnl_amount = projected_value_usdt - float(original_amount_in)

        # CALCULATE TOTAL AMOUNT OUT
        amount_out = float(original_amount_in) + float(projected_pnl_amount)
        amount_in = amount_out / float(price)

        # print(f'amount_in {amount_in} | amount_out {amount_out}')


        # #PREPARE TRADE DATA
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

            note_time = timestamp_to_time_UTC(fz_feeder_cycle_last_candle['time'])
            to_postman += (
                f'{note_time} TRADE: id#{record_id} NEW {trade_type} {trade_position} {trade_entry} {trade_action} ORDER PLACED! '
                f'{amount_out} {currency_buy} with {amount_in} of {currency_sell} for {price}')

            to_crystal += (
                f'<p>{note_time} TRADE: id#{record_id} NEW {trade_type} {trade_position} {trade_entry} {trade_action} ORDER #{record_id} PLACED! '
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


def place_stop_lossProfit_futures(db, signal_db, trade_db, futures_db, signal_trade_db, base_price, data, percent, type):
    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''

# CALCULATE STOP-LIMIT PRICE
    if (data['trade_position'] == 'short' and type == 'loss') or (data['trade_position'] == 'long' and type == 'profit'):
        stop_price = add_n_percent(base_price, percent)
    elif (data['trade_position'] == 'short' and type == 'profit') or (data['trade_position'] == 'long' and type == 'loss'):
        stop_price = subtract_n_percent(base_price, percent)


    place_SL_order_data = place_sl_order_futures(db=db,
                                                   signal_db=signal_db,
                                                   trade_db=trade_db,
                                                   futures_db=futures_db,
                                                   signal_trade_db=signal_trade_db,
                                                   trade_id=data['trade_id'],
                                                   signal='',
                                                   price=stop_price,
                                                   trade_entry_stop=stop_price,
                                                   trade_type='futures',
                                                   trade_position=data['trade_position'],
                                                   trade_action='sell',
                                                   trade_entry='stop-limit',
                                                   currency_buy=data['currency_sell'],
                                                   currency_sell=data['currency_buy'],
                                                   tdp_0=fz_feeder_cycle_last_candle['time'])
    to_postman += place_SL_order_data['to_postman']
    to_crystal += place_SL_order_data['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


def place_futures_order(db, signal_db, trade_db, futures_db, signal_trade_db, pair, signal, price, trade_position, trade_action, trade_entry):
    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''

    if trade_action == 'buy':
        currency_buy = pair.split('-')[0]
        currency_sell = pair.split('-')[1]
    if trade_action == 'sell':
        currency_buy = pair.split('-')[1]
        currency_sell = pair.split('-')[0]

    # CHECK IF SIGNAL ALREADY HAS TRADES TO GET trade_id. IF IT DOESN'T CREATE NEW ONE
    trade_ids_of_signal = get_trade_ids_by_signal(db, signal_trade_db, signal['id'])
    if not trade_ids_of_signal:
        new_trade_id = get_new_trade_id(db, trade_db)
    else:
        new_trade_id = trade_ids_of_signal[0]
    # print(f'place_futures_order new_trade_id {new_trade_id} | trade_ids_of_signal {trade_ids_of_signal} | fz_feeder_cycle_last_candle[time] {fz_feeder_cycle_last_candle['time']}')

    # CHECK AVAILABLE FUNDS
    currency_sell_balance = fetch_bank_currency_balance_futures(db, futures_db, trade_db, currency_sell, price)
    if currency_sell_balance > 0:
        place_new_order_data = place_new_order_futures(db=db,
                                                        signal_db=signal_db,
                                                        trade_db=trade_db,
                                                        futures_db=futures_db,
                                                        signal_trade_db=signal_trade_db,
                                                        trade_id=new_trade_id,
                                                        signal=signal,
                                                        price=price,
                                                        amount_in=currency_sell_balance,
                                                        trade_type='futures',
                                                        trade_position=trade_position,
                                                        trade_action=trade_action,
                                                        trade_entry=trade_entry,
                                                        currency_buy=currency_buy,
                                                        currency_sell=currency_sell,
                                                        tdp_0=fz_feeder_cycle_last_candle['time'])
        to_postman += place_new_order_data['to_postman']
        to_crystal += place_new_order_data['to_crystal']
    else:
        to_postman += 'No active contract.'
        to_crystal += '<p>No active contract.</p>'

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


def get_original_buy_in_parameter_of_position_futures(db, trade_db, trade_id, parameter):
    query = text(f"""
            SELECT * 
            FROM {trade_db}
            WHERE trade_id = :trade_id
        """)
    existing_trades_with_this_id = db.session.execute(query, {"trade_id": trade_id}).mappings().fetchall()
    filled_buy_trades_with_this_id = [trade for trade in existing_trades_with_this_id if
                                      trade['trade_status'] == 'filled' and trade['trade_action'] == 'buy' and trade[
                                          'trade_type'] == 'futures']

    if filled_buy_trades_with_this_id:
        original_amount_in = filled_buy_trades_with_this_id[0][parameter]
    else:
        original_amount_in = 0
        print(f'get_original_buy_in_parameter_of_position_futures trade_id {trade_id} | parameter {parameter} | existing_trades_with_this_id {existing_trades_with_this_id}')
        print('something is weird with get_original_buy_in_parameter_of_position_futures function in _common_functions')
    return original_amount_in

