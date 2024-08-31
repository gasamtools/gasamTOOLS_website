
def init_app_morse_code_generator(db, app):
    class MorseCodeDB(db.Model):
        __tablename__ = 'app_morse_code_db'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), nullable=False)
        description = db.Column(db.String(200), nullable=True)

        def __init__(self, name, description=None):
            self.name = name
            self.description = description
