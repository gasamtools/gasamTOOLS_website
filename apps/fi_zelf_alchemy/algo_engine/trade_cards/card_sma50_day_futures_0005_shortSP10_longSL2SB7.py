from ._common_functions import *
from._common_functions_spot import *
from._common_functions_futures import *

def card_sma50_day_futures_0005_shortSP10_longSL2SB7(db, signal_db, trade_db, futures_db, signal_trade_db, pair, command):
    if command == 'adjust_trades':
        return adjust_trades(db, signal_db, trade_db, futures_db, signal_trade_db, pair)
    elif command == 'take_trades':
        return take_trades(db, signal_db, trade_db, futures_db, signal_trade_db, pair)


def adjust_trades(db, signal_db, trade_db, futures_db, signal_trade_db, pair):
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''

# FETCH ALL FLAGGED DATA
    flagged_trades_data = fetch_flagged_trades(db, trade_db, pair)
    shorts_buy_limit_flagged_trades_data = [trade for trade in flagged_trades_data if trade['trade_position'] == 'short' and trade['trade_action'] == 'buy' and trade['trade_entry'] == 'limit']
    longs_buy_limit_flagged_trades_data = [trade for trade in flagged_trades_data if trade['trade_position'] == 'long' and trade['trade_action'] == 'buy' and trade['trade_entry'] == 'limit']
    print(flagged_trades_data)
# SHORTs SL/SP
    if shorts_buy_limit_flagged_trades_data:
        for data in shorts_buy_limit_flagged_trades_data:

    # PLACE STOP LOSS 2%  based on flagged-filled-buy order
#             place_SL_data = place_stop_lossProfit_futures(db, signal_db, trade_db, futures_db, signal_trade_db,
#                                                           data['price'], data, 2, 'loss')
#             to_postman += place_SL_data['to_postman']
#             to_crystal += place_SL_data['to_crystal']

    # PLACE STOP PROFIT 10%  based on flagged-filled-buy order
            place_SL_data = place_stop_lossProfit_futures(db, signal_db, trade_db, futures_db, signal_trade_db,
                                                          data['price'], data, 10, 'profit')
            to_postman += place_SL_data['to_postman']
            to_crystal += place_SL_data['to_crystal']


# LONGSs SL/SB
        if longs_buy_limit_flagged_trades_data:
            for data in longs_buy_limit_flagged_trades_data:
                pass
                print(longs_buy_limit_flagged_trades_data)
        # PLACE STOP LOSS 2%  based on flagged-filled-buy order
                place_SL_data = place_stop_lossProfit_futures(db, signal_db, trade_db, futures_db, signal_trade_db,
                                                              data['price'], data, 2, 'loss')
                to_postman += place_SL_data['to_postman']
                to_crystal += place_SL_data['to_crystal']

# PLACE BUY STOP-LIMIT
# if the trend continues, but we got stopped out 7% from the stop-loss sell price
#             if data['trade_action'] == 'sell' and data['trade_status'] == 'filled' and data['trade_entry'] == 'stop-limit':
#                 place_SB_data = place_buy_stop_limit(db, signal_db, trade_db, bank_db, signal_trade_db, data['price'], data, 7)
#                 to_postman += place_SB_data['to_postman']
#                 to_crystal += place_SB_data['to_crystal']


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



def take_trades(db, signal_db, trade_db, futures_db, signal_trade_db, pair):
    # EVERYTHING IS ALREADY TIED TO PAIR
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''

    # FETCH FLAGGED SIGNALS and TRADES
    flagged_signals = fetch_flagged_signals(db, signal_db, pair)
    flagged_trades = fetch_flagged_trades(db, trade_db, pair)

    active_placed_trades = fetch_active_placed_trades_from_trade_db(db, trade_db)
    active_placed_long_sell_limit_trades = [trade for trade in active_placed_trades if trade['trade_position'] == 'long' and trade['trade_action'] == 'sell' and trade['trade_entry'] == 'limit']
    active_placed_short_sell_limit_trades = [trade for trade in active_placed_trades if trade['trade_position'] == 'short' and trade['trade_action'] == 'sell' and trade['trade_entry'] == 'limit']


    # FETCH NEW SIGNALS
    not_traded_signals = fetch_not_traded_signals(db, signal_db, signal_trade_db, pair)  # checks that it is active too
    not_traded_sma50_bull_day_signals_of_pair = [signal for signal in not_traded_signals if signal['signal_type'] == 'SMA50' and signal['trend_type'] == 'bull' and signal['interval'] == '1day']
    not_traded_sma50_bear_day_signals_of_pair = [signal for signal in not_traded_signals if signal['signal_type'] == 'SMA50' and signal['trend_type'] == 'bear' and signal['interval'] == '1day']

