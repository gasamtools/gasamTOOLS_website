from ..trade_cards._common_functions import timestamp_to_time_UTC


def fetch_active_from_db(db, signal_db, trading_pair, interval, signal_type):
    from sqlalchemy import text
    records_proxy = db.session.execute(
        text(
            f"SELECT * FROM {signal_db} WHERE is_active = :is_active AND interval = :interval AND trading_pair = :trading_pair AND signal_type = :signal_type"),
        {
            "is_active": True,
            "interval": interval,
            "trading_pair": trading_pair,
            "signal_type": signal_type
        }
    )
    got_back = records_proxy.mappings().fetchall()
    if got_back:
        got_back = got_back[0]

    return got_back

def fetch_all_from_db(db, signal_db, trading_pair, interval, signal_type):
    from sqlalchemy import text
    records_proxy = db.session.execute(
        text(
            f"SELECT * FROM {signal_db} WHERE interval = :interval AND trading_pair = :trading_pair AND signal_type = :signal_type"),
        {
            "interval": interval,
            "trading_pair": trading_pair,
            "signal_type": signal_type
        }
    )
    got_back = records_proxy.mappings().fetchall()

    return got_back

def insert_into_signal_db(db, signal_db, new_proxy):
    from sqlalchemy import text
    from datetime import datetime
    import pytz
    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''

    # GET  TIMESTAMP of NOW
    now = datetime.now(pytz.UTC)
    date_added = int(now.timestamp())

    # GET DATE in the format YYYY-MM-DD of trend_start
    utc_timezone = pytz.UTC
    date_object_utc = datetime.fromtimestamp(new_proxy["sdp_0"], utc_timezone)
    date_utc = date_object_utc.date()

    try:
        # Insert into database and retrieve the ID

        data_values = {
            "is_active": True,
            "date_added": date_added,
        } | new_proxy

        keys_string = ', '.join(new_proxy.keys())
        keys_value_string = ', :'.join(new_proxy.keys())

        result = db.session.execute(
            text(
                f"INSERT INTO {signal_db} (is_active, date_added,  {keys_string}) "
                f"VALUES (:is_active, :date_added, :{keys_value_string})"
            ), data_values)

        # Commit the session
        db.session.commit()

        # Get the last inserted ID
        inserted_id = result.lastrowid

        # Prepare the messages
        note_time = timestamp_to_time_UTC(fz_feeder_cycle_last_candle['time'])
        to_postman += (
            f"{note_time} #{inserted_id} NEW {new_proxy['signal_type']} SIGNAL! {new_proxy['trading_pair']} / {new_proxy['interval']}. "
            f"Confirmed Trend: {new_proxy['trend_type']}! Trend started on: {date_utc}")
        to_crystal += (
            f"<p>{note_time} <a class='fz crystal signal' id='{inserted_id}' href='#'> #{inserted_id} NEW {new_proxy['signal_type']} SIGNAL!</a> {new_proxy['trading_pair']} / {new_proxy['interval']}.<br>"
            f"Confirmed Trend: {new_proxy['trend_type']}! Trend started on: {date_utc}</p>")

    except Exception as e:
        db.session.rollback()  # Rollback if there is any error
        print(f"Error inserting into DB: {e}")

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


def flag_signal(db, signal_db, record_proxy, trend_ended):
    from sqlalchemy import text
    from datetime import datetime
    import pytz
    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''

    # GET  TIMESTAMP of NOW
    now = datetime.now(pytz.UTC)
    date_closed = int(now.timestamp())

    # GET DATE in the format YYYY-MM-DD of trend_end
    utc_timezone = pytz.UTC
    date_object_utc = datetime.fromtimestamp(trend_ended, utc_timezone)
    date_utc = date_object_utc.date()

    db.session.execute(
        text(
            f"UPDATE {signal_db} SET is_flagged = :is_flagged, date_closed = :date_closed, is_trend_valid = :is_trend_valid, sdp_1 = :sdp_1  WHERE id = :record_id"
        ),
        {"is_flagged": True,
         "is_trend_valid": False,
         "date_closed": date_closed,
         "sdp_1": trend_ended,
         "record_id": record_proxy['id']
         }
    )
    db.session.commit()

    note_time = timestamp_to_time_UTC(fz_feeder_cycle_last_candle['time'])
    to_postman += (f"{note_time} #{record_proxy['id']} INVALIDATED {record_proxy['signal_type']} SIGNAL! {record_proxy['trading_pair']} / {record_proxy['interval']}. "
                   f"Invalidated Trend: {record_proxy['trend_type']}! Trend ended on: {date_utc}")
    to_crystal += (
        f"<p>{note_time} <a class='fz crystal signal' id='{record_proxy['id']}' href='#'>#{record_proxy['id']} INVALIDATED {record_proxy['signal_type']} SIGNAL!</a> {record_proxy['trading_pair']} / {record_proxy['interval']}.<br>"
        f"Invalidated Trend: {record_proxy['trend_type']}! Trend ended on: {date_utc}</p>")

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }

def reactivate_signal(db, signal_db, record_proxy):
    from sqlalchemy import text
    from ...fz_feeder import fz_feeder_cycle_last_candle

    to_postman, to_crystal = '', ''

    db.session.execute(
        text(
            f"UPDATE {signal_db} SET is_active = :is_active, is_trend_valid = :is_trend_valid, date_closed = :date_closed, sdp_1 = :sdp_1  WHERE id = :record_id"
        ),
        {"is_active": True,
         "is_trend_valid": True,
         "date_closed": None,
         "sdp_1": None,
         "record_id": record_proxy['id']
         }
    )
    db.session.commit()

    note_time = timestamp_to_time_UTC(fz_feeder_cycle_last_candle['time'])
    trend_started = timestamp_to_time_UTC(record_proxy["sdp_0"])
    to_postman += (f"{note_time} #{record_proxy['id']} REVALIDATED {record_proxy['signal_type']} SIGNAL! {record_proxy['trading_pair']} / {record_proxy['interval']}. "
                   f"Trend: {record_proxy['trend_type']}! Trend started on: {trend_started}")
    to_crystal += (
        f"<p>{note_time} <a class='fz crystal signal' id='{record_proxy['id']}' href='#'>#{record_proxy['id']} REVALIDATED {record_proxy['signal_type']} SIGNAL!</a> {record_proxy['trading_pair']} / {record_proxy['interval']}.<br>"
        f"Trend: {record_proxy['trend_type']}! Trend started on: {trend_started}</p>")

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


