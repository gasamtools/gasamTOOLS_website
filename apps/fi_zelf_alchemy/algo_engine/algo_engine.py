from .vault_engine import vault_engine, get_bank_spot_values, get_bank_futures_values, fund_spot, fund_futures
from .signal_engine import signal_engine

def algo_engine(db, signal_db, trade_db, bank_db, futures_db, signal_trade_db, json_data, candle_formats, pair, command):

    to_postman, to_crystal = '', ''

    if command == 'reset_db':
        tables = [signal_trade_db, signal_db, trade_db, bank_db, futures_db]
        reset_tables_with_sequences(db, tables)
    elif command == 'get_bank_spot_values':
        return get_bank_spot_values(db, bank_db, candle_formats)
    elif command == 'get_bank_futures_values':
        return get_bank_futures_values(db, trade_db, futures_db, candle_formats)
    elif command == 'fund_spot':
        return fund_spot(db, bank_db)
    elif command == 'fund_futures':
        return fund_futures(db, trade_db, futures_db)
    elif command == 'run_engine':
        # STEP 1 vault_engine GET UPDATES ON TAKEN TRADES
            # UPDATE TRADE_DB AND NOTE CHANGES
            # UPDATE SIGNAL_DB AND NOTE CHANGES
                # IF TRADE IS LIQUIDATED, FLAG SIGNAL
            # SEND NOTES TO POSTMAN / CRYSTAL
        # ONLY CHECKS IF ORDERS ARE FILLED
        # ONLY TRIGGERS FLAGGING IF TARGET OR STOP_LOSS ARE FILLED or LIQUIDATION
        vault_engine_initial_update = vault_engine(db, signal_db, trade_db, bank_db, futures_db, signal_trade_db, 'adjust_trades', pair)
        to_postman = vault_engine_initial_update['to_postman']
        to_crystal = vault_engine_initial_update['to_crystal']

        # STEP 2 signal_engine SCAN THROUGH is_flagged SIGNALS
            # UPDATE THEM
            # NOTE CHANGES
            # if needed, UPDATE TRADES VIA vault_engine

        signal_engine_is_flagged_scan = signal_engine(db, signal_db, trade_db, 'is_flagged_scan', candle_formats, pair)
        to_postman += signal_engine_is_flagged_scan['to_postman']
        to_crystal += signal_engine_is_flagged_scan['to_crystal']

        # STEP 3 signal_engine SCAN THROUGH is_active SIGNALS, (might be redundant)
            # UPDATE THEM (move stop_loss, etc)
            # NOTE CHANGES
            # if needed, UPDATE TRADES VIA vault_engine
        signal_engine_is_active_scan = signal_engine(db, signal_db, trade_db, 'is_active_scan', candle_formats, pair)
        to_postman += signal_engine_is_active_scan['to_postman']
        to_crystal += signal_engine_is_active_scan['to_crystal']

        # STEP 4 signal_engine SCAN FOR NEW SIGNALS
            # CHECK NEW SIGNALS AGAINST RECORDED ONES SO THEY DON'T DUPLICATE
            # NOTE CHANGES
            # if needed, UPDATE TRADES VIA vault_engine
        signal_engine_data_new_scan = signal_engine(db, signal_db, trade_db, 'new_scan', candle_formats, pair)
        to_postman += signal_engine_data_new_scan['to_postman']
        to_crystal += signal_engine_data_new_scan['to_crystal']

        # STEP 5 vault_engine TAKE TRADES
        vault_engine_data_take_trade = vault_engine(db, signal_db, trade_db, bank_db, futures_db, signal_trade_db,'take_trades', pair)
        to_postman += vault_engine_data_take_trade['to_postman']
        to_crystal += vault_engine_data_take_trade['to_crystal']

        return {
            'to_postman': to_postman,
            'to_crystal': to_crystal
        }


def reset_tables_with_sequences(db, table_names):
    """
    Delete all records and reset sequences for specified tables.

    Args:
        db: SQLAlchemy database session
        table_names: List of table names to reset
    """
    from sqlalchemy import text
    # Option 1: Using TRUNCATE with RESTART IDENTITY
    # for table in table_names:
    #     db.session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))

    # Option 2: If TRUNCATE isn't suitable, use DELETE and manually reset sequences
    # def reset_sequence(table_name):
    #     # Get the sequence name (assumes standard PostgreSQL naming convention)
    #     sequence_name = f"{table_name}_id_seq"
    #     db.session.execute(text(f"ALTER SEQUENCE {sequence_name} RESTART WITH 1"))
    #
    # # Example using DELETE and manual sequence reset
    # for table in table_names:
    #     db.session.execute(text(f"DELETE FROM {table}"))
    #     reset_sequence(table)

    # Detect database type
    engine = db.session.get_bind()
    dialect = engine.dialect.name

    if dialect == 'sqlite':
        # SQLite approach
        for table in table_names:
            db.session.execute(text(f"DELETE FROM {table}"))

    elif dialect == 'postgresql':
        # PostgreSQL approach
        for table in table_names:
            db.session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))

    else:
        raise ValueError(f"Unsupported database dialect: {dialect}")

    db.session.commit()