# BULL: IF BULL IS FLAGGED
    flagged_sma50_day_bull_signals = [signal for signal in flagged_signals if
                                      signal['signal_type'] == 'SMA50' and
                                      signal['interval'] == '1day' and
                                      signal['trend_type'] == 'bull']

    # BULL: DEACTIVATE AND UNFLAG ALL TRADES OF SIGNAL
    for flagged_bull_signal in flagged_sma50_day_bull_signals:
        trades_of_signal = get_trades_by_signal(db, signal_trade_db, trade_db, flagged_bull_signal['id'])
        for trade in trades_of_signal:
            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, trade_db, trade)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']


    # BULL: PLACE SELL ORDER
    if flagged_sma50_day_bull_signals:
        this_data = place_futures_order(db, signal_db, trade_db, futures_db, signal_trade_db,
                                        pair,
                                        flagged_sma50_day_bull_signals[0],
                                        fz_feeder_cycle_last_candle['close'],
                                        'long',
                                        'sell',
                                        'limit')
        to_postman += this_data['to_postman']
        to_crystal += this_data['to_crystal']

# BEAR: IF BEAR IS FLAGGED
    flagged_sma50_day_bear_signals = [signal for signal in flagged_signals if
                                      signal['signal_type'] == 'SMA50' and
                                      signal['interval'] == '1day' and
                                      signal['trend_type'] == 'bear']

    # BEAR: DEACTIVATE AND UNFLAG ALL TRADES OF SIGNAL
    for flagged_bear_signal in flagged_sma50_day_bear_signals:
        trades_of_signal = get_trades_by_signal(db, signal_trade_db, trade_db, flagged_bear_signal['id'])
        for trade in trades_of_signal:
            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, trade_db, trade)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']

    # BEAR: PLACE SELL ORDER
    if flagged_sma50_day_bear_signals:
        this_data = place_futures_order(db, signal_db, trade_db, futures_db, signal_trade_db,
                                        pair=pair,
                                        signal=flagged_sma50_day_bear_signals[0],
                                        price=fz_feeder_cycle_last_candle['close'],
                                        trade_position='short',
                                        trade_action='sell',
                                        trade_entry='limit')
        to_postman += this_data['to_postman']
        to_crystal += this_data['to_crystal']

# BULL: IF NEW BULL signal
    if not_traded_sma50_bull_day_signals_of_pair and not active_placed_short_sell_limit_trades:
        this_data = place_futures_order(db, signal_db, trade_db, futures_db, signal_trade_db,
                                        pair,
                                        not_traded_sma50_bull_day_signals_of_pair[0],
                                        fz_feeder_cycle_last_candle['close'],
                                        'long',
                                        'buy',
                                        'limit')
        to_postman += this_data['to_postman']
        to_crystal += this_data['to_crystal']

# BEAR: IF NEW BEAR signal
    if not_traded_sma50_bear_day_signals_of_pair and not active_placed_long_sell_limit_trades:
        this_data = place_futures_order(db, signal_db, trade_db, futures_db, signal_trade_db,
                                        pair=pair,
                                        signal=not_traded_sma50_bear_day_signals_of_pair[0],
                                        price=fz_feeder_cycle_last_candle['close'],
                                        trade_position='short',
                                        trade_action='buy',
                                        trade_entry='limit')
        to_postman += this_data['to_postman']
        to_crystal += this_data['to_crystal']

# BULL&BEAR: UNFLAG AND DEACTIVATE ALL FLAGGED TRADES
    if flagged_trades:
        for data in flagged_trades:
            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, trade_db, data)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']

# BULL&BEAR: UNFLAG AND DEACTIVATE ALL FLAGGED SIGNALS
    unflag_and_deactivate_signals_data = unflag_and_deactivate_signals(db, signal_db, pair, flagged_signals)
    to_postman += unflag_and_deactivate_signals_data['to_postman']
    to_crystal += unflag_and_deactivate_signals_data['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }