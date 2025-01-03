import os
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Table, ForeignKey

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


# def register_database(db, app):
#
#     # Recreate the association table
#     # app_fi_zelf_association_signal_trade = db.Table(
#     #     'app_fi_zelf_association_signal_trade',
#     #     db.Column('signal_id', db.Integer, db.ForeignKey('app_fi_zelf_alchemy_signal_db.id'), primary_key=True),
#     #     db.Column('trade_id', db.Integer, db.ForeignKey('app_fi_zelf_alchemy_trade_db.trade_id'), primary_key=True),
#     #     extend_existing=True
#     # )
#
#     # Recreate the association table with the primary key being both columns together
#     app_fi_zelf_association_signal_trade = db.Table(
#         'app_fi_zelf_association_signal_trade',
#         db.Column('signal_id', db.Integer, db.ForeignKey('app_fi_zelf_alchemy_signal_db.id')),
#         db.Column('trade_id', db.Integer, db.ForeignKey('app_fi_zelf_alchemy_trade_db.id')),
#         db.PrimaryKeyConstraint('signal_id', 'trade_id'),  # Composite primary key
#         extend_existing=True
#     )
#
#     class fiZelfAlchemyKeysDB(db.Model):
#         __tablename__ = 'app_fi_zelf_alchemy_keys_db'
#
#         record_id = db.Column(db.Integer, primary_key=True)
#         user_id = db.Column(db.Integer, nullable=False)
#         env_key = db.Column(db.String(200), nullable=False)
#         env_value = db.Column(db.String(200), nullable=False)
#
#         __table_args__ = {'extend_existing': True}
#
#     class fiZelfAlchemyTestPairDB(db.Model):
#         __tablename__ = 'app_fi_zelf_alchemy_testPair_db'
#
#         record_id = db.Column(db.Integer, primary_key=True)
#         pair_id = db.Column(db.String(200), nullable=False)
#         time = db.Column(db.Integer, nullable=False)
#         open = db.Column(db.Float, nullable=False)
#         high = db.Column(db.Float, nullable=False)
#         low = db.Column(db.Float, nullable=False)
#         close = db.Column(db.Float, nullable=True)
#         volume = db.Column(db.Float, nullable=True)
#         notes = db.Column(db.String(200), nullable=True)
#
#         __table_args__ = {'extend_existing': True}
#
#     class fiZelfAlchemySignalDB(db.Model):
#         __tablename__ = "app_fi_zelf_alchemy_signal_db"
#
#         id = db.Column(db.Integer, primary_key=True)
#         is_active = db.Column(db.Boolean, nullable=False)
#         is_flagged = db.Column(db.Boolean, nullable=True)
#         date_added = db.Column(db.Integer, nullable=False)
#         date_closed = db.Column(db.Integer, nullable=True)
#         trading_pair = db.Column(db.String(100), nullable=False)
#         interval = db.Column(db.String(100), nullable=False)
#         signal_type = db.Column(db.String(1000), nullable=False)
#         is_trend_valid = db.Column(db.Boolean, nullable=True)
#         trend_type = db.Column(db.String(100), nullable=True)
#         tp_entrance_1 = db.Column(db.Float, nullable=True)
#         tp_entrance_2 = db.Column(db.Float, nullable=True)
#         tp_entrance_3 = db.Column(db.Float, nullable=True)
#         tp_entrance_4 = db.Column(db.Float, nullable=True)
#         tp_entrance_5 = db.Column(db.Float, nullable=True)
#         tp_exit_1 = db.Column(db.Float, nullable=True)
#         tp_exit_2 = db.Column(db.Float, nullable=True)
#         tp_exit_3 = db.Column(db.Float, nullable=True)
#         tp_exit_4 = db.Column(db.Float, nullable=True)
#         tp_exit_5 = db.Column(db.Float, nullable=True)
#         tp_stoploss_1 = db.Column(db.Float, nullable=True)
#         tp_stoploss_2 = db.Column(db.Float, nullable=True)
#         tp_stoploss_3 = db.Column(db.Float, nullable=True)
#         sdp_0 = db.Column(db.Text, nullable=True)
#         sdp_1 = db.Column(db.Text, nullable=True)
#         sdp_2 = db.Column(db.Text, nullable=True)
#         sdp_3 = db.Column(db.Text, nullable=True)
#         sdp_4 = db.Column(db.Text, nullable=True)
#         sdp_5 = db.Column(db.Text, nullable=True)
#         sdp_6 = db.Column(db.Text, nullable=True)
#         sdp_7 = db.Column(db.Text, nullable=True)
#         sdp_8 = db.Column(db.Text, nullable=True)
#         sdp_9 = db.Column(db.Text, nullable=True)
#         trades = relationship("fiZelfAlchemyTradeDB", secondary=app_fi_zelf_association_signal_trade, back_populates="signals")
#
#         __table_args__ = {'extend_existing': True}
#
#     class fiZelfAlchemyTradeDB(db.Model):
#         __tablename__ = "app_fi_zelf_alchemy_trade_db"
#
#         id = db.Column(db.Integer, primary_key=True)
#         trade_id = db.Column(db.Integer, nullable=False, index=True)
#         is_active = db.Column(db.Boolean, nullable=False)
#         is_flagged = db.Column(db.Boolean, nullable=True)
#         trade_status = db.Column(db.String(100), nullable=False)
#         trade_type = db.Column(db.String(100), nullable=False)  # spot, futures
#         trade_position = db.Column(db.String(100), nullable=False) # long/short
#         trade_action = db.Column(db.String(100), nullable=False) # buy/sell
#         trade_entry = db.Column(db.String(100), nullable=False) # limit, market, stop limit
#         trade_entry_stop = db.Column(db.Float, nullable=True)  # stoploss trigger price
#         date_placed = db.Column(db.Integer, nullable=False)
#         date_filled = db.Column(db.Integer, nullable=True)
#         currency_buy = db.Column(db.String(100), nullable=False)
#         currency_sell = db.Column(db.String(100), nullable=False)
#         amount_buy = db.Column(db.Float, nullable=False)
#         amount_sell = db.Column(db.Float, nullable=False)
#         price = db.Column(db.Float, nullable=True)
#         tdp_0 = db.Column(db.Text, nullable=True)
#         tdp_1 = db.Column(db.Text, nullable=True)
#         tdp_2 = db.Column(db.Text, nullable=True)
#         tdp_3 = db.Column(db.Text, nullable=True)
#         signals = relationship("fiZelfAlchemySignalDB", secondary=app_fi_zelf_association_signal_trade, back_populates="trades")
#
#         __table_args__ = {'extend_existing': True}
#
#     class fiZelfAlchemyBankDB(db.Model):
#         __tablename__ = "app_fi_zelf_alchemy_bank_db"
#
#         id = db.Column(db.Integer, primary_key=True)
#         currency = db.Column(db.String(100), nullable=False)
#         amount = db.Column(db.Float, nullable=False)
#
#         __table_args__ = {'extend_existing': True}
#
#
#     class fiZelfAlchemyFuturesDB(db.Model):
#         __tablename__ = "app_fi_zelf_alchemy_futures_db"
#
#         id = db.Column(db.Integer, primary_key=True)
#         currency = db.Column(db.String(100), nullable=False)
#         amount = db.Column(db.Float, nullable=False)
#         pnl = db.Column(db.Float, nullable=True)
#         trade_id = db.Column(db.Integer, nullable=True)
#         trade_position = db.Column(db.String(100), nullable=True)
#
#         __table_args__ = {'extend_existing': True}
#
#     with app.app_context():
#         db.create_all()

