from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, send_from_directory, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Boolean
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os
import importlib

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
    role: Mapped[str] = mapped_column(String(1000), nullable=True)
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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
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


@app.route('/login')
def login_redirect():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':

            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            repeat_password = request.form['repeat_password']

            user = User.query.filter_by(email=email).first()
            if user:
                flash('This email is already registered. Please login.')
                return redirect(url_for('login'))
            elif password != repeat_password:
                flash("Passwords do not match")
            else:
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

                new_user = User(name=name,
                                email=email,
                                password=hashed_password,
                                approved=False
                                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)

                return redirect(url_for('home'))
        return render_template("register.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    # app1 = GasamApp(title="App Management", subtitle="For admin only", app_url="app_management")
    # current_user.apps.append(app1)
    # current_user.approved = True
    # current_user.role = 'admin'
    # db.session.commit()

    return render_template("home.html",
                           user_approved=current_user.approved,
                           user_apps=current_user.apps)

@app.route('/<path:appname>/js/<path:filename>')
def serve_app_js(appname,filename):
    return send_from_directory(f'apps/{appname}/js', filename)

@app.route('/<path:appname>/css/<path:filename>')
def serve_app_css(appname,filename):
    return send_from_directory(f'apps/{appname}/css', filename)


@app.route("/app/<app_name>", methods=["GET", "POST", "PUT"])
@login_required
def access_app(app_name):
    if request.method == "POST":
        return_data = request.form
    else:
        return_data = False

    html_file_path = os.path.join('apps', app_name, f'{app_name}.html')
    js_file_path = os.path.join('apps', app_name, 'js', '_registry.html')
    css_file_path = os.path.join('apps', app_name, 'css', '_registry.html')

    with open(html_file_path, 'r') as file:
        html_content = file.read()

    with open(js_file_path, 'r') as file:
        js_html_content = file.read()

    with open(css_file_path, 'r') as file:
        css_html_content = file.read()

    try:
        module_name = f"apps.{app_name}.{app_name}"
        app_manager = importlib.import_module(module_name)
    except ImportError:
        return f"Error: No {app_name}.py found for {app_name}", 404

    if hasattr(app_manager, 'app_logic'):
        send_data = app_manager.app_logic(current_user, db, User, GasamApp, return_data)
    else:
        send_data = {}

    if current_user.approved:

        if request.method == 'PUT':
            json_data = request.get_json()
            if hasattr(app_manager, 'json_logic'):
                send_json_data = app_manager.json_logic(current_user, db, User, GasamApp, json_data)
            else:
                send_json_data = {}

            return jsonify(send_json_data)
        else:
            rendered_html_content = render_template_string(html_content, send_data=send_data)
            rendered_js_content = render_template_string(js_html_content, send_data='')
            rendered_css_content = render_template_string(css_html_content, send_data='')
            return render_template("app.html",
                                   app_html=rendered_html_content,
                                   user_apps=current_user.apps,
                                   app_name=app_name,
                                   app_js=rendered_js_content,
                                   app_css=rendered_css_content
                                   )
    else:
        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
