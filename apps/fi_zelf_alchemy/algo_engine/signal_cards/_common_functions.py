def fetch_from_db(db, signal_db, trading_pair, interval, signal_type):
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

def insert_into_signal_db(db, signal_db, new_proxy):
    from sqlalchemy import text
    from datetime import datetime
    import pytz

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
            "is_trend_valid": True,
        } | new_proxy

        keys_string = ', '.join(new_proxy.keys())
        keys_value_string = ', :'.join(new_proxy.keys())

        # print(f"data_values {data_values}")
        # print(f'keys_string {keys_string}')
        # print(f'keys_value_string {keys_value_string}')

        result = db.session.execute(
            text(
                f"INSERT INTO {signal_db} (is_active, date_added, is_trend_valid, {keys_string}) "
                f"VALUES (:is_active, :date_added, :is_trend_valid, :{keys_value_string})"
            ), data_values)

        # Commit the session
        db.session.commit()

        # Get the last inserted ID
        inserted_id = result.lastrowid

        # Prepare the messages
        to_postman += (
            f"NEW {new_proxy['signal_type']} SIGNAL! {new_proxy['trading_pair']} / {new_proxy['interval']}. "
            f"Confirmed Trend: {new_proxy['trend_type']}! Trend started on: {date_utc}")
        to_crystal += (
            f"<p><a class='fz crystal' id='{inserted_id}'>NEW {new_proxy['signal_type']} SIGNAL!</a> {new_proxy['trading_pair']} / {new_proxy['interval']}.<br>"
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

    to_postman += (f"INVALIDATED {record_proxy["signal_type"]} SIGNAL! {record_proxy["trading_pair"]} / {record_proxy["interval"]}. "
                   f"Invalidated Trend: {record_proxy["trend_type"]}! Trend ended on: {date_utc}")
    to_crystal += (
        f"<p><a class='fz crystal' id='{record_proxy["id"]}'>INVALIDATED {record_proxy["signal_type"]} SIGNAL!</a> {record_proxy["trading_pair"]} / {record_proxy["interval"]}.<br>"
        f"Invalidated Trend: {record_proxy["trend_type"]}! Trend ended on: {date_utc}</p>")

    return {
        'to_postman': to_postman,
        'to_crystal': to_crystal
    }