def register_database(db, app):
    # Define association table using Flask-SQLAlchemy syntax
    app_fi_zelf_association_signal_trade = db.Table(
        'app_fi_zelf_association_signal_trade',
        db.Model.metadata,
        db.Column('signal_id', db.Integer, db.ForeignKey('app_fi_zelf_alchemy_signal_db.id')),
        db.Column('trade_id', db.Integer, db.ForeignKey('app_fi_zelf_alchemy_trade_db.id')),
        extend_existing=True
    )

    class fiZelfAlchemySignalDB(db.Model):
        __tablename__ = "app_fi_zelf_alchemy_signal_db"

        id = db.Column(db.Integer, primary_key=True)
        is_active = db.Column(db.Boolean, nullable=False)
        is_flagged = db.Column(db.Boolean, nullable=True)
        trade_level = db.Column(db.Integer, nullable=True)
        date_added = db.Column(db.Integer, nullable=False)
        date_closed = db.Column(db.Integer, nullable=True)
        trading_pair = db.Column(db.String(100), nullable=False)
        interval = db.Column(db.String(100), nullable=False)
        signal_type = db.Column(db.String(1000), nullable=False)
        is_trend_valid = db.Column(db.Boolean, nullable=True)
        trend_type = db.Column(db.String(100), nullable=True)
        tp_entrance_1 = db.Column(db.Float, nullable=True)
        tp_entrance_2 = db.Column(db.Float, nullable=True)
        tp_entrance_3 = db.Column(db.Float, nullable=True)
        tp_entrance_4 = db.Column(db.Float, nullable=True)
        tp_entrance_5 = db.Column(db.Float, nullable=True)
        tp_exit_1 = db.Column(db.Float, nullable=True)
        tp_exit_2 = db.Column(db.Float, nullable=True)
        tp_exit_3 = db.Column(db.Float, nullable=True)
        tp_exit_4 = db.Column(db.Float, nullable=True)
        tp_exit_5 = db.Column(db.Float, nullable=True)
        tp_stoploss_1 = db.Column(db.Float, nullable=True)
        tp_stoploss_2 = db.Column(db.Float, nullable=True)
        tp_stoploss_3 = db.Column(db.Float, nullable=True)
        sdp_0 = db.Column(db.Text, nullable=True)
        sdp_1 = db.Column(db.Text, nullable=True)
        sdp_2 = db.Column(db.Text, nullable=True)
        sdp_3 = db.Column(db.Text, nullable=True)
        sdp_4 = db.Column(db.Text, nullable=True)
        sdp_5 = db.Column(db.Text, nullable=True)
        sdp_6 = db.Column(db.Text, nullable=True)
        sdp_7 = db.Column(db.Text, nullable=True)
        sdp_8 = db.Column(db.Text, nullable=True)
        sdp_9 = db.Column(db.Text, nullable=True)
        trades = db.relationship('fiZelfAlchemyTradeDB',
                               secondary=app_fi_zelf_association_signal_trade,
                               backref=db.backref('signals', lazy='dynamic'),
                               lazy='dynamic')

        __table_args__ = {'extend_existing': True}

    class fiZelfAlchemyTradeDB(db.Model):
        __tablename__ = "app_fi_zelf_alchemy_trade_db"

        id = db.Column(db.Integer, primary_key=True)
        trade_id = db.Column(db.Integer, nullable=False, index=True)
        is_active = db.Column(db.Boolean, nullable=False)
        is_flagged = db.Column(db.Boolean, nullable=True)
        trade_level = db.Column(db.Integer, nullable=True)
        trade_status = db.Column(db.String(100), nullable=False)
        trade_type = db.Column(db.String(100), nullable=False)
        trade_position = db.Column(db.String(100), nullable=False)
        trade_action = db.Column(db.String(100), nullable=False)
        trade_entry = db.Column(db.String(100), nullable=False)
        trade_entry_stop = db.Column(db.Float, nullable=True)
        date_placed = db.Column(db.Integer, nullable=False)
        date_filled = db.Column(db.Integer, nullable=True)
        currency_buy = db.Column(db.String(100), nullable=False)
        currency_sell = db.Column(db.String(100), nullable=False)
        amount_buy = db.Column(db.Float, nullable=False)
        amount_sell = db.Column(db.Float, nullable=False)
        price = db.Column(db.Float, nullable=True)
        tdp_0 = db.Column(db.Text, nullable=True)
        tdp_1 = db.Column(db.Text, nullable=True)
        tdp_2 = db.Column(db.Text, nullable=True)
        tdp_3 = db.Column(db.Text, nullable=True)

        __table_args__ = {'extend_existing': True}

    class fiZelfAlchemyKeysDB(db.Model):
        __tablename__ = 'app_fi_zelf_alchemy_keys_db'

        record_id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False)
        env_key = db.Column(db.String(200), nullable=False)
        env_value = db.Column(db.String(200), nullable=False)

        __table_args__ = {'extend_existing': True}

    class fiZelfAlchemyTestPairDB(db.Model):
        __tablename__ = 'app_fi_zelf_alchemy_testpair_db'

        record_id = db.Column(db.Integer, primary_key=True)
        pair_id = db.Column(db.String(200), nullable=False)
        time = db.Column(db.Integer, nullable=False)
        open = db.Column(db.Float, nullable=False)
        high = db.Column(db.Float, nullable=False)
        low = db.Column(db.Float, nullable=False)
        close = db.Column(db.Float, nullable=True)
        volume = db.Column(db.Float, nullable=True)
        notes = db.Column(db.String(200), nullable=True)

        __table_args__ = {'extend_existing': True}

    class fiZelfAlchemyBankDB(db.Model):
        __tablename__ = "app_fi_zelf_alchemy_bank_db"

        id = db.Column(db.Integer, primary_key=True)
        currency = db.Column(db.String(100), nullable=False)
        amount = db.Column(db.Float, nullable=False)

        __table_args__ = {'extend_existing': True}

    class fiZelfAlchemyFuturesDB(db.Model):
        __tablename__ = "app_fi_zelf_alchemy_futures_db"

        id = db.Column(db.Integer, primary_key=True)
        currency = db.Column(db.String(100), nullable=False)
        amount = db.Column(db.Float, nullable=False)
        pnl = db.Column(db.Float, nullable=True)
        trade_id = db.Column(db.Integer, nullable=True)
        trade_position = db.Column(db.String(100), nullable=True)

        __table_args__ = {'extend_existing': True}

    class fiZelfAlchemyCharts1DB(db.Model):
        __tablename__ = "app_fi_zelf_alchemy_charts_1_db"

        id = db.Column(db.Integer, primary_key=True)
        timestamp = db.Column(db.Integer, nullable=False)
        hodl = db.Column(db.Float, nullable=True)
        bot = db.Column(db.Float, nullable=True)
        sma = db.Column(db.Float, nullable=True)
        candle = db.Column(db.Float, nullable=True)

        __table_args__ = {'extend_existing': True}

    with app.app_context():
        db.create_all()

    return {
        'SignalDB': fiZelfAlchemySignalDB,
        'TradeDB': fiZelfAlchemyTradeDB,
        'KeysDB': fiZelfAlchemyKeysDB,
        'TestPairDB': fiZelfAlchemyTestPairDB,
        'BankDB': fiZelfAlchemyBankDB,
        'FuturesDB': fiZelfAlchemyFuturesDB
    }

