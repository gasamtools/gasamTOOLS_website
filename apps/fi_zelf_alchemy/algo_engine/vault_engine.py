fund_bank_ini_usdt_value = 1000
fund_futures_ini_usdt_value = 1000
vault_id = '0000'
def vault_engine(db, db_names, action, pair):
    if action == 'adjust_trades':
        return vault_adjust_trades(db, db_names, pair)
    if action == 'take_trades':
        return vault_take_trades(db, db_names, pair)

def  vault_adjust_trades(db, db_names, pair):
    from .trade_cards._common_functions import fetch_active_placed_trades_from_trade_db, update_bank_balances_and_trade_db, update_signal_trade_level
    from ..fz_fetcher import fz_fetcher_update_orders
    global vault_id

    to_postman, to_crystal = '', ''

    # FETCH active placed orders DATA FROM db
    placed_active_trades = fetch_active_placed_trades_from_trade_db(db, db_names['trade_db'])

    # FETCH flagged_trades DATA FROM KUCOIN - FLAGGED BECAUSE FILLED
    flagged_filled_trades = fz_fetcher_update_orders(db, db_names['bank_db'], placed_active_trades)

    # UPDATE BANK and TRADE_DB AND NOTE CHANGES
    for trade in flagged_filled_trades:
        update_bank_balances_and_trade_db_data = update_bank_balances_and_trade_db(db, db_names['bank_db'], db_names['futures_db'], db_names['trade_db'], trade)
        to_postman += update_bank_balances_and_trade_db_data['to_postman']
        to_crystal += update_bank_balances_and_trade_db_data['to_crystal']

        #  UPDATE SIGNAL is_traded parameter
        update_signal_is_traded_data = update_signal_trade_level(db, db_names['signal_trade_db'], db_names['signal_db'],
                                                                 trade)
        to_postman += update_signal_is_traded_data['to_postman']
        to_crystal += update_signal_is_traded_data['to_crystal']

    # 4 card_sma50_day_spot_sl2prcnt
    # from .trade_cards.card_sma50_day_spot_sl2prcnt import card_sma50_day_spot_sl2prcnt
    # card_data = card_sma50_day_spot_sl2prcnt(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'adjust_trades')

    # 5 card_sma50_day_spot_sl3prcnt
    # from .trade_cards.card_sma50_day_spot_sl3prcnt import card_sma50_day_spot_sl3prcnt
    # card_data = card_sma50_day_spot_sl3prcnt(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'adjust_trades')

    #6 card_sma50_day_spot_SLmoving2prcnt
    # from .trade_cards.card_sma50_day_spot_SLmoving2prcnt import card_sma50_day_spot_SLmoving2prcnt
    # card_data = card_sma50_day_spot_SLmoving2prcnt(db, signal_db, trade_db, bank_db, signal_trade_db, pair,
    #                                                'adjust_trades')

    #7 card_sma50_day_spot_movingSL_7dif_2move
    # from .trade_cards.card_sma50_day_spot_SLmoving_7dif_2move import card_sma50_day_spot_SLmoving_7dif_2move
    # card_data = card_sma50_day_spot_SLmoving_7dif_2move(db, signal_db, trade_db, bank_db, signal_trade_db, pair,
    #                                                'adjust_trades')

    # 8 card_sma50_day_spot_SL2_SB_4
    # from .trade_cards.card_sma50_day_spot_SL2_SBuy4 import card_sma50_day_spot_SL2_SBuy4
    # card_data = card_sma50_day_spot_SL2_SBuy4(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'adjust_trades')

    # 9 card_sma50_day_spot_0001_SL2_SB7
    # from .trade_cards.card_sma50_day_spot_0001_SL2_SB7 import card_sma50_day_spot_0001_SL2_SB7
    # card_data = card_sma50_day_spot_0001_SL2_SB7(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'adjust_trades')

    # 10 card_sma50_day_futures_0002_shortNOSL
    # from .trade_cards.card_sma50_day_futures_0002_shortNOSL import card_sma50_day_futures_0002_shortNOSL
    # card_data = card_sma50_day_futures_0002_shortNOSL(db, signal_db, trade_db, futures_db, signal_trade_db, pair,
    #                                              'adjust_trades')
    #
    # # 11 card_sma50_day_futures_0003_shortSL2SP10
    # from .trade_cards.card_sma50_day_futures_0003_shortSL2SP10 import card_sma50_day_futures_0003_shortSL2SP10
    # card_data = card_sma50_day_futures_0003_shortSL2SP10(db, signal_db, trade_db, futures_db, signal_trade_db, pair,
    #                                                'adjust_trades')

    # 12 card_sma50_day_spot_0004_shortSP10_longNOSL
    # from .trade_cards.card_sma50_day_futures_0004_shortSP10_longNOSL import card_sma50_day_futures_0004_shortSP10_longNOSL
    # card_data = card_sma50_day_futures_0004_shortSP10_longNOSL(db, signal_db, trade_db, futures_db, signal_trade_db, pair,
    #                                                   'adjust_trades')

    # 13 card_sma50_day_futures_0005_shortSP10_longSL2SB7
    # from .trade_cards.card_sma50_day_futures_0005_shortSP10_longSL2SB7 import card_sma50_day_futures_0005_shortSP10_longSL2SB7
    # card_data = card_sma50_day_futures_0005_shortSP10_longSL2SB7(db, signal_db, trade_db, futures_db, signal_trade_db, pair,
    #                                                   'adjust_trades')

    # 14 card_sma50_day_futures_0006_shortSP10SL2_longSL2SB10
    # vault_id = '0006'
    # from .trade_cards.card_sma50_day_futures_0006_shortSP10SL2_longSL2SB10 import card_sma50_day_futures_0006_shortSP10SL2_longSL2SB10
    # card_data = card_sma50_day_futures_0006_shortSP10SL2_longSL2SB10(db, db_names, pair,'adjust_trades')

    # 15 card_sma50_day_futures_0007_shortSP12_longSL2SB7
    # vault_id = '0007b'
    # from .trade_cards.card_sma50_day_futures_0007_shortSP12_longSL2SB7 import card_sma50_day_futures_0007_shortSP12_longSL2SB7
    # card_data = card_sma50_day_futures_0007_shortSP12_longSL2SB7(db, db_names, pair, 'adjust_trades')

    # 16 card_sma50_day_futures_0007_shortSP12_longSL2SB7
    # vault_id = '0008b'
    # from .trade_cards.card_sma50_day_futures_0008_shortSP9_longSL2SB7 import card_sma50_day_futures_0008_shortSP9_longSL2SB7
    # card_data = card_sma50_day_futures_0008_shortSP9_longSL2SB7(db, db_names, pair, 'adjust_trades')
    #
    # 17 card_sma50_day_futures_0009_shortSP9_longSL2SB7
    vault_id = '0009'
    from .trade_cards.card_sma50_day_futures_0009_shortSP9_longSL2SB7 import card_sma50_day_futures_0009_shortSP9_longSL2SB7
    card_data = card_sma50_day_futures_0009_shortSP9_longSL2SB7(db, db_names, pair, 'adjust_trades')



    to_postman += card_data['to_postman']
    to_crystal += card_data['to_crystal']

    # UPDATE SIGNAL_DB AND NOTE CHANGES
        # ONLY CHECKS IF ORDERS ARE FILLED
        # ONLY TRIGGERS FLAGGING IF TARGET OR STOP_LOSS ARE FILLED or LIQUIDATION


    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }

