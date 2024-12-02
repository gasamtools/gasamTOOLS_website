#zelf workhorse fetcher

def fz_fetcher(current_user, db, User, GasamApp, json_data, files_data, db_name):
    if json_data['js_function_sub'] == 'api':
        return fz_fetcher_api(current_user, db, User, GasamApp, json_data, files_data, db_name)


def fz_fetcher_api(current_user, db, User, GasamApp, json_data, files_data, db_name):

    def get_or_update_env_db(current_user, db, env_key, json_data, db_name):
        from sqlalchemy import text

        if env_key in json_data:
            env_value = json_data[env_key].strip()
        else:
            env_value = None

        if env_value:

            # Check if the user_id already exists
            existing_record = db.session.execute(
                text(f"SELECT * FROM {db_name} WHERE env_key = :env_key"),
                {"env_key": env_key}
            ).fetchone()

            if existing_record:

                db.session.execute(
                    text(
                        f"UPDATE {db_name} SET env_value = :env_value WHERE env_key = :env_key"),
                    {"env_value": env_value, "env_key": env_key}
                )
            else:
                # User does not exist, insert a new record
                db.session.execute(
                    text(
                        f"INSERT INTO {db_name} (user_id, env_key, env_value) VALUES (:user_id, "
                        ":env_key, :env_value)"),
                    {"user_id": current_user.id, "env_key": env_key, "env_value": env_value}
                )

            db.session.commit()

        results = db.session.execute(
            text(f"SELECT env_value FROM {db_name} WHERE env_key=:env_key"),
            {"env_key": env_key})
        return results.scalar()

    if current_user.role == 'admin':
        kc_api_key = get_or_update_env_db(current_user, db, 'KC_API_KEY', json_data, db_name)
        kc_api_secret = get_or_update_env_db(current_user, db, 'KC_API_SECRET', json_data, db_name)
        kc_api_passphrase = get_or_update_env_db(current_user, db, 'KC_API_PASSPHRASE', json_data, db_name)

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



