

def register_subpages(current_user):
    if current_user.role == 'admin':
        app_subpages = []
    else:
        app_subpages = []

    return app_subpages


def register_database(db, app):
    pass


def app_logic(current_user, db, User, GasamApp, page, return_data):
    if page == 'game_breakout':
        send_data = {'db_init': register_database,
                     # 'file_path_coin_gif_choice_undecided': file_path_coin_gif_choice_undecided,
                     }

        return send_data


def json_logic(current_user, db, User, GasamApp, json_data, files_data):
    if json_data['js_function'] == 'game_breakout_ini':
        return js_function_game_breakout_ini(current_user, db, User, GasamApp, json_data, files_data)


def js_function_game_breakout_ini(current_user, db, User, GasamApp, json_data, files_data):
    return json_data