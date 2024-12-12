from sqlalchemy.sql import text

def printSignals(db, signal_db, trade_db, signal_trade_db, json_data):
    from .algo_engine.signal_engine import signal_data_for_crystal
    return_data = {}
    if json_data['crystalSignalcommand'] == 'false':
        return return_data
    else:
        # GET TRADES OF SIGNAL DATA
        from .algo_engine.trade_cards._common_functions import get_trade_ids_by_signal, get_trades_by_trade_id
        trade_ids_of_signal = get_trade_ids_by_signal(db, signal_trade_db, json_data['crystalSignalID'])
        trades_of_signal = get_trades_by_trade_id(db, trade_db, trade_ids_of_signal)
        filled_trades_of_signal = [dict(trade) for trade in trades_of_signal if trade['trade_status'] == 'filled']
        # print(filled_trades_of_signal)

        # GET SIGNAL DATA
        signal_data = fetch_signal_by_id(db, signal_db, json_data['crystalSignalID'])

        # SEND DATA
        if 'signal_type' in signal_data:
            if signal_data['signal_type'] == 'SMA50':
                sma50_1day_data = signal_data_for_crystal[signal_data['signal_type']]
                return_data['signal_type'] = signal_data['signal_type']
                return_data['ma_data'] = sma50_1day_data
                return_data['trend_type'] = signal_data['trend_type']
                return_data['sdp_0'] = signal_data['sdp_0']
                return_data['sdp_1'] = signal_data['sdp_1']
                return_data['trades'] = filled_trades_of_signal

        return return_data


def fetch_signal_by_id(db, signal_db, signal_id):
    # Query to fetch the signal based on the provided ID
    if signal_id:
        query = text(f"""
            SELECT *
            FROM {signal_db}
            WHERE id = :signal_id
        """)

        # Execute the query
        result = db.session.execute(query, {"signal_id": signal_id}).mappings().first()

        return result
    else:
        return None

