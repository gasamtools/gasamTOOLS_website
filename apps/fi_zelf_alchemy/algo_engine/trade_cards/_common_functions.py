from sqlalchemy import text


def fetch_flagged_signals(db, signal_db, pair):
    check_query = text(f"SELECT * FROM {signal_db} WHERE is_flagged = :is_flagged AND trading_pair = :trading_pair")
    flagged_signals = db.session.execute(check_query, {"is_flagged": True, "trading_pair": pair}).mappings().fetchall()
    return flagged_signals


def fetch_flagged_trades(db, trade_db):
    check_query = text(f"SELECT * FROM {trade_db} WHERE is_flagged = :is_flagged")
    flagged_trades = db.session.execute(check_query, {"is_flagged": True}).mappings().fetchall()
    return flagged_trades

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

        to_postman += f"vault_take_trade | Found {len(flagged_signals)} flagged signals and updated {rows_affected} rows"
        to_crystal += f"<p>vault_take_trade | Found {len(flagged_signals)} flagged signals and updated {rows_affected} rows</p>"
    else:
        to_postman += "vault_take_trade | No flagged signals found"
        to_crystal += "<p>vault_take_trade | No flagged signals found</p>"

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


def unflag_and_deactivate_trade(db, trade_db, flagged_trade):
    to_postman, to_crystal = '', ''
    if flagged_trade:
        update_query = text(
            f"UPDATE {trade_db} SET is_active = :is_active, is_flagged = :new_is_flagged WHERE is_flagged = :current_is_flagged AND id = :id"
        )
        result = db.session.execute(update_query, {
            "is_active": False,
            "new_is_flagged": None,
            "current_is_flagged": True,
            "id": flagged_trade['id']
        })

        db.session.commit()

        to_postman += (f"vault_take_trade | Flagged {flagged_trade['trade_status']} Trade @{flagged_trade['price']}"
                       f" #{flagged_trade['id']} | {flagged_trade['currency_buy']}-{flagged_trade['currency_sell']} is deactivated. ")
        to_crystal += (f"<p>vault_take_trade | Flagged {flagged_trade['trade_status']} Trade @{flagged_trade['price']}"
                       f" #{flagged_trade['id']} | {flagged_trade['currency_buy']}-{flagged_trade['currency_sell']} is deactivated</p>")
    else:
        to_postman += "vault_take_trade | No flagged trades found"
        to_crystal += "<p>vault_take_trade | No flagged trades found</p>"

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
        signal=None,
        price=None,
        amount_in=None,
        trade_type=None, #spot, futures
        trade_position=None, #long/short
        trade_action=None, #buy/sell
        currency_buy=None,
        currency_sell=None
):
    from datetime import datetime
    from ...fz_fetcher import fz_fetcher_send_placed_order
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

        # ESTABLISH TRADE ID
        new_trade_id = get_new_trade_id(db, trade_db)

        #PREPARE TRADE DATA
        trade_data = {
            "trade_id": new_trade_id,
            "is_active": True,
            "trade_type": trade_type,
            "trade_position": trade_position,
            "trade_action": trade_action,
            "trade_status": "placed",
            "date_placed": int(datetime.now().timestamp()),
            "currency_buy": currency_buy,
            "currency_sell": currency_sell,
            "amount_buy": amount_out,
            "amount_sell": amount_in,
            "price": price
        }

        # SEND placed order REQUEST TO EXCHANGE / return True/False
        if fz_fetcher_send_placed_order(trade_data):

            # INSERT TRADE RECORD
            trade_query = text(f"""
                    INSERT INTO {trade_db} (
                        trade_id, is_active, trade_type, trade_position, trade_action, 
                        trade_status, date_placed,
                        currency_buy, currency_sell, amount_buy, amount_sell, price
                    ) VALUES (
                        :trade_id, :is_active, :trade_type, :trade_position, :trade_action,
                        :trade_status, :date_placed,
                        :currency_buy, :currency_sell, :amount_buy, :amount_sell, :price
                    ) RETURNING trade_id
                """)
            trade_result = db.session.execute(trade_query, trade_data).fetchone()
            trade_id = trade_result[0]

            # TIE TRADE TO SIGNAL
            association_query = text(f"""
                    INSERT INTO {signal_trade_db} (signal_id, trade_id)
                    VALUES (:signal_id, :trade_id)
                """)
            db.session.execute(association_query, {"signal_id": signal['id'], "trade_id": trade_id})
            db.session.commit()

            to_postman += (f'TRADE: NEW {trade_type} ORDER PLACED! '
                           f'{amount_out} {currency_buy} with {amount_in} of {currency_sell} for {price}')

            to_crystal += (f'<p>TRADE: NEW {trade_type} ORDER PLACED! '
                           f'{amount_out} {currency_buy} with {amount_in} of {currency_sell} for {price}</p>')

            # UPDATE BANK RECORDS
            try:
                update_bank_balances(
                    db=db,
                    bank_db=bank_db,
                    deduct_currency=currency_sell,
                    deduct_amount=amount_in,
                    add_currency=currency_buy,
                    add_amount=amount_out
                )
                print("Bank balances updated successfully.")
            except ValueError as e:
                print(str(e))
        else:
            print(f"Error sending data to exchange via fz_fetcher_send_placed_order")

    except Exception as e:
        db.session.rollback()  # Rollback if there is any error
        print(f"Error inserting into DB: {e}")

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


def fetch_active_trades_from_trade_db(db, trade_db):
    from sqlalchemy import text

    # Define the query to fetch active trades
    query = text(f"SELECT * FROM {trade_db} WHERE is_active = :is_active")

    # Define the parameter
    query_params = {"is_active": True}

    # Execute the query
    active_trades = db.session.execute(query, query_params).mappings().fetchall()

    # Print the result
    # for trade in active_trades:
    #     print(trade)

    return active_trades


def update_trade_in_trade_db(
        db=None,
        trade_db=None,
        record_id=None,
        update_data=None):

    from sqlalchemy import text
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

        to_postman += f'Trade #{record_id} is updated. '
        to_crystal += f'<p>Trade #{record_id} is updated. </p>'
    except ValueError as e:
        print(str(e))

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


