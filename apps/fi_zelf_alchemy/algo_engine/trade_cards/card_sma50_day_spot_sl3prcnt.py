from ._common_functions import *
from._common_functions_spot import *
from._common_functions_futures import *

def card_sma50_day_spot_sl3prcnt(db, signal_db, trade_db, bank_db, signal_trade_db, pair, command):
    if command == 'adjust_trades':
        return adjust_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair)
    elif command == 'take_trades':
        return take_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair)


def adjust_trades(db, signal_db, trade_db, bank_db, signal_trade_db, pair):
    from ...fz_feeder import fz_feeder_cycle_last_candle
    to_postman, to_crystal = '', ''

    # 2 order is filled via vault_engine_initial_update = vault_engine('initial_update')
    flagged_trades_data = fetch_flagged_trades(db, trade_db)
    if flagged_trades_data:
        for data in flagged_trades_data:
            if data['trade_action'] == 'buy' and data['trade_status'] == 'filled':

                # PLACE STOP LOSS
                stop_price = data['price'] - (data['price'] * 0.03)  # Subtract 3% of the value

                # check available funds and place 100% for stop loss
                currency_sell_balance = fetch_bank_currency_balance_spot(db, bank_db, data['currency_buy'])

                place_stop_loss_order_data = place_new_order_spot(db=db, signal_db=signal_db, trade_db=trade_db,
                                                                  bank_db=bank_db, signal_trade_db=signal_trade_db,
                                                                  trade_id=data['trade_id'], signal='',
                                                                  price=stop_price, amount_in=currency_sell_balance,
                                                                  trade_type='spot', trade_position='long',
                                                                  trade_action='sell', trade_entry='stop-limit',
                                                                  trade_entry_stop=stop_price,
                                                                  currency_buy=data['currency_sell'],
                                                                  currency_sell=data['currency_buy'],
                                                                  tdp_0=fz_feeder_cycle_last_candle['time'])
                to_postman += place_stop_loss_order_data['to_postman']
                to_crystal += place_stop_loss_order_data['to_crystal']

            unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, trade_db, data)
            to_postman += unflag_and_deactivate_trades_data['to_postman']
            to_crystal += unflag_and_deactivate_trades_data['to_crystal']


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

        currency_sell_balance = fetch_bank_currency_balance_spot(db, bank_db, currency_sell)

        # ESTABLISH TRADE ID
        new_trade_id = get_new_trade_id(db, trade_db)

        place_new_order_data = place_new_order_spot(db=db, signal_db=signal_db, trade_db=trade_db, bank_db=bank_db,
                                                    signal_trade_db=signal_trade_db, trade_id=new_trade_id,
                                                    signal=not_traded_sma50_bull_day_signals[0],
                                                    price=not_traded_sma50_bull_day_signals[0]['tp_entrance_1'],
                                                    amount_in=currency_sell_balance, trade_type='spot',
                                                    trade_position='long', trade_action='buy', trade_entry='limit',
                                                    currency_buy=currency_buy, currency_sell=currency_sell)
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

        currency_sell_balance = fetch_bank_currency_balance_spot(db, bank_db, currency_sell)
        stoplimit_trades_data = fetch_stoplimit_trades(db, trade_db)

        # UNFLAG AND DEACTIVATE STOP LIMIT ORDERS
        if stoplimit_trades_data:
            for data in stoplimit_trades_data:
                unflag_and_deactivate_trades_data = unflag_and_deactivate_trade(db, trade_db, data)
                to_postman += unflag_and_deactivate_trades_data['to_postman']
                to_crystal += unflag_and_deactivate_trades_data['to_crystal']


        # PLACE NEW SELL TRADE
        new_trade_id = get_new_trade_id(db, trade_db)

        place_new_order_data = place_new_order_spot(db=db, signal_db=signal_db, trade_db=trade_db, bank_db=bank_db,
                                                    signal_trade_db=signal_trade_db, trade_id=new_trade_id,
                                                    signal=flagged_sma50_day_bull_signals[0],
                                                    price=not_traded_sma50_bear_day_signals[0]['tp_entrance_1'],
                                                    amount_in=currency_sell_balance, trade_type='spot',
                                                    trade_position='long', trade_action='sell', trade_entry='limit',
                                                    currency_buy=currency_buy, currency_sell=currency_sell)
        to_postman += place_new_order_data['to_postman']
        to_crystal += place_new_order_data['to_crystal']

    unflag_and_deactivate_signals_data = unflag_and_deactivate_signals(db, signal_db, pair, flagged_signals)
    to_postman += unflag_and_deactivate_signals_data['to_postman']
    to_crystal += unflag_and_deactivate_signals_data['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }