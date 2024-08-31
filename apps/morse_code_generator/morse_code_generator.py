# from main import db
#
# class MorseCodeDB(db.Model):
#     __tablename__ = 'app_morse_code_db'
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     description = db.Column(db.String(200), nullable=True)
#
#     def __init__(self, name, description=None):
#         self.name = name
#         self.description = description




def register_subpages():
    app_subpages = [
    ]

    return app_subpages

def app_logic(current_user, db, User, GasamApp, page, return_data):
    if page == 'morse_code_generator':
        send_data = {'test': 'morse_code_generator'}


    return send_data