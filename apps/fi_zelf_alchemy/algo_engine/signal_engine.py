def signal_engine(db, signal_db, trade_db, action, candle_formats, pair):
    if action == 'is_flagged_scan':
        return signal_is_flagged_scan(db, signal_db, trade_db, candle_formats, pair)
    if action == 'is_active_scan':
        return signal_is_active_scan(db, signal_db, trade_db, candle_formats, pair)
    if action == 'new_scan':
        return signal_new_scan(db, signal_db, trade_db, candle_formats, pair)



def signal_is_flagged_scan(db, signal_db, trade_db, candle_formats, pair):
    to_postman = 'signal_is_flagged_scan | '
    to_crystal = '<p>signal_is_flagged_scan |</p>'
    # UPDATE is_flagged SIGNALS
    # NOTE CHANGES
    # if needed, UPDATE TRADES VIA vault_engine

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }

def signal_is_active_scan(db, signal_db, trade_db, candle_formats, pair):
    to_postman = 'signal_is_active_scan | '
    to_crystal = '<p>signal_is_active_scan | </p>'
    # UPDATE is_active SIGNALS (move stop_loss, etc)
    # NOTE CHANGES
    # if needed, UPDATE TRADES VIA vault_engine

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }

def signal_new_scan(db, signal_db, trade_db, candle_formats, pair):
    from .signal_cards.sma50 import sma50
    from .signal_cards.litmus import litmus
    to_postman = 'signal_new_scan | '
    to_crystal = '<p>signal_new_scan | </p>'

    # CHECK NEW SIGNALS AGAINST RECORDED ONES SO THEY DON'T DUPLICATE
    # NOTE CHANGES

# TYPES OF SIGNALS
    #0 LITMUS
    # litmus_data = litmus(db, signal_db, candle_formats, pair)
    # to_postman += litmus_data['to_postman']
    # to_crystal += litmus_data['to_crystal']

    #1 SMA50
    sma50_data = sma50(db, signal_db, candle_formats, pair)
    to_postman += sma50_data['to_postman']
    to_crystal += sma50_data['to_crystal']



    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