def vault_take_trades(db, db_names, pair):
    to_postman, to_crystal = '', ''

# TRADE STRATEGIES
    #1 BYPASS
    # from .trade_cards.card__bypass import card__bypass
    # card_info = card__bypass(db, signal_db, trade_db, bank_db, pair)

    #2 LITMUS
    # from .trade_cards.card_litmus import card_litmus
    # card_info = card_litmus(db, signal_db, trade_db, bank_db, signal_trade_db, pair)

    #3 card_sma50_day_spot
    # from .trade_cards.card_sma50_day_spot import card_sma50_day_spot
    # card_info = card_sma50_day_spot(db, signal_db, trade_db, bank_db, signal_trade_db, pair)

    #4 card_sma50_day_spot_sl2prcnt
    # from .trade_cards.card_sma50_day_spot_sl2prcnt import card_sma50_day_spot_sl2prcnt
    # card_info = card_sma50_day_spot_sl2prcnt(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'take_trades')

    #5 card_sma50_day_spot_sl3prcnt
    # from .trade_cards.card_sma50_day_spot_sl3prcnt import card_sma50_day_spot_sl3prcnt
    # card_info = card_sma50_day_spot_sl3prcnt(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'take_trades')

    #6 card_sma50_day_spot_SLmoving2prcnt
    # from .trade_cards.card_sma50_day_spot_SLmoving2prcnt import card_sma50_day_spot_SLmoving2prcnt
    # card_info = card_sma50_day_spot_SLmoving2prcnt(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'take_trades')

    # 7 card_sma50_day_spot_movingSL_7dif_2move
    # from .trade_cards.card_sma50_day_spot_SLmoving_7dif_2move import card_sma50_day_spot_SLmoving_7dif_2move
    # card_info = card_sma50_day_spot_SLmoving_7dif_2move(db, signal_db, trade_db, bank_db, signal_trade_db, pair,'take_trades')

    # 8 card_sma50_day_spot_SL2_SB_4
    # from .trade_cards.card_sma50_day_spot_SL2_SBuy4 import card_sma50_day_spot_SL2_SBuy4
    # card_info = card_sma50_day_spot_SL2_SBuy4(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'take_trades')

    # 9 card_sma50_day_spot_0001_SL2_SB7
    # from .trade_cards.card_sma50_day_spot_0001_SL2_SB7 import card_sma50_day_spot_0001_SL2_SB7
    # card_info = card_sma50_day_spot_0001_SL2_SB7(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'take_trades')

    # 10 card_sma50_day_spot_0002_longSL2SB4_shortNOSL
    # from .trade_cards.card_sma50_day_futures_0002_shortNOSL import card_sma50_day_futures_0002_shortNOSL
    # card_info = card_sma50_day_futures_0002_shortNOSL(db, signal_db, trade_db, futures_db, signal_trade_db, pair, 'take_trades')

    # 11 card_sma50_day_futures_0003_shortSL2SP10
    # from .trade_cards.card_sma50_day_futures_0003_shortSL2SP10 import card_sma50_day_futures_0003_shortSL2SP10
    # card_info = card_sma50_day_futures_0003_shortSL2SP10(db, signal_db, trade_db, futures_db, signal_trade_db, pair,
    #                                                'take_trades')

    # 12 card_sma50_day_futures_0004_shortSP10_longNOSL
    # from .trade_cards.card_sma50_day_futures_0004_shortSP10_longNOSL import card_sma50_day_futures_0004_shortSP10_longNOSL
    # card_info = card_sma50_day_futures_0004_shortSP10_longNOSL(db, signal_db, trade_db, futures_db, signal_trade_db, pair,
    #                                                   'take_trades')

    # 13 card_sma50_day_futures_0005_shortSP10_longSL2SB7
    # from .trade_cards.card_sma50_day_futures_0005_shortSP10_longSL2SB7 import card_sma50_day_futures_0005_shortSP10_longSL2SB7
    # card_info = card_sma50_day_futures_0005_shortSP10_longSL2SB7(db, signal_db, trade_db, futures_db, signal_trade_db, pair,
    #                                                         'take_trades')

    # 14 card_sma50_day_futures_0005_shortSP10SL2_longSL2SB10
    # from .trade_cards.card_sma50_day_futures_0006_shortSP10SL2_longSL2SB10 import card_sma50_day_futures_0006_shortSP10SL2_longSL2SB10
    # card_info = card_sma50_day_futures_0006_shortSP10SL2_longSL2SB10(db, db_names, pair,'take_trades')

    # 15 card_sma50_day_futures_0007_shortSP12_longSL2SB7
    # from .trade_cards.card_sma50_day_futures_0007_shortSP12_longSL2SB7 import card_sma50_day_futures_0007_shortSP12_longSL2SB7
    # card_info = card_sma50_day_futures_0007_shortSP12_longSL2SB7(db, db_names, pair, 'take_trades')

    # 16 card_sma50_day_futures_0008_shortSP9_longSL2SB7
    # from .trade_cards.card_sma50_day_futures_0008_shortSP9_longSL2SB7 import card_sma50_day_futures_0008_shortSP9_longSL2SB7
    # card_info = card_sma50_day_futures_0008_shortSP9_longSL2SB7(db, db_names, pair, 'take_trades')

    # 17 card_sma50_day_futures_0009_shortSP9_longSL2SB7
    from .trade_cards.card_sma50_day_futures_0009_shortSP9_longSL2SB7 import card_sma50_day_futures_0009_shortSP9_longSL2SB7
    card_info = card_sma50_day_futures_0009_shortSP9_longSL2SB7(db, db_names, pair, 'take_trades')



    to_postman += card_info['to_postman']
    to_crystal += card_info['to_crystal']
    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }

