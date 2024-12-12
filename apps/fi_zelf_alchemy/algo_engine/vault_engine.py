fund_bank_ini_usdt_value = 1000
def vault_engine(db, signal_db, trade_db, bank_db,  signal_trade_db, action, pair):
    if action == 'adjust_trades':
        return vault_adjust_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair)
    if action == 'take_trades':
        return vault_take_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair)

def  vault_adjust_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair):
    from .trade_cards._common_functions import fetch_active_placed_trades_from_trade_db
    from .trade_cards._common_functions import update_bank_balances_and_trade_db
    from ..fz_fetcher import fz_fetcher_update_orders

    to_postman, to_crystal = '', ''

    # FETCH active placed orders DATA FROM db
    placed_active_trades = fetch_active_placed_trades_from_trade_db(db, trade_db)

    # FETCH flagged_trades DATA FROM KUCOIN - FLAGGED BECAUSE FILLED
    flagged_filled_trades = fz_fetcher_update_orders(db, bank_db, placed_active_trades)

    # UPDATE BANK and TRADE_DB AND NOTE CHANGES
    for trade in flagged_filled_trades:
        update_bank_balances_and_trade_db_data = update_bank_balances_and_trade_db(db, bank_db, trade_db, trade)
        to_postman += update_bank_balances_and_trade_db_data['to_postman']
        to_crystal += update_bank_balances_and_trade_db_data['to_crystal']

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

    # 9 card_sma50_day_spot_SL2_SB_4
    # from .trade_cards.card_sma50_day_spot_0001_SL2_SB7 import card_sma50_day_spot_0001_SL2_SB7
    # card_data = card_sma50_day_spot_0001_SL2_SB7(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'adjust_trades')

    # 10 card_sma50_day_spot_0002_longSL2SB4_shortNOSL
    from .trade_cards.card_sma50_day_spot_0002_longSL2SB4_shortNOSL import card_sma50_day_spot_0002_longSL2SB4_shortNOSL
    card_data = card_sma50_day_spot_0002_longSL2SB4_shortNOSL(db, signal_db, trade_db, bank_db, signal_trade_db, pair,
                                                 'adjust_trades')



    to_postman += card_data['to_postman']
    to_crystal += card_data['to_crystal']

    # UPDATE SIGNAL_DB AND NOTE CHANGES
        # ONLY CHECKS IF ORDERS ARE FILLED
        # ONLY TRIGGERS FLAGGING IF TARGET OR STOP_LOSS ARE FILLED or LIQUIDATION


    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }

def vault_take_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair):
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

    # 9 card_sma50_day_spot_0001_SL2_SB4
    # from .trade_cards.card_sma50_day_spot_0001_SL2_SB7 import card_sma50_day_spot_0001_SL2_SB7
    # card_info = card_sma50_day_spot_0001_SL2_SB7(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'take_trades')

    # 10 card_sma50_day_spot_0001_SL2_SB4
    from .trade_cards.card_sma50_day_spot_0002_longSL2SB4_shortNOSL import card_sma50_day_spot_0002_longSL2SB4_shortNOSL
    card_info = card_sma50_day_spot_0002_longSL2SB4_shortNOSL(db, signal_db, trade_db, bank_db, signal_trade_db, pair, 'take_trades')




    to_postman += card_info['to_postman']
    to_crystal += card_info['to_crystal']
    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }

def get_bank_values(db, bank_db, timestamp):
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
        'amount': round(float(row['amount']), 5)  # Ensure float
    } for row in coins_data]

    return {
        'total': calculate_total(coins_data, timestamp),
        'coins_data': serializable_data
    }


def fund_bank(db, bank_db):
    from sqlalchemy import text
    global fund_bank_ini_usdt_value

    data_query = text(f"INSERT INTO {bank_db} (currency, amount) VALUES (:currency, :amount)")
    db.session.execute(data_query, {
        "currency": "USDT",
        "amount": fund_bank_ini_usdt_value
    })
    db.session.commit()

    return get_bank_values(db, bank_db, 0)

