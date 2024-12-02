# fi_tradingview_lightweight_charts
import os
from datetime import datetime, timedelta
from .functions_fetch_kucoin_data import fetch_kucoin_data
from .functions_indicators import calculate_moving_average_series_data, calculate_market_structure_series_data, calculate_time_mode_main
from sqlalchemy import text


def register_subpages(current_user):
    if current_user.role == 'admin':
        app_subpages = [
            {'html_name': 'app_keys',
             'title': 'App Keys'
             }
        ]
    else:
        app_subpages = []

    return app_subpages


def register_database(db, app):
    class fiTradingViewLightweightDB(db.Model):
        __tablename__ = 'app_fi_tradingview_lightweight_db'

        record_id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False)
        env_key = db.Column(db.String(200), nullable=False)
        env_value = db.Column(db.String(200), nullable=False)

        __table_args__ = {'extend_existing': True}

    with app.app_context():
        db.create_all()


def app_logic(current_user, db, User, GasamApp, page, return_data):
    if page == 'fi_tradingview_lightweight_charts':
        send_data = {'db_init': register_database,
                     # 'file_path_coin_gif_choice_undecided': file_path_coin_gif_choice_undecided,
                     }

        return send_data


def json_logic(current_user, db, User, GasamApp, json_data, files_data):
    if json_data['js_function'] == 'fi_tradingview_lightweight_charts_ini':
        return fi_tradingview_lightweight_charts_ini(current_user, db, User, GasamApp, json_data, files_data)
    if json_data['js_function'] == 'fi_tradingview_lightweight_charts_load':
        return fi_tradingview_lightweight_charts_load(current_user, db, User, GasamApp, json_data, files_data)
    if json_data['js_function'] == 'fi_tradingview_lightweight_api_keys':
        return fi_tradingview_lightweight_api_keys(current_user, db, User, GasamApp, json_data, files_data)


def fi_tradingview_lightweight_charts_ini(current_user, db, User, GasamApp, json_data, files_data):
    from main import check_and_install_requirements
    requirements_dir = os.path.join('apps', 'fi_tradingview_lightweight_charts',
                                    'fi_tradingview_lightweight_charts_requirements.txt')
    check_and_install_requirements(requirements_dir)

    return {'status': 'packages installed'}


def fi_tradingview_lightweight_charts_load(current_user, db, User, GasamApp, json_data, files_data):
    import pytz

    KC_API_KEY = get_env_value_from_env_or_db(db, 'KC_API_KEY')
    KC_API_SECRET = get_env_value_from_env_or_db(db, 'KC_API_SECRET')
    KC_API_PASSPHRASE = get_env_value_from_env_or_db(db, 'KC_API_PASSPHRASE')

    end_time = datetime.now(pytz.UTC)
    start_time = end_time - timedelta(days=int(json_data['daysOfData']))  # Fetch last 7 days of data

    candle_data = fetch_kucoin_data(json_data['tradingPair'], start_time, end_time, json_data['chartResolution'], KC_API_KEY,
                                    KC_API_SECRET, KC_API_PASSPHRASE)
    candle_data_1day = fetch_kucoin_data(json_data['tradingPair'], start_time, end_time, '1day', KC_API_KEY, KC_API_SECRET,
                                         KC_API_PASSPHRASE)
    candle_data_1week = fetch_kucoin_data(json_data['tradingPair'], start_time, end_time, '1week', KC_API_KEY, KC_API_SECRET,
                                          KC_API_PASSPHRASE)