def get_bank_spot_values(db, bank_db, timestamp):
    from sqlalchemy import text

    def calculate_total(data, timestamp):
        from ..fz_fetcher import fz_fetcher_fetch_kucoin_coin_price
        total = 0
        if data:
            for coin in data:
                if coin['currency'] == 'USDT':
                    total += round(coin['amount'], 2)
                else:
                    try:
                        # FETCH LAST UPDATED PRICE OF COIN
                        pair = f"{coin['currency']}-USDT"
                        price = fz_fetcher_fetch_kucoin_coin_price(db, timestamp, pair)[0]['close']
                        total += round((float(coin['amount']) * float(price)), 2)
                    except Exception as e:
                        print(f"Error fetching price of {coin['currency']}-USDT: {e}")

        return total

    data_query = text(f"SELECT * FROM {bank_db}")
    coins_data = db.session.execute(data_query).mappings().fetchall()

    serializable_data = [{
        'id': int(row['id']),  # Ensure integer
        'currency': str(row['currency']),  # Ensure string
        'amount': round(float(row['amount']), 5),  # Ensure float
    } for row in coins_data]

    return {
        'total': calculate_total(coins_data, timestamp),
        'coins_data': serializable_data
    }


def get_bank_futures_values(db, trade_db, futures_db, timestamp):
    from sqlalchemy import text
    from .trade_cards._common_functions import get_trades_by_trade_id
    from .trade_cards._common_functions_futures import get_original_buy_in_parameter_of_position_futures
    def calculate_total(data, trade_db):
        total = 0
        if data:
            for coin in data:
                if coin['currency'] == 'USDT':
                    total += round(coin['amount'], 2)
                else:
                    try:
                        # FETCH LAST UPDATED PRICE OF COIN
                        original_amount_in = get_original_buy_in_parameter_of_position_futures(db, trade_db,
                                                                                               coin['trade_id'], 'amount_sell')
                        total += round((float(original_amount_in) + float(coin['pnl'])), 2)
                    except Exception as e:
                        print(f"fn calculate_total Error calculating total value of {coin['currency']}-USDT: {e}")

        return total

    def calculate_pnl(db, futures_db, coin, buy_trade, trade_position, timestamp):
        from ..fz_fetcher import fz_fetcher_fetch_kucoin_coin_price
        pnl = 0
        if coin:
            try:
                # FETCH LAST UPDATED PRICE OF COIN
                pair = f"{coin['currency']}-USDT"
                current_price = fz_fetcher_fetch_kucoin_coin_price(db, timestamp, pair)[0]['close']

                # CALCULATE PNL
                current_value_usdt = float(buy_trade['amount_buy']) * float(current_price)
                if trade_position == 'long':
                    profit_usdt = current_value_usdt - float(buy_trade['amount_sell'])
                if trade_position == 'short':
                    profit_usdt = float(buy_trade['amount_sell']) - current_value_usdt
                # pnl = profit_usdt / current_price
                pnl = profit_usdt

                # UPDATE PNL IN DB
                update_query = text(
                    f"UPDATE {futures_db} SET pnl = :pnl WHERE trade_id = :trade_id"
                )
                db.session.execute(update_query, {
                    "pnl": pnl,
                    "trade_id": buy_trade['trade_id']
                })
                db.session.commit()

            except Exception as e:
                print(f"Error fetching price of {coin['currency']}-USDT: {e}")

        return round(pnl, 5)


    data_query = text(f"SELECT * FROM {futures_db}")
    coins_data = db.session.execute(data_query).mappings().fetchall()
    serializable_data = []
    for coin in coins_data:
        if coin['currency'] == 'USDT':
            serializable_data.append(
                {
                    'id': int(coin['id']),  # Ensure integer
                    'currency': str(coin['currency']),  # Ensure string
                    'amount': round(float(coin['amount']), 5),  # Ensure float
                    'trade_id': int(coin['trade_id']),
                    'trade_position': '',
                    'pnl': round(float(coin['pnl']), 5),
                }
            )
        else:

            trades_of_coin = get_trades_by_trade_id(db, trade_db, [int(coin['trade_id']),])
            filled_buy_trades_of_coin = [trade for trade in trades_of_coin if trade['trade_status'] == 'filled' and trade['trade_action'] == 'buy']
            if filled_buy_trades_of_coin:
                buy_trade = filled_buy_trades_of_coin[0]
                trade_position = filled_buy_trades_of_coin[0]['trade_position']
                current_pnl = calculate_pnl(db, futures_db, coin, buy_trade, trade_position, timestamp)

            serializable_data.append(
                {
                    'id': int(coin['id']),  # Ensure integer
                    'currency': str(coin['currency']),  # Ensure string
                    'amount': round(float(coin['amount']), 5),  # Ensure float
                    'pnl': round(float(current_pnl), 5),
                    'trade_id': int(coin['trade_id']),
                    'trade_position': coin['trade_position'],
                }
            )

    return {
        'total': calculate_total(serializable_data, trade_db),
        'coins_data': serializable_data
    }


def fund_spot(db, bank_db):
    from sqlalchemy import text
    global fund_bank_ini_usdt_value

    data_query = text(f"INSERT INTO {bank_db} (currency, amount) VALUES (:currency, :amount)")
    db.session.execute(data_query, {
        "currency": "USDT",
        "amount": fund_bank_ini_usdt_value
    })
    db.session.commit()

    return get_bank_spot_values(db, bank_db, 0)

def fund_futures(db, trade_db, futures_db):
    from sqlalchemy import text
    global fund_futures_ini_usdt_value

    data_query = text(f"INSERT INTO {futures_db} (currency, amount, trade_id, pnl) VALUES (:currency, :amount, :trade_id, :pnl)")
    db.session.execute(data_query, {
        "currency": "USDT",
        "amount": fund_futures_ini_usdt_value,
        "trade_id": 0,
        "pnl": 0
    })
    db.session.commit()

    return get_bank_futures_values(db, trade_db,futures_db, 0)

