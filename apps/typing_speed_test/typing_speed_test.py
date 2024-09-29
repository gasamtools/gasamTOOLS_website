import os
import requests
import random
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
    class TypingSpeedTestDB(db.Model):
        __tablename__ = 'app_typing_speed_test_db'

        record_id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False)
        user_score = db.Column(db.Integer, nullable=True)
        admin_key = db.Column(db.String(200), nullable=True)

        def __init__(self, user_id, user_score=None):
            self.user_id = user_id
            self.user_score = user_score

        __table_args__ = {'extend_existing': True}

    with app.app_context():
        db.create_all()


def app_logic(current_user, db, User, GasamApp, page, return_data):
    if page == 'typing_speed_test':
        send_data = {'db_init': register_database,
                     # 'file_path_coin_gif_choice_undecided': file_path_coin_gif_choice_undecided,
                     }

        return send_data


def json_logic(current_user, db, User, GasamApp, json_data, files_data):
    if json_data['js_function'] == 'typing_speed_test_ini':
        return js_function_typing_speed_test_ini(current_user, db, User, GasamApp, json_data, files_data)
    if json_data['js_function'] == 'typing_speed_test_get_text':
        return js_function_typing_speed_test_get_text(current_user, db, User, GasamApp, json_data, files_data)
    if json_data['js_function'] == 'typing_speed_test_update_record':
        return js_function_typing_speed_test_update_record(current_user, db, User, GasamApp, json_data, files_data)
    if json_data['js_function'] == 'typing_speed_test_api':
        return js_function_typing_speed_test_api(current_user, db, User, GasamApp, json_data, files_data)



def js_function_typing_speed_test_ini(current_user, db, User, GasamApp, json_data, files_data):
    # install plugin packages
    from main import check_and_install_requirements
    requirements_dir = os.path.join('apps', 'typing_speed_test', 'typing_speed_test_requirements.txt')
    check_and_install_requirements(requirements_dir)

    # array_operations()

    return {'status': 'packages installed'}


def js_function_typing_speed_test_get_text(current_user, db, User, GasamApp, json_data, files_data):
    char_num = 300
    char_min_num = 150
    chosen_chapter_verses = ''

    while len(chosen_chapter_verses) < char_min_num:
        chosen_chapter_verses = request_api_bible(char_num, db)

    results = db.session.execute(text("SELECT user_score FROM app_typing_speed_test_db WHERE user_id=:user_id"),
                                 {"user_id": current_user.id})
    user_score = results.scalar()
    if user_score is None:
        user_score = 0

    return {'text': chosen_chapter_verses, 'user_record': user_score}


def js_function_typing_speed_test_update_record(current_user, db, User, GasamApp, json_data, files_data):
    new_user_score = int(json_data['new_score'])

    # Check if the user_id already exists
    existing_record = db.session.execute(
        text("SELECT * FROM app_typing_speed_test_db WHERE user_id = :user_id"),
        {"user_id": current_user.id}
    ).fetchone()

    if existing_record:

        results = db.session.execute(text("SELECT user_score FROM app_typing_speed_test_db WHERE user_id=:user_id"),
                                     {"user_id": current_user.id})
        user_score = results.scalar()
        if user_score < new_user_score:
            # User exists, update the user_score
            db.session.execute(
                text("UPDATE app_typing_speed_test_db SET user_score = :user_score WHERE user_id = :user_id"),
                {"user_score": new_user_score, "user_id": current_user.id}
            )
            print(f"Updated user_score for user_id {current_user.id} to {new_user_score}.")
    else:
        # User does not exist, insert a new record
        db.session.execute(
            text("INSERT INTO app_typing_speed_test_db (user_id, user_score) VALUES (:user_id, :user_score)"),
            {"user_id": current_user.id, "user_score": new_user_score}
        )
        print(f"Inserted new record for user_id {current_user.id} with score {new_user_score}.")

    # Commit the session
    db.session.commit()


def request_api_bible(char_num, db):

    if os.getenv('BIBLE_API_KEY'):
        API_KEY = os.getenv('BIBLE_API_KEY')
    else:
        results = db.session.execute(text("SELECT admin_key FROM app_typing_speed_test_db WHERE user_id=:user_id"),
                                     {"user_id": 1})
        admin_key = results.scalar()
        API_KEY = admin_key

    API_CONTENTS_URL = 'https://api.scripture.api.bible/v1/bibles/de4e12af7f28f599-01/books?include-chapters=false&include-chapters-and-sections=true'

    headers = {
        'accept': 'application/json',
        'api-key': API_KEY,
    }

    response = requests.get(url=API_CONTENTS_URL, headers=headers)
    response.raise_for_status()
    response_data = response.json()
    random_book = random.choice(response_data['data'])
    random_chapter = random.choice(random_book['chapters'])

    API_CHAPTER_URL = (f'https://api.scripture.api.bible/v1/bibles/de4e12af7f28f599-01/chapters/{random_chapter["id"]}'
                       f'?content-type=text&include-notes=false&include-titles=false&include-chapter-numbers=false&'
                       f'include-verse-numbers=false&include-verse-spans=false')

    response = requests.get(url=API_CHAPTER_URL, headers=headers)
    response.raise_for_status()
    response_data = response.json()

    chosen_chapter_verses_arr = [verse.strip() for verse in response_data['data']['content'].split('.')]

    chosen_chapter_verses = ''

    i = 0
    for verse in chosen_chapter_verses_arr:
        i += 1
        if len(chosen_chapter_verses) < char_num:

            if i != 1:
                chosen_chapter_verses += ' '
            chosen_chapter_verses += verse
            chosen_chapter_verses += '.'

    if len(chosen_chapter_verses) > char_num:
        end = chosen_chapter_verses[0:char_num].rfind(" ")  # Find the last comma
        updated_chosen_chapter_verses = chosen_chapter_verses[0:end].strip()  # Slice between the commas
    else:
        updated_chosen_chapter_verses = chosen_chapter_verses

    return updated_chosen_chapter_verses


def js_function_typing_speed_test_api(current_user, db, User, GasamApp, json_data, files_data):

    inputAPI = json_data['api_val'].strip()

    if current_user.role == 'admin':

        if inputAPI:

            # Check if the user_id already exists
            existing_record = db.session.execute(
                text("SELECT * FROM app_typing_speed_test_db WHERE user_id = :user_id"),
                {"user_id": current_user.id}
            ).fetchone()

            if existing_record:

                db.session.execute(
                    text("UPDATE app_typing_speed_test_db SET admin_key = :admin_key WHERE user_id = :user_id"),
                    {"admin_key": inputAPI, "user_id": current_user.id}
                )
            else:
                # User does not exist, insert a new record
                db.session.execute(
                    text("INSERT INTO app_typing_speed_test_db (user_id, user_score, admin_key) VALUES (:user_id, "
                         ":user_score, :admin_key)"),
                    {"user_id": current_user.id, "user_score": 0, "admin_key": inputAPI}
                )

            db.session.commit()

        results = db.session.execute(text("SELECT admin_key FROM app_typing_speed_test_db WHERE user_id=:user_id"),
                                     {"user_id": 1})
        admin_key = results.scalar()

    else:
        admin_key = ''

    return { 'key': admin_key}


# test function to text local requirements.txt
def array_operations():
    import numpy as np
    # Create a NumPy array
    array = np.array([1, 2, 3, 4, 5])

    # Perform some operations
    sum_array = np.sum(array)  # Sum of all elements
    mean_array = np.mean(array)  # Mean of the array
    max_value = np.max(array)  # Maximum value in the array
    min_value = np.min(array)  # Minimum value in the array

    # return sum_array, mean_array, max_value, min_value
    print(f"Sum: {sum_array}, Mean: {mean_array}, Max: {max_value}, Min: {min_value}")
