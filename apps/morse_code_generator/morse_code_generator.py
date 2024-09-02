from .morse_data import morse_data
from .sound_player import SoundPlayer
import os
from flask import render_template_string

def register_subpages():
    app_subpages = [
    ]

    return app_subpages

def register_database(db, app):
    class MorseCodeDB(db.Model):
        __tablename__ = 'app_morse_code_db'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), nullable=False)
        description = db.Column(db.String(200), nullable=True)

        def __init__(self, name, description=None):
            self.name = name
            self.description = description

        __table_args__ = {'extend_existing': True}

    with app.app_context():
        db.create_all()

def app_logic(current_user, db, User, GasamApp, page, return_data):

    if page == 'morse_code_generator':
        send_data = {'db_init': register_database,
                     'morse_data': morse_data,
                     }



    return send_data


def json_logic(current_user, db, User, GasamApp, json_data):
    if json_data['js_function'] == 'morse_code_generator':
        return js_function_morse_code_generator(current_user, db, User, GasamApp, json_data)

def js_function_morse_code_generator(current_user, db, User, GasamApp, json_data):
    this_text = json_data['input_text'].upper().strip()
    this_au_filename = f"{this_text.replace(' ', '_')}.wav"
    morse_code = ''
    for char in this_text:
        morse_code += morse_data[char]
        morse_code += '   '

    json_data['morse_code_response'] = morse_code

    play_dot_sound = SoundPlayer()
    play_dot_sound.play_and_save_sound(morse_code=morse_code, output_file=this_au_filename)

    part_html_file_path = os.path.join('apps', 'morse_code_generator', 'parts',
                                       'morse_code_generator__play_download_sound.html')
    with open(part_html_file_path, 'r') as file:
        part_html_file = file.read()
    file_path_output_wav = os.path.join('apps', 'morse_code_generator', 'generated_sound')
    json_data['download_file_directory'] = file_path_output_wav
    json_data['download_file_filename'] = this_au_filename
    rendered_part_html_content = render_template_string(part_html_file, send_data=json_data)
    json_data['user_apps_html'] = rendered_part_html_content

    return json_data
