from._common_functions_futures import *

def card_sma50_day_futures_0009_shortSP9_longSL2SB7(db, db_names, pair, command):
    if command == 'adjust_trades':
        return adjust_trades(db, db_names, pair)
    elif command == 'take_trades':
        return take_trades(db, db_names, pair)


def adjust_trades(db, db_names, pair):
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''

    # FETCH ACTIVE SIGNALS
    active_signals = fetch_active_signals(db, db_names['signal_db'], pair)
    bull_active_sma50_1day_signals = [signal for signal in active_signals if signal['signal_type'] == 'SMA50' and signal['interval'] == '1day' and signal['trend_type'] == 'bull']
    bear_active_sma50_1day_signals = [signal for signal in active_signals if signal['signal_type'] == 'SMA50' and signal['interval'] == '1day' and signal['trend_type'] == 'bear']

    # BULL TRADES
    if bull_active_sma50_1day_signals:
        for bull_signal in bull_active_sma50_1day_signals:
            trades_of_signal = get_trades_by_signal(db, db_names['signal_trade_db'], db_names['trade_db'], bull_signal['id'])
            longs_sell_stoplimit_active_trades_data = [trade for trade in trades_of_signal if trade['trade_position'] == 'long' and trade['trade_action'] == 'sell' and trade['trade_entry'] == 'stop-limit' and trade['is_active']]
            longs_buy_stoplimit_active_trades_data = [trade for trade in trades_of_signal if trade['trade_position'] == 'long' and trade['trade_action'] == 'buy' and trade['trade_entry'] == 'stop-limit' and trade['is_active']]


            if bull_signal['trade_level'] == 1 and not longs_sell_stoplimit_active_trades_data:  # IF BULL buy order is filled
            # PLACE STOP LOSS 2%
                longs_buy_trades_data = [trade for trade in trades_of_signal if trade['trade_position'] == 'long' and trade['trade_action'] == 'buy']
                place_SL_data = place_stop_lossProfit_futures(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'], db_names['signal_trade_db'],
                                                              trade_level=2,
                                                              base_price=fz_feeder_cycle_last_candle['close'],
                                                              data=longs_buy_trades_data[-1],
                                                              percent=2,
                                                              type='loss')
                to_postman += place_SL_data['to_postman']
                to_crystal += place_SL_data['to_crystal']

            if bull_signal['trade_level'] == 2 and not longs_buy_stoplimit_active_trades_data:  # IF BULL sell stop-limit is filled
            # PLACE STOP BUY 7%
                longs_sell_stoplimit_trades_data = [trade for trade in trades_of_signal if trade['trade_position'] == 'long' and trade['trade_action'] == 'sell' and trade['trade_entry'] == 'stop-limit']
                place_SB_data = place_stop_buy_futures(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'], db_names['signal_trade_db'],
                                                       trade_level=1,
                                                       base_price=fz_feeder_cycle_last_candle['close'],
                                                       data=longs_sell_stoplimit_trades_data[-1],
                                                       percent=7,
                                                       type='loss')
                to_postman += place_SB_data['to_postman']
                to_crystal += place_SB_data['to_crystal']

    # BEAR TRADES
    if bear_active_sma50_1day_signals:
        for bear_signal in bear_active_sma50_1day_signals:
            trades_of_signal = get_trades_by_signal(db, db_names['signal_trade_db'], db_names['trade_db'], bear_signal['id'])
            shorts_sell_stoplimit_active_trades_data = [trade for trade in trades_of_signal if trade['trade_position'] == 'short' and trade['trade_action'] == 'sell' and trade['trade_entry'] == 'stop-limit' and trade['is_active']]

            if bear_signal['trade_level'] == 1 and not shorts_sell_stoplimit_active_trades_data:  # IF BEAR buy is filled
            # PLACE STOP PROFIT 9%
                shorts_buy_trades_data = [trade for trade in trades_of_signal if trade['trade_position'] == 'short' and trade['trade_action'] == 'buy']
                place_SP_data = place_stop_lossProfit_futures(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'], db_names['signal_trade_db'],
                                                        trade_level=2,
                                                        base_price=fz_feeder_cycle_last_candle['close'],
                                                        data=shorts_buy_trades_data[-1],
                                                        percent=9,
                                                        type='profit')
                to_postman += place_SP_data['to_postman']
                to_crystal += place_SP_data['to_crystal']

            if bear_signal['trade_level'] == 2:  # IF BEAR sell stop-profit is filled
                for trade in trades_of_signal:
                    unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, db_names['trade_db'], trade)
                    to_postman += unflag_and_deactivate_trades_data['to_postman']
                    to_crystal += unflag_and_deactivate_trades_data['to_crystal']

    return {
            'to_postman': to_postman,
            'to_crystal': to_crystal
        }


def take_trades(db, db_names, pair):
    # EVERYTHING IS ALREADY TIED TO PAIR

    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''

    # FETCH ACTIVE SIGNALS
    active_signals = fetch_active_signals(db, db_names['signal_db'], pair)
    bull_active_sma50_1day_signals = [signal for signal in active_signals if signal['signal_type'] == 'SMA50' and signal['interval'] == '1day' and signal['trend_type'] == 'bull']
    bear_active_sma50_1day_signals = [signal for signal in active_signals if signal['signal_type'] == 'SMA50' and signal['interval'] == '1day' and signal['trend_type'] == 'bear']
    flagged_active_signals = [signal for signal in active_signals if signal['signal_type'] == 'SMA50' and signal['interval'] == '1day' and signal['is_flagged']]

    # BULL TRADES
    if bull_active_sma50_1day_signals:
        for bull_signal in bull_active_sma50_1day_signals:
            if bull_signal['trade_level'] == 9:  # IF BULL IS FLAGGED
                # DEACTIVATE AND UNFLAG ALL TRADES OF SIGNAL
                trades_of_signal = get_trades_by_signal(db, db_names['signal_trade_db'], db_names['trade_db'], bull_signal['id'])
                for trade in trades_of_signal:
                    unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, db_names['trade_db'], trade)
                    to_postman += unflag_and_deactivate_trades_data['to_postman']
                    to_crystal += unflag_and_deactivate_trades_data['to_crystal']

                # PLACE SELL ORDER
                this_data = place_futures_order(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'],
                                                db_names['signal_trade_db'],
                                                pair=pair,
                                                signal=bull_signal,
                                                price=fz_feeder_cycle_last_candle['close'],
                                                trade_level=0,
                                                trade_position='long',
                                                trade_action='sell',
                                                trade_entry='limit')
                to_postman += this_data['to_postman']
                to_crystal += this_data['to_crystal']

            if bull_signal['trade_level'] == 0:  # IF BULL IS NEW
                # PLACE BUY ORDER
                this_data = place_futures_order(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'],
                                                db_names['signal_trade_db'],
                                                pair=pair,
                                                signal=bull_signal,
                                                price=fz_feeder_cycle_last_candle['close'],
                                                trade_level=1,
                                                trade_position='long',
                                                trade_action='buy',
                                                trade_entry='limit')
                to_postman += this_data['to_postman']
                to_crystal += this_data['to_crystal']

    # BEAR TRADES
    if bear_active_sma50_1day_signals:
        for bear_signal in bear_active_sma50_1day_signals:
            if bear_signal['trade_level'] == 9:  # IF BEAR IS FLAGGED
                # DEACTIVATE AND UNFLAG ALL TRADES OF SIGNAL
                trades_of_signal = get_trades_by_signal(db, db_names['signal_trade_db'], db_names['trade_db'], bear_signal['id'])
                for trade in trades_of_signal:
                    unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, db_names['trade_db'], trade)
                    to_postman += unflag_and_deactivate_trades_data['to_postman']
                    to_crystal += unflag_and_deactivate_trades_data['to_crystal']

                # PLACE SELL ORDER
                this_data = place_futures_order(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'],
                                                db_names['signal_trade_db'],
                                                pair=pair,
                                                signal=bear_signal,
                                                price=fz_feeder_cycle_last_candle['close'],
                                                trade_level=0,
                                                trade_position='short',
                                                trade_action='sell',
                                                trade_entry='limit')
                to_postman += this_data['to_postman']
                to_crystal += this_data['to_crystal']

            if bear_signal['trade_level'] == 0:  # IF BEAR IS NEW
                # # PLACE BUY ORDER
                this_data = place_futures_order(db, db_names['signal_db'], db_names['trade_db'], db_names['futures_db'],
                                                db_names['signal_trade_db'],
                                                pair=pair,
                                                signal=bear_signal,
                                                price=fz_feeder_cycle_last_candle['close'],
                                                trade_level=1,
                                                trade_position='short',
                                                trade_action='buy',
                                                trade_entry='limit')
                to_postman += this_data['to_postman']
                to_crystal += this_data['to_crystal']

# BULL&BEAR: UNFLAG AND DEACTIVATE ALL FLAGGED TRADES
    flagged_trades = fetch_flagged_trades(db, db_names['trade_db'], pair)
    if flagged_trades:
        for data in flagged_trades:
            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, db_names['trade_db'], data)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']

# BULL&BEAR: UNFLAG AND DEACTIVATE ALL FLAGGED SIGNALS
    unflag_and_deactivate_signals_data = unflag_and_deactivate_signals(db, db_names['signal_db'], pair, flagged_active_signals)
    to_postman += unflag_and_deactivate_signals_data['to_postman']
    to_crystal += unflag_and_deactivate_signals_data['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }

