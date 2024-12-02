from ._common_functions import *

def card__bypass(db, signal_db, trade_db, bank_db, pair):
    flagged_signals = fetch_flagged_signals(db, signal_db, pair)
    return unflag_and_deactivate_signals(db, signal_db, pair, flagged_signals)