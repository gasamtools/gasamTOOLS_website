from ._common_functions import *
from._common_functions_spot import *
from._common_functions_futures import *

def card_sma50_day_futures_0008_shortSP9_longSL2SB7(db, db_names, pair, command):

    if command == 'adjust_trades':
        return adjust_trades(db, db_names, pair)
    elif command == 'take_trades':
        return take_trades(db, db_names, pair)


def adjust_trades(db, db_names, pair):
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''

# FETCH ALL FLAGGED DATA
    flagged_trades_data = fetch_flagged_trades(db, db_names['trade_db'], pair)
    shorts_buy_limit_flagged_trades_data = [trade for trade in flagged_trades_data if trade['trade_position'] == 'short' and trade['trade_action'] == 'buy' and trade['trade_entry'] == 'limit']
    shorts_sell_stoplimit_flagged_trades_data = [trade for trade in flagged_trades_data if trade['trade_position'] == 'short' and trade['trade_action'] == 'sell' and trade['trade_entry'] == 'stop-limit']

    longs_buy_limit_flagged_trades_data = [trade for trade in flagged_trades_data if trade['trade_position'] == 'long' and trade['trade_action'] == 'buy' and trade['trade_entry'] == 'limit']
    longs_sell_stoplimit_flagged_trades_data = [trade for trade in flagged_trades_data if trade['trade_position'] == 'long' and trade['trade_action'] == 'sell' and trade['trade_entry'] == 'stop-limit']

# SHORTs SL/SP
    if shorts_buy_limit_flagged_trades_data:
        for data in shorts_buy_limit_flagged_trades_data:
            pass
    # PLACE STOP LOSS 2%  based on flagged-filled-buy order
    #         place_SL_data = place_stop_lossProfit_futures(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'], db_names['signal_trade_db'],
    #                                                       data['price'], data, 2, 'loss')
    #         to_postman += place_SL_data['to_postman']
    #         to_crystal += place_SL_data['to_crystal']

    # PLACE STOP PROFIT 12%  based on flagged-filled-buy order
            place_SL_data = place_stop_lossProfit_futures(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'], db_names['signal_trade_db'],
                                                          data['price'], data, 9, 'profit')
            to_postman += place_SL_data['to_postman']
            to_crystal += place_SL_data['to_crystal']

    # CHECK IF ANY STOP-LIMIT TRADES GOT FILLED AND CANCEL OTHERS
    if shorts_sell_stoplimit_flagged_trades_data:
        active_placed_trades = fetch_active_placed_trades_from_trade_db(db, db_names['trade_db'])
        for data in active_placed_trades:
            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, db_names['trade_db'], data)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']

# LONGSs SL
    if longs_buy_limit_flagged_trades_data:
        for data in longs_buy_limit_flagged_trades_data:
    # PLACE STOP LOSS 2%  based on flagged-filled-buy order
            place_SL_data = place_stop_lossProfit_futures(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'], db_names['signal_trade_db'],
                                                          data['price'], data, 2, 'loss')
            to_postman += place_SL_data['to_postman']
            to_crystal += place_SL_data['to_crystal']

# LONGSs SB
# if the trend continues, but we got stopped out 7% from the stop-loss sell price
    if longs_sell_stoplimit_flagged_trades_data:
        for data in longs_sell_stoplimit_flagged_trades_data:
            place_SB_data = place_stop_buy_futures(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'], db_names['signal_trade_db'],
                                                          data['price'], data, 7, 'loss')
            to_postman += place_SB_data['to_postman']
            to_crystal += place_SB_data['to_crystal']



    return {
            'to_postman': to_postman,
            'to_crystal': to_crystal
        }