def app_logic(current_user, db, User, GasamApp, page, return_data):
    if page == 'fi_zelf_alchemy':
        send_data = {'db_init': register_database,
                     # 'file_path_coin_gif_choice_undecided': file_path_coin_gif_choice_undecided,
                     }

        return send_data

def json_logic(current_user, db, User, GasamApp, json_data, files_data):
    db_names = {
        'signal_db': 'app_fi_zelf_alchemy_signal_db',
        'trade_db': 'app_fi_zelf_alchemy_trade_db',
        'bank_db': 'app_fi_zelf_alchemy_bank_db',
        'futures_db': 'app_fi_zelf_alchemy_futures_db',
        'signal_trade_db': 'app_fi_zelf_association_signal_trade',
        'testPair_db': 'app_fi_zelf_alchemy_testpair_db',
        'charts_1_db': 'app_fi_zelf_alchemy_charts_1_db',
    }


    from .fz_fetcher import fz_fetcher
    from .fz_feeder import fz_feeder
    from .algo_engine.algo_engine import algo_engine

    if json_data['js_function'] == 'app_ini':
        return app_ini(current_user, db, User, GasamApp, json_data, files_data)
    if json_data['js_function'] == 'fz_fetcher':
        # RESET ALL DBs
        algo_engine(db, db_names, json_data, {}, '', 'reset_db')
        # FETCH AND LOAD DATA TO TEST_DB
        fz_fetcher_status = fz_fetcher(current_user, db, User, GasamApp, json_data, files_data )
        # FUND SPOT BANK WITH TEST MONEY
        bank_spot_values_data = algo_engine(db, db_names, json_data, {}, '', 'fund_spot')
        # FUND FUTURES BANK WITH TEST MONEY
        bank_futures_values_data = algo_engine(db, db_names, json_data, {}, '',
                                       'fund_futures')

        # SEND DATA
        ini_data = (fz_fetcher_status |
                    {'bank_spot_values_data': bank_spot_values_data,
                     'bank_futures_values_data': bank_futures_values_data,
                     })
        return ini_data

    if json_data['js_function'] == 'fz_feeder':
        # FEED DATA TO algo_engine
        return fz_feeder(current_user, db, db_names, User, GasamApp, json_data, files_data)



def app_ini(current_user, db, User, GasamApp, json_data, files_data):
    from main import check_and_install_requirements
    requirements_dir = os.path.join('apps', 'fi_zelf_alchemy',
                                    'fi_zelf_alchemy_requirements.txt')
    check_and_install_requirements(requirements_dir)

    return {'status': 'packages installed'}

