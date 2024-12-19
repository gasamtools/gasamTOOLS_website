from sqlalchemy import text
from._common_functions import *
from._common_functions_futures import *


def bank_spot_has_enough_funds(db, bank_db, currency, required_amount):
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


def update_bank_balances_spot(db, bank_db, deduct_currency, deduct_amount, add_currency, add_amount):
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


def fetch_bank_currency_balance_spot(db, bank_db, currency):
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


def place_new_order_spot(
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
    if not bank_spot_has_enough_funds(db, bank_db, currency_sell, amount_in):
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


def place_stop_loss_spot(db, signal_db, trade_db, bank_db, signal_trade_db, base_price, data, percent):
    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''

    # Subtract % of the value
    stop_price = subtract_n_percent(base_price, percent)

    # check available funds and place 100% for stop loss
    currency_sell_balance = fetch_bank_currency_balance_spot(db, bank_db, data['currency_buy'])

    place_stop_loss_order_data = place_new_order_spot(db=db, signal_db=signal_db, trade_db=trade_db, bank_db=bank_db,
                                                      signal_trade_db=signal_trade_db, trade_id=data['trade_id'],
                                                      signal='', price=stop_price, amount_in=currency_sell_balance,
                                                      trade_type='spot', trade_position='long', trade_action='sell',
                                                      trade_entry='stop-limit', trade_entry_stop=stop_price,
                                                      currency_buy=data['currency_sell'],
                                                      currency_sell=data['currency_buy'],
                                                      tdp_0=fz_feeder_cycle_last_candle['time'])

    return {
        'to_postman': place_stop_loss_order_data['to_postman'],
        'to_crystal': place_stop_loss_order_data['to_crystal']
    }


def place_buy_stop_limit(db, signal_db, trade_db, bank_db, signal_trade_db, base_price, data, percent):
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''

    # add % to the value
    stop_price = add_n_percent(base_price, percent)

    # check available funds and place 100% for stop loss
    currency_buy_balance = fetch_bank_currency_balance_spot(db, bank_db, data['currency_buy'])

    place_stop_loss_order_data = place_new_order_spot(db=db, signal_db=signal_db, trade_db=trade_db, bank_db=bank_db,
                                                      signal_trade_db=signal_trade_db, trade_id=data['trade_id'],
                                                      signal='', price=stop_price, amount_in=currency_buy_balance,
                                                      trade_type='spot', trade_position='long', trade_action='buy',
                                                      trade_entry='stop-limit', trade_entry_stop=stop_price,
                                                      currency_buy=data['currency_sell'],
                                                      currency_sell=data['currency_buy'],
                                                      tdp_0=fz_feeder_cycle_last_candle['time'])

    return {
        'to_postman': place_stop_loss_order_data['to_postman'],
        'to_crystal': place_stop_loss_order_data['to_crystal']
    }