def take_trades(db, db_names, pair):
    # EVERYTHING IS ALREADY TIED TO PAIR

    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''

    # FETCH FLAGGED SIGNALS and TRADES
    flagged_signals = fetch_flagged_signals(db, db_names['signal_db'], pair)
    flagged_trades = fetch_flagged_trades(db, db_names['trade_db'], pair)

    # FETCH ACTIVE SIGNALS
    active_signals = fetch_active_signals(db, db_names['signal_db'], pair)
    bull_active_signals = [signal for signal in active_signals if signal['signal_type'] == 'SMA50' and signal['interval'] == '1day' and signal['trend_type'] == 'bull']
    bear_active_signals = [signal for signal in active_signals if signal['signal_type'] == 'SMA50' and signal['interval'] == '1day' and signal['trend_type'] == 'bear']


    active_placed_trades = fetch_active_placed_trades_from_trade_db(db, db_names['trade_db'])
    active_placed_long_buy_stoplimit_trades = [trade for trade in active_placed_trades if trade['trade_position'] == 'long' and trade['trade_action'] == 'buy' and trade['trade_entry'] == 'stop-limit']
    active_placed_short_buy_stoplimit_trades = [trade for trade in active_placed_trades if trade['trade_position'] == 'short' and trade['trade_action'] == 'buy' and trade['trade_entry'] == 'stop-limit']


    # FETCH NEW SIGNALS
    # not_traded_signals = fetch_not_traded_signals(db, db_names['signal_db'], db_names['signal_trade_db'], pair)  # checks that it is active too
    # not_traded_sma50_bull_day_signals_of_pair = [signal for signal in not_traded_signals if signal['signal_type'] == 'SMA50' and signal['trend_type'] == 'bull' and signal['interval'] == '1day']
    # not_traded_sma50_bear_day_signals_of_pair = [signal for signal in not_traded_signals if signal['signal_type'] == 'SMA50' and signal['trend_type'] == 'bear' and signal['interval'] == '1day']

    active_not_flagged_not_traded_signals = fetch_active_not_flagged_not_traded_signals(db, db_names['signal_db'], pair)
    active_not_flagged_not_traded_signals_bull = [signal for signal in active_not_flagged_not_traded_signals if signal['signal_type'] == 'SMA50' and signal['trend_type'] == 'bull' and signal['interval'] == '1day']
    active_not_flagged_not_traded_signals_bear = [signal for signal in active_not_flagged_not_traded_signals if signal['signal_type'] == 'SMA50' and signal['trend_type'] == 'bear' and signal['interval'] == '1day']

    # BULL: IF BULL IS FLAGGED
    flagged_sma50_day_bull_signals = [signal for signal in flagged_signals if
                                      signal['signal_type'] == 'SMA50' and
                                      signal['interval'] == '1day' and
                                      signal['trend_type'] == 'bull']

    # BULL: DEACTIVATE AND UNFLAG ALL TRADES OF SIGNAL
    for flagged_bull_signal in flagged_sma50_day_bull_signals:
        trades_of_signal = get_trades_by_signal(db, db_names['signal_trade_db'], db_names['trade_db'], flagged_bull_signal['id'])
        for trade in trades_of_signal:
            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, db_names['trade_db'], trade)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']


    # BULL: PLACE SELL ORDER
    if flagged_sma50_day_bull_signals:
        this_data = place_futures_order(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'], db_names['signal_trade_db'],
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
        trades_of_signal = get_trades_by_signal(db, db_names['signal_trade_db'], db_names['trade_db'], flagged_bear_signal['id'])
        for trade in trades_of_signal:
            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, db_names['trade_db'], trade)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']

    # BEAR: PLACE SELL ORDER
    if flagged_sma50_day_bear_signals:
        this_data = place_futures_order(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'], db_names['signal_trade_db'],
                                        pair=pair,
                                        signal=flagged_sma50_day_bear_signals[0],
                                        price=fz_feeder_cycle_last_candle['close'],
                                        trade_position='short',
                                        trade_action='sell',
                                        trade_entry='limit')
        to_postman += this_data['to_postman']
        to_crystal += this_data['to_crystal']

# BULL: IF NEW BULL signal
#     print(f'BULL active_not_flagged_not_traded_signals_bull {active_not_flagged_not_traded_signals_bull}')
#     print(f'BULL active_placed_long_buy_stoplimit_trades {active_placed_long_buy_stoplimit_trades}')
    if active_not_flagged_not_traded_signals_bull and not active_placed_long_buy_stoplimit_trades:
        this_data = place_futures_order(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'], db_names['signal_trade_db'],
                                        pair,
                                        active_not_flagged_not_traded_signals_bull[0],
                                        fz_feeder_cycle_last_candle['close'],
                                        'long',
                                        'buy',
                                        'limit')
        to_postman += this_data['to_postman']
        to_crystal += this_data['to_crystal']

# BEAR: IF NEW BEAR signal
#     print(f'BEAR active_not_flagged_not_traded_signals_bear {active_not_flagged_not_traded_signals_bear}')
#     print(f'BEAR active_placed_short_buy_stoplimit_trades {active_placed_short_buy_stoplimit_trades}')
    if active_not_flagged_not_traded_signals_bear and not active_placed_short_buy_stoplimit_trades:
        this_data = place_futures_order(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'], db_names['signal_trade_db'],
                                        pair=pair,
                                        signal=active_not_flagged_not_traded_signals_bear[0],
                                        price=fz_feeder_cycle_last_candle['close'],
                                        trade_position='short',
                                        trade_action='buy',
                                        trade_entry='limit')
        to_postman += this_data['to_postman']
        to_crystal += this_data['to_crystal']

# BULL&BEAR: UNFLAG AND DEACTIVATE ALL FLAGGED TRADES
    if flagged_trades:
        for data in flagged_trades:
            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, db_names['trade_db'], data)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']

# BULL&BEAR: UNFLAG AND DEACTIVATE ALL FLAGGED SIGNALS
    unflag_and_deactivate_signals_data = unflag_and_deactivate_signals(db, db_names['signal_db'], pair, flagged_signals)
    to_postman += unflag_and_deactivate_signals_data['to_postman']
    to_crystal += unflag_and_deactivate_signals_data['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }