from ._common_functions import *


def card_litmus(db, signal_db, trade_db, bank_db, signal_trade_db, pair):

    to_postman, to_crystal = '', ''

    #NEW SIGNALS SECTION
    not_traded_signals = fetch_not_traded_signals(db, signal_db, signal_trade_db, pair)
    not_traded_litmus_signals = [signal for signal in not_traded_signals if signal['signal_type'] == 'litmus']

    if not_traded_litmus_signals:
        currency_buy = pair.split('-')[0]
        currency_sell = pair.split('-')[1]

        # ESTABLISH TRADE ID
        new_trade_id = get_new_trade_id(db, trade_db)

        place_new_order_data = place_new_order_spot(db=db, signal_db=signal_db, trade_db=trade_db, bank_db=bank_db,
                                                    signal_trade_db=signal_trade_db, trade_id=new_trade_id,
                                                    signal=not_traded_litmus_signals[0],
                                                    price=not_traded_litmus_signals[0]['tp_entrance_1'], amount_in=1000,
                                                    trade_type='spot', trade_position='long', trade_action='buy',
                                                    trade_entry='limit', currency_buy=currency_buy,
                                                    currency_sell=currency_sell)
        to_postman += place_new_order_data['to_postman']
        to_crystal += place_new_order_data['to_crystal']


    # FLAGGED SIGNALS SECTION
    flagged_signals = fetch_flagged_signals(db, signal_db, pair)
    unflag_and_deactivate_signals_data = unflag_and_deactivate_signals(db, signal_db, pair, flagged_signals)
    to_postman += unflag_and_deactivate_signals_data['to_postman']
    to_crystal += unflag_and_deactivate_signals_data['to_crystal']

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }
