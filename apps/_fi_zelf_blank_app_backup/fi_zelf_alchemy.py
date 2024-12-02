import os

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
    class fiZelfAlchemyKeysDB(db.Model):
        __tablename__ = 'app_fi_zelf_alchemy_keys_db'

        record_id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False)
        env_key = db.Column(db.String(200), nullable=False)
        env_value = db.Column(db.String(200), nullable=False)

        __table_args__ = {'extend_existing': True}

    with app.app_context():
        db.create_all()


def app_logic(current_user, db, User, GasamApp, page, return_data):
    if page == 'fi_zelf_alchemy':
        send_data = {'db_init': register_database,
                     # 'file_path_coin_gif_choice_undecided': file_path_coin_gif_choice_undecided,
                     }

        return send_data

def json_logic(current_user, db, User, GasamApp, json_data, files_data):
    if json_data['js_function'] == 'app_ini':
        return app_ini(current_user, db, User, GasamApp, json_data, files_data)
    if json_data['js_function'] == 'fz_fetcher':
        from .fz_fetcher import fz_fetcher
        return fz_fetcher(current_user, db, User, GasamApp, json_data, files_data, 'app_fi_zelf_alchemy_keys_db')


def app_ini(current_user, db, User, GasamApp, json_data, files_data):
    from main import check_and_install_requirements
    requirements_dir = os.path.join('apps', 'fi_zelf_alchemy',
                                    'fi_zelf_alchemy_requirements.txt')
    check_and_install_requirements(requirements_dir)

    return {'status': 'packages installed'}

