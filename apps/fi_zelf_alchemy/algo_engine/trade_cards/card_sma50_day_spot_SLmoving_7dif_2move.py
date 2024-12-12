from ._common_functions import *

def card_sma50_day_spot_SLmoving_7dif_2move(db, signal_db, trade_db, bank_db, signal_trade_db, pair, command):
    if command == 'adjust_trades':
        return adjust_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair)
    elif command == 'take_trades':
        return take_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair)


def adjust_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair):
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''

# PLACE STOP LOSS
    flagged_trades_data = fetch_flagged_trades(db, trade_db)
    if flagged_trades_data:
        for data in flagged_trades_data:
            if data['trade_action'] == 'buy' and data['trade_status'] == 'filled':

                # PLACE STOP LOSS
                stop_price = subtract_n_percent( data['price'], 2)  # Subtract 3% of the value

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
                to_postman += place_stop_loss_order_data['to_postman']
                to_crystal += place_stop_loss_order_data['to_crystal']

            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, trade_db, data)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']

#MOVE STOP LOSS
    #fetched stop-limit trades that are still placed but not filled
    stoplimit_trades_data = fetch_stoplimit_trades(db, trade_db)
    placed_stoplimit_trades_data = [trade for trade in stoplimit_trades_data if trade['trade_status'] == 'placed']
    if placed_stoplimit_trades_data:

        if is_difference_at_least_n_percent(fz_feeder_cycle_last_candle['close'], placed_stoplimit_trades_data[0]['trade_entry_stop'], 7):

            update_data = {
                'trade_entry_stop':add_n_percent(placed_stoplimit_trades_data[0]['trade_entry_stop'], 2),
                'price': add_n_percent(placed_stoplimit_trades_data[0]['price'], 2),
                'amount_buy': placed_stoplimit_trades_data[0]['amount_sell'] * add_n_percent(placed_stoplimit_trades_data[0]['price'], 2),
                'tdp_0': fz_feeder_cycle_last_candle['time']
            }

            update_trade_in_trade_db_data = update_trade_in_trade_db(
                db=db,
                trade_db=trade_db,
                record_id=placed_stoplimit_trades_data[0]['id'],
                update_data=update_data)
            to_postman += update_trade_in_trade_db_data['to_postman']
            to_crystal += update_trade_in_trade_db_data['to_crystal']

    return {
            'to_postman': to_postman,
            'to_crystal': to_crystal
        }


def take_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair):
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''

    # NEW SIGNALS SECTION
    not_traded_signals = fetch_not_traded_signals(db, signal_db, signal_trade_db, pair)  # checks that it is active too
    not_traded_sma50_bull_day_signals = [signal for signal in not_traded_signals if signal['signal_type'] == 'SMA50' and signal['trend_type'] == 'bull' and signal['interval'] == '1day']
    not_traded_sma50_bear_day_signals = [signal for signal in not_traded_signals if signal['signal_type'] == 'SMA50' and signal['trend_type'] == 'bear' and signal['interval'] == '1day']

    # IF BULL
    if not_traded_sma50_bull_day_signals:

        currency_buy = pair.split('-')[0]
        currency_sell = pair.split('-')[1]

        currency_sell_balance = fetch_bank_currency_balance(db, bank_db, currency_sell)

        # ESTABLISH TRADE ID
        new_trade_id = get_new_trade_id(db, trade_db)

        place_new_order_data = place_new_order(
            db=db,
            signal_db=signal_db,
            trade_db=trade_db,
            bank_db=bank_db,
            signal_trade_db=signal_trade_db,
            trade_id=new_trade_id,
            signal=not_traded_sma50_bull_day_signals[0],
            price=not_traded_sma50_bull_day_signals[0]['tp_entrance_1'],
            amount_in=currency_sell_balance,
            trade_type='spot',  # spot, futures
            trade_position='long',  # long/short
            trade_action='buy',  # buy/sell
            trade_entry='limit',
            currency_buy=currency_buy,
            currency_sell=currency_sell
        )
        to_postman += place_new_order_data['to_postman']
        to_crystal += place_new_order_data['to_crystal']

    # IF BEAR - bull is flagged
    flagged_signals = fetch_flagged_signals(db, signal_db, pair)
    flagged_sma50_day_bull_signals = [signal for signal in flagged_signals if
                                      signal['signal_type'] == 'SMA50' and
                                      signal['interval'] == '1day' and
                                      signal['trend_type'] == 'bull']
    if flagged_sma50_day_bull_signals:

        currency_sell = pair.split('-')[0]
        currency_buy = pair.split('-')[1]

        currency_sell_balance = fetch_bank_currency_balance(db, bank_db, currency_sell)
        stoplimit_trades_data = fetch_stoplimit_trades(db, trade_db)

        # CHECK IF SELL POSITION STILL EXISTS
        if stoplimit_trades_data:
            for data in stoplimit_trades_data:
                # UNFLAG AND DEACTIVATE STOP LIMIT ORDERS
                unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, trade_db, data)
                to_postman += unflag_and_deactivate_trades_data['to_postman']
                to_crystal += unflag_and_deactivate_trades_data['to_crystal']

                # PLACE NEW SELL TRADE
                new_trade_id = get_new_trade_id(db, trade_db)

                place_new_order_data = place_new_order(
                    db=db,
                    signal_db=signal_db,
                    trade_db=trade_db,
                    bank_db=bank_db,
                    signal_trade_db=signal_trade_db,
                    trade_id=new_trade_id,
                    signal=flagged_sma50_day_bull_signals[0],
                    price=not_traded_sma50_bear_day_signals[0]['tp_entrance_1'],
                    amount_in=currency_sell_balance,
                    trade_type='spot',  # spot, futures
                    trade_position='long',  # long/short
                    trade_action='sell',  # buy/sell
                    trade_entry='limit',
                    currency_buy=currency_buy,
                    currency_sell=currency_sell
                )
                to_postman += place_new_order_data['to_postman']
                to_crystal += place_new_order_data['to_crystal']

    unflag_and_deactivate_signals_data = unflag_and_deactivate_signals(db, signal_db, pair, flagged_signals)
    to_postman += unflag_and_deactivate_signals_data['to_postman']
    to_crystal += unflag_and_deactivate_signals_data['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }