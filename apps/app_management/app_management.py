from sqlalchemy import text

def register_subpages():
    app_subpages = [
        {'html_name': 'register_app',
         'title': 'Register App'
         }
    ]
    return app_subpages


def app_logic(current_user, db, User, GasamApp, page, return_data):
    if page == 'app_management':
        apps = GasamApp.query.all()
        send_data = {
            'app_data': [
                {
                    'id': app.id,
                    'title': app.title,
                    'subtitle': app.subtitle,
                    'app_url': app.app_url,
                    'app_users': len(app.users),
                    'delete_app': ''
                }
                for app in apps
            ],
            'delete_db_table': 'app_morse_code_db'
        }
    elif page == 'register_app':
        send_data = {'test': 'register_app'}

    return send_data


def json_logic(current_user, db, User, GasamApp, json_data, files_data):
    if json_data['js_function'] == 'app_management_add_new_app':
        return js_function_app_management_add_new_app(current_user, db, User, GasamApp, json_data)
    if json_data['js_function'] == 'app_management_change_app_data':
        return js_function_app_management_change_app_data(current_user, db, User, GasamApp, json_data)


def js_function_app_management_add_new_app(current_user, db, User, GasamApp, json_data):
    new_app = GasamApp(title=json_data['title'], subtitle=json_data['subtitle'], app_url=json_data['app_url'])
    admin = User.query.filter_by(role='admin').first()
    admin.apps.append(new_app)

    db.session.commit()
    return json_data

def js_function_app_management_change_app_data(current_user, db, User, GasamApp, json_data):
    app_to_update = GasamApp.query.get(int(json_data['app_id']))
    if app_to_update:
        if json_data['target'] == 'title':
            app_to_update.title = json_data['title']
        elif json_data['target'] == 'subtitle':
            app_to_update.subtitle = json_data['subtitle']
        elif json_data['target'] == 'app_url':
            app_to_update.app_url = json_data['app_url']
        elif json_data['target'] == 'delete_app':
            db.session.delete(app_to_update)
            if 'delete_db_table' in json_data:
                db.session.execute(text(f'DROP TABLE {json_data["delete_db_table"]}'))

        db.session.commit()  # Commit the changes to the database
    return json_data