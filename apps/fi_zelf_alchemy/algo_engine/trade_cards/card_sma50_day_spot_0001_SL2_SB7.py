from ._common_functions import *

def card_sma50_day_spot_0001_SL2_SB7(db, signal_db, trade_db, bank_db, signal_trade_db, pair, command):
    if command == 'adjust_trades':
        return adjust_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair)
    elif command == 'take_trades':
        return take_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair)


def adjust_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair):
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''

# FETCH ALL FLAGGED DATA
    flagged_trades_data = fetch_flagged_trades(db, trade_db, pair)
    if flagged_trades_data:
        for data in flagged_trades_data:

# PLACE STOP LOSS based on flagged-filled-buy order
            if data['trade_action'] == 'buy' and data['trade_status'] == 'filled':
                # PLACE STOP LOSS 2 %
                place_SL_data = place_stop_loss(db, signal_db, trade_db, bank_db, signal_trade_db, data['price'], data, 2)
                to_postman += place_SL_data['to_postman']
                to_crystal += place_SL_data['to_crystal']


# PLACE BUY STOP-LIMIT
# if the trend continues, but we got stopped out 4% from the stop-loss sell price
            if data['trade_action'] == 'sell' and data['trade_status'] == 'filled' and data['trade_entry'] == 'stop-limit':
                place_SB_data = place_buy_stop_limit(db, signal_db, trade_db, bank_db, signal_trade_db, data['price'], data, 7)
                to_postman += place_SB_data['to_postman']
                to_crystal += place_SB_data['to_crystal']
                

# UNFLAG AND DEACTIVATE ALL FLAGGED TRADES
            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, trade_db, data)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']

# MOVE STOP LOSS
#     #fetched stop-limit SELL trades that are still placed but not filled
#     stoplimit_trades_data = fetch_stoplimit_trades(db, trade_db, pair)
#     placed_stoplimit_sell_trades_data = [trade for trade in stoplimit_trades_data if trade['trade_status'] == 'placed' and trade['trade_action'] == 'sell']
#     if placed_stoplimit_sell_trades_data:
#         for stoplimit_sell_trade in placed_stoplimit_sell_trades_data:
#             move_stoplimit_up_n_percent_data = move_stoplimit_up_n_percent(db, trade_db, stoplimit_sell_trade, 7, 2)
#             to_postman += move_stoplimit_up_n_percent_data['to_postman']
#             to_crystal += move_stoplimit_up_n_percent_data['to_crystal']
#


    return {
            'to_postman': to_postman,
            'to_crystal': to_crystal
        }



def take_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair):
    # EVERYTHING IS ALREADY TIED TO PAIR

    from ...fz_feeder import fz_feeder_cycle_last_candle


    # print(timestamp_to_time_UTC(fz_feeder_cycle_last_candle['time']))


    to_postman, to_crystal = '', ''

    # NEW SIGNALS SECTION
    not_traded_signals = fetch_not_traded_signals(db, signal_db, signal_trade_db, pair)  # checks that it is active too
    not_traded_sma50_bull_day_signals_of_pair = [signal for signal in not_traded_signals if signal['signal_type'] == 'SMA50' and signal['trend_type'] == 'bull' and signal['interval'] == '1day']
    not_traded_sma50_bear_day_signals_of_pair = [signal for signal in not_traded_signals if signal['signal_type'] == 'SMA50' and signal['trend_type'] == 'bear' and signal['interval'] == '1day']

    # IF BULL
    if not_traded_sma50_bull_day_signals_of_pair:

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
            signal=not_traded_sma50_bull_day_signals_of_pair[0],
            price=not_traded_sma50_bull_day_signals_of_pair[0]['tp_entrance_1'],
            amount_in=currency_sell_balance,
            trade_type='spot',  # spot, futures
            trade_position='long',  # long/short
            trade_action='buy',  # buy/sell
            trade_entry='limit',
            currency_buy=currency_buy,
            currency_sell=currency_sell,
            tdp_0=fz_feeder_cycle_last_candle['time']
        )
        to_postman += place_new_order_data['to_postman']
        to_crystal += place_new_order_data['to_crystal']

    # IF BEAR - bull is flagged
    flagged_signals = fetch_flagged_signals(db, signal_db, pair)
    flagged_sma50_day_bull_signals = [signal for signal in flagged_signals if
                                      signal['signal_type'] == 'SMA50' and
                                      signal['interval'] == '1day' and
                                      signal['trend_type'] == 'bull']

    # DEACTIVATE AND UNFLAG ALL TRADES OF SIGNAL
    for flagged_bull_signal in flagged_sma50_day_bull_signals:
        trades_of_signal = get_trades_by_signal(db, signal_trade_db, trade_db, flagged_bull_signal['id'])
        for trade in trades_of_signal:
            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, trade_db, trade)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']

        currency_sell = flagged_bull_signal['trading_pair'].split('-')[0]
        currency_buy = flagged_bull_signal['trading_pair'].split('-')[1]
        currency_sell_balance = fetch_bank_currency_balance(db, bank_db, currency_sell)

        if currency_sell_balance > 0:
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
                price=not_traded_sma50_bear_day_signals_of_pair[0]['tp_entrance_1'],
                amount_in=currency_sell_balance,
                trade_type='spot',  # spot, futures
                trade_position='long',  # long/short
                trade_action='sell',  # buy/sell
                trade_entry='limit',
                currency_buy=currency_buy,
                currency_sell=currency_sell,
                tdp_0=fz_feeder_cycle_last_candle['time']
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