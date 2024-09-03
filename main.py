from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, send_from_directory
from flask import render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Boolean
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os
import importlib
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv



load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')

print("SECRET_KEY:", app.config['SECRET_KEY'])

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///users.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)


user_app_association = db.Table(
    'user_app_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('app_id', db.Integer, db.ForeignKey('gasam_apps.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    role = db.Column(db.String(1000), nullable=True)
    approved = db.Column(db.Boolean, nullable=False)
    apps = relationship("GasamApp", secondary=user_app_association, back_populates="users")

class GasamApp(db.Model):
    __tablename__ = "gasam_apps"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250))
    app_url = db.Column(db.String(250), unique=True)
    users = relationship("User", secondary=user_app_association, back_populates="apps")

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':

            # CSRF token validation is automatically handled

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


@app.route('/profile', methods=["GET", "POST", "PUT"])
@login_required
def profile():
    if request.method == 'PUT':
        json_data = request.get_json()

        if check_password_hash(current_user.password, json_data['user_password']):
            json_data['correct_password'] = True

            current_user.name = json_data['user_name']
            db.session.commit()  # Commit the changes to the database
        else:
            json_data['correct_password'] = False

        return jsonify(json_data)
    else:
        return render_template("profile.html",
                               user_approved=current_user.approved,
                               user_apps=current_user.apps,
                               user_name=current_user.name,
                               user_role=current_user.role
                               )


@app.route('/settings', methods=["GET", "POST", "PUT"])
@login_required
def settings():
    if request.method == 'PUT':
        json_data = request.get_json()

        if check_password_hash(current_user.password, json_data['user_password']):
            json_data['correct_password'] = True

            current_user.email = json_data['user_email']
            if json_data['user_new_password'] != '':
                hashed_password = generate_password_hash(json_data['user_new_password'], method='pbkdf2:sha256',
                                                         salt_length=8)
                current_user.password = hashed_password

            db.session.commit()  # Commit the changes to the database
        else:
            json_data['correct_password'] = False

        return jsonify(json_data)
    else:
        return render_template("settings.html",
                               user_approved=current_user.approved,
                               user_apps=current_user.apps,
                               user_email=current_user.email,
                               )


@app.route('/home')
@login_required
def home():
    app1 = GasamApp(title="App Management", subtitle="For admin only", app_url="app_management")
    current_user.apps.append(app1)
    # current_user.approved = True
    # current_user.role = 'admin'
    db.session.commit()

    return render_template("home.html",
                           user_approved=current_user.approved,
                           user_apps=current_user.apps)

@app.route('/audio/<path:directory>/<filename>')
def serve_audio(directory,filename):
    # Path to the directory containing your wav files
    path = f"{directory}"
    return send_from_directory(path, filename)

@app.route('/download/<path:directory>/<filename>')
def download_file(directory,filename):
    # Path to the directory containing your wav files
    path = f"{directory}"
    return send_from_directory(path, filename, as_attachment=True)


@app.route('/<path:appname>/js/<path:filename>')
def serve_app_js(appname, filename):
    return send_from_directory(f'apps/{appname}/js', filename)


@app.route('/<path:appname>/css/<path:filename>')
def serve_app_css(appname, filename):
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
        send_data = app_manager.app_logic(current_user, db, User, GasamApp, app_name, return_data)
        if 'db_init' in send_data:
            plugin_db_func = send_data['db_init']
            plugin_db_func(db, app)
    else:
        send_data = {}

    if hasattr(app_manager, 'register_subpages'):
        app_subpages = app_manager.register_subpages()
    else:
        app_subpages = {}

    if current_user.approved:

        if request.method == 'PUT':
            json_data = request.get_json()
            if hasattr(app_manager, 'json_logic'):
                send_json_data = app_manager.json_logic(current_user, db, User, GasamApp, json_data)
            else:
                send_json_data = {}

            return jsonify(send_json_data)
        # elif request.method == 'GET':
        #     if request.args:
        #         query_params = request.args.to_dict(flat=False)
        #         print(query_params)
        #         sub_html_file_path = os.path.join('apps', app_name, 'subpage', f'{query_params["sub_page"][0]}.html')
        #         with open(sub_html_file_path, 'r') as file:
        #             sub_html_content = file.read()
        #             rendered_sub_html_content = render_template_string(sub_html_content, send_data=query_params)
        #             rendered_js_content = render_template_string(js_html_content, send_data='')
        #             rendered_css_content = render_template_string(css_html_content, send_data='')
        #             return render_template("app.html",
        #                                    app_html=rendered_sub_html_content,
        #                                    user_apps=current_user.apps,
        #                                    app_name=app_name,
        #                                    app_js=rendered_js_content,
        #                                    app_css=rendered_css_content
        #                                    )
        else:
            rendered_html_content = render_template_string(html_content, send_data=send_data)
            rendered_js_content = render_template_string(js_html_content, send_data='')
            rendered_css_content = render_template_string(css_html_content, send_data='')
            return render_template("app.html",
                                   app_html=rendered_html_content,
                                   user_apps=current_user.apps,
                                   app_name=app_name,
                                   app_js=rendered_js_content,
                                   app_css=rendered_css_content,
                                   app_subpages=app_subpages
                                   )
    else:
        return redirect(url_for('home'))


@app.route("/app/<app_name>/<subpage_name>", methods=["GET", "POST", "PUT"])
@login_required
def access_app_subpage(app_name, subpage_name):
    if request.method == "POST":
        return_data = request.form
    else:
        return_data = False

    html_file_path = os.path.join('apps', app_name, 'subpage', f'{subpage_name}.html')
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
        send_data = app_manager.app_logic(current_user, db, User, GasamApp, subpage_name, return_data)
    else:
        send_data = {}

    if hasattr(app_manager, 'register_subpages'):
        app_subpages = app_manager.register_subpages()
    else:
        app_subpages = {}

    if current_user.approved:

        if request.method == 'PUT':
            json_data = request.get_json()
            if hasattr(app_manager, 'json_logic'):
                send_json_data = app_manager.json_logic(current_user, db, User, GasamApp, json_data)
            else:
                send_json_data = {}

            return jsonify(send_json_data)
        elif request.method == 'GET':
            if request.args:
                query_params = request.args.to_dict(flat=False)
                print(query_params)
                sub_html_file_path = os.path.join('apps', app_name, 'subpage', f'{query_params["sub_page"][0]}.html')
                with open(sub_html_file_path, 'r') as file:
                    sub_html_content = file.read()
                    rendered_sub_html_content = render_template_string(sub_html_content, send_data=query_params)
                    rendered_js_content = render_template_string(js_html_content, send_data='')
                    rendered_css_content = render_template_string(css_html_content, send_data='')
                    return render_template("app.html",
                                           app_html=rendered_sub_html_content,
                                           user_apps=current_user.apps,
                                           app_name=app_name,
                                           app_js=rendered_js_content,
                                           app_css=rendered_css_content,
                                           app_subpages=app_subpages
                                           )
            else:
                rendered_html_content = render_template_string(html_content, send_data=send_data)
                rendered_js_content = render_template_string(js_html_content, send_data='')
                rendered_css_content = render_template_string(css_html_content, send_data='')
                return render_template("app.html",
                                       app_html=rendered_html_content,
                                       user_apps=current_user.apps,
                                       app_name=app_name,
                                       app_js=rendered_js_content,
                                       app_css=rendered_css_content,
                                       app_subpages=app_subpages
                                       )
    else:
        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=False)
