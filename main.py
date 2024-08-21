from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Boolean
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

login_manager = LoginManager()
login_manager.init_app(app)


# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///users.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE IN DB
# Association table for the many-to-many relationship
user_app_association = db.Table(
    'user_app_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('app_id', db.Integer, db.ForeignKey('gasam_apps.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(1000), nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Establish the many-to-many relationship with GasamApp
    apps = relationship("GasamApp", secondary=user_app_association, back_populates="users")


class GasamApp(db.Model):
    __tablename__ = "gasam_apps"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250))
    app_url: Mapped[str] = mapped_column(String(250), unique=True)

    # Establish the many-to-many relationship with User
    users = relationship("User", secondary=user_app_association, back_populates="apps")


session = db.session


@login_manager.user_loader
def load_user(user_id):
    return session.get(User, int(user_id))


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']

        user = User.query.filter_by(email=email).first()
        if user:
            flash('This email is already registered. Please login.')
            return redirect(url_for('login'))

        else:
            hashed_password = generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=8)

            new_user = User(name=name,
                            email=email,
                            password=hashed_password,
                            approved=False
                            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            return render_template("home.html")
    return render_template("register.html")


@app.route('/home')
@login_required
def home():
    return render_template("home.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