# APPLYING INDICATORS
    # 50SMA DATA
    ma_data_1day_last = calculate_moving_average_series_data(candle_data_1day, 50)[-1]
    ma_data_1week_last = calculate_moving_average_series_data(candle_data_1week, 50)[-1]
    ma_data = calculate_moving_average_series_data(candle_data, 50)

    # MS DATA
    ms_1day_bull = calculate_market_structure_series_data(candle_data_1day, 'bull')
    ms_1day_bear = calculate_market_structure_series_data(candle_data_1day, 'bear')
    ms_1week_bull = calculate_market_structure_series_data(candle_data_1week, 'bull')
    ms_1week_bear = calculate_market_structure_series_data(candle_data_1week, 'bear')

    # TM DATA
    tm_1day_exp = calculate_time_mode_main(candle_data_1day)
    tm_1week_exp = calculate_time_mode_main(candle_data_1week)
    tm_1day_mode = calculate_time_mode_main(candle_data_1day)
    tm_1week_mode = calculate_time_mode_main(candle_data_1week)

    # POSTMAN MESSAGE
    postman = f'Pair: {json_data['tradingPair']}'

    postman_crystal = (
        f"<h4>Pair: {json_data['tradingPair']}</h4>"
        f"<h6>SMA</h6>"
        f"<div>DAY: {ma_data_1day_last}, WEEK: {ma_data_1week_last}</div"
    )


    aggregate_data = {
        'candle_data': candle_data,
        'postman': postman,
        'postman_crystal': postman_crystal,
        'ma_data': ma_data,
        'ma_1day_last': ma_data_1day_last,
        'ma_1week_last': ma_data_1week_last,
        'ms_1day_bull': ms_1day_bull,
        'ms_1day_bear': ms_1day_bear,
        'ms_1week_bull': ms_1week_bull,
        'ms_1week_bear': ms_1week_bear,
        'tm_1day_exp': tm_1day_exp,
        'tm_1week_exp': tm_1week_exp,
        'tm_1day_mode': tm_1day_mode,
        'tm_1week_mode': tm_1week_mode,
    }

    return aggregate_data


def fi_tradingview_lightweight_api_keys(current_user, db, User, GasamApp, json_data, files_data):

    if current_user.role == 'admin':
        kc_api_key = get_or_update_env_db(current_user, db, 'KC_API_KEY', json_data)
        kc_api_secret = get_or_update_env_db(current_user, db, 'KC_API_SECRET', json_data)
        kc_api_passphrase = get_or_update_env_db(current_user, db, 'KC_API_PASSPHRASE', json_data)

        return {
            'KC_API_KEY': kc_api_key,
            'KC_API_SECRET': kc_api_secret,
            'KC_API_PASSPHRASE': kc_api_passphrase
        }
    else:
        return {
            'KC_API_KEY': '',
            'KC_API_SECRET': '',
            'KC_API_PASSPHRASE': ''
        }



def get_env_value_from_env_or_db(db, env_key):
    if os.getenv(env_key):
        env_value = os.getenv(env_key)
    else:
        results = db.session.execute(
            text("SELECT env_value FROM app_fi_tradingview_lightweight_db WHERE env_key=:env_key"),
            {"env_key": env_key})
        env_value = results.scalar()

    return env_value


def get_or_update_env_db(current_user, db, env_key, json_data):

    if env_key in json_data:
        env_value = json_data[env_key].strip()
    else:
        env_value = None

    if env_value:

        # Check if the user_id already exists
        existing_record = db.session.execute(
            text("SELECT * FROM app_fi_tradingview_lightweight_db WHERE env_key = :env_key"),
            {"env_key": env_key}
        ).fetchone()

        if existing_record:

            db.session.execute(
                text("UPDATE app_fi_tradingview_lightweight_db SET env_value = :env_value WHERE env_key = :env_key"),
                {"env_value": env_value, "env_key": env_key}
            )
        else:
            # User does not exist, insert a new record
            db.session.execute(
                text("INSERT INTO app_fi_tradingview_lightweight_db (user_id, env_key, env_value) VALUES (:user_id, "
                     ":env_key, :env_value)"),
                {"user_id": current_user.id, "env_key": env_key, "env_value": env_value}
            )

        db.session.commit()

    results = db.session.execute(
        text("SELECT env_value FROM app_fi_tradingview_lightweight_db WHERE env_key=:env_key"),
        {"env_key": env_key})
    return results.scalar()

