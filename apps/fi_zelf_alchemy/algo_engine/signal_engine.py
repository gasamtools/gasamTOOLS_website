signal_data_for_crystal = {}


def signal_engine(db, signal_db, trade_db, action, candle_formats, pair):
    if action == 'is_flagged_scan':
        return signal_is_flagged_scan(db, signal_db, trade_db, candle_formats, pair)
    if action == 'is_active_scan':
        return signal_is_active_scan(db, signal_db, trade_db, candle_formats, pair)
    if action == 'new_scan':
        return signal_new_scan(db, signal_db, trade_db, candle_formats, pair)



def signal_is_flagged_scan(db, signal_db, trade_db, candle_formats, pair):
    to_postman, to_crystal = '', ''
    # UPDATE is_flagged SIGNALS
    # NOTE CHANGES
    # if needed, UPDATE TRADES VIA vault_engine

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }

def signal_is_active_scan(db, signal_db, trade_db, candle_formats, pair):
    to_postman, to_crystal = '', ''
    # UPDATE is_active SIGNALS (move stop_loss, etc)
    # NOTE CHANGES
    # if needed, UPDATE TRADES VIA vault_engine

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }

def signal_new_scan(db, signal_db, trade_db, candle_formats, pair):

    from .signal_cards.litmus import litmus
    global signal_data_for_crystal
    to_postman, to_crystal = '',''

    # CHECK NEW SIGNALS AGAINST RECORDED ONES SO THEY DON'T DUPLICATE
    # NOTE CHANGES

# TYPES OF SIGNALS
    #0 LITMUS
    # litmus_data = litmus(db, signal_db, candle_formats, pair)
    # to_postman += litmus_data['to_postman']
    # to_crystal += litmus_data['to_crystal']

    # 1 SMA50
    # from .signal_cards.sma50 import sma50
    # sma50_data = sma50(db, signal_db, candle_formats, pair)
    # to_postman += sma50_data['to_postman']
    # to_crystal += sma50_data['to_crystal']
    # signal_data_for_crystal['SMA50'] = sma50_data['new_1day']

    # 2 signal_sma50_0001_prev_and_open
    # from .signal_cards.signal_sma50_0001_prev_and_open import signal_sma50_0001_prev_and_open
    # sma50_data = signal_sma50_0001_prev_and_open(db, signal_db, candle_formats, pair)
    # to_postman += sma50_data['to_postman']
    # to_crystal += sma50_data['to_crystal']
    # signal_data_for_crystal['SMA50'] = sma50_data['new_1day']

    # 3 signal_sma50_0001_prev_and_open
    from .signal_cards.signal_sma50_0002_prev_and_open_v2 import signal_sma50_0002_prev_and_open_v2
    sma50_data = signal_sma50_0002_prev_and_open_v2(db, signal_db, candle_formats, pair)
    to_postman += sma50_data['to_postman']
    to_crystal += sma50_data['to_crystal']
    signal_data_for_crystal['SMA50'] = sma50_data['new_1day']




    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


