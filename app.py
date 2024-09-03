import hashlib
import uuid
from datetime import datetime

from flask import Flask, render_template, redirect, session, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/flaskdb'
app.config['SECRET_KEY'] = uuid.uuid4().hex

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    middlename = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __salted_hash(self,password):
        salt = uuid.uuid4().hex
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

    def __setattr__(self, key, value):
        if key == "password":
            object.__setattr__(self, key, self.__salted_hash(value))
        else:
            object.__setattr__(self, key, value)

    def check_password(self, provided_password):
        hashed_psw, salt = self.password.split(':')
        return hashed_psw == hashlib.sha256(salt.encode() + provided_password.encode()).hexdigest()

class OnlineUser(db.Model):
    __tablename__ = 'onlineUsers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    ipaddress = db.Column(db.String(80), nullable=False)
    logindatetime = db.Column(db.DateTime, nullable=False)

def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.fullmatch(regex, email))

def password_error_message(password):
    regex = r'^(?=.*[a-zçğıöşü])(?=.*[A-ZÇĞİÖŞÜ])(?=.*\d).+$'
    if len(password) < 8:
        return 'Password must be at least 8 characters long.'
    elif not bool(re.fullmatch(regex, password)):
        return 'Password must include a lowercase letter, an uppercase letter, and a digit.'
    return ""


def find_errors(data):
    errors = {}
    if not is_valid_email(data['email']):
        errors['email'] = 'Invalid email address.'

    try:
        datetime.strptime(data['birthdate'], '%Y-%m-%d')
    except ValueError:
        errors['birthdate'] = 'Invalid date.'

    for key in data.keys():
        if not data.get(key) and key != 'middlename' and key != 'new_password' and key != 'confirm_password':
            errors[key] = key.capitalize() + ' is required.'

    return errors

def log(text):
    timestamp = datetime.now().strftime("%c")
    log_entry = f"{timestamp} : {text}"
    with open('logs/log.txt', 'a') as file:
        file.write(log_entry + '\n')


@app.route('/user/create', methods=['GET', 'POST'])
def create_user():
    data = request.get_json()
    errors = {}
    if User.query.filter_by(username=data['username']).first():
        errors['username'] = 'Username already taken.'
    if User.query.filter_by(email=data['email']).first():
        errors['email'] = 'Email already taken.'
    errors["password"] = password_error_message(data['password'])
    errors.update(find_errors(data))

    print(data["password"])
    errors = {k: v for k, v in errors.items() if v}
    if errors:
        log(f"Failed user creation for {data['username']} with errors: {errors}")
        return jsonify(success=False, message="User creation failed", errors=errors)

    new_user = User(
        username = data['username'],
        firstname = data['firstname'],
        middlename = data['middlename'],
        lastname = data['lastname'],
        birthdate = datetime.strptime(data['birthdate'], '%Y-%m-%d'),
        email = data['email'],
        password = data['password'])
    db.session.add(new_user)
    db.session.commit()

    log(f"User created successfully: {data['username']}")
    return jsonify(success=True, message="User created successfully")


@app.route('/user/list', methods=["GET"])
def list_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'firstname': user.firstname,
            'middlename': user.middlename,
            'lastname': user.lastname,
            'birthdate': user.birthdate.strftime('%d-%m-%Y'),
            'email': user.email
        }
        user_list.append(user_data)
    log("User list retrieved")
    return jsonify(success=True, message="User list retrieved", user_list=user_list)


@app.route('/onlineusers', methods=["GET"])
def online_users():
    users = OnlineUser.query.all()
    online_user_list = []
    for online_user in users:
        online_user_data = {
            'id': online_user.id,
            'username': online_user.username,
            'ipaddress': online_user.ipaddress,
            'logindatetime': online_user.logindatetime.strftime('%d-%m-%Y'),
        }
        online_user_list.append(online_user_data)
    log("Online user list retrieved")
    return jsonify(success=True, message="Online user list retrieved", online_user_list=online_user_list)


@app.route("/login",methods=['GET', "POST", "DELETE"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    online_user = OnlineUser.query.filter_by(username=username).first()
    if 'user_name' in session or 'admin' in session:
        logout()
    if username == "admin" and password == "admin":
        session['admin'] = True
        log("Admin logged in successfully")
        return jsonify(success=True, message="Admin login successful", isAdmin=True)
    elif user and user.check_password(password):
        session['user_name'] = user.username
        if online_user:
            db.session.delete(online_user)
            db.session.commit()
        online_user = OnlineUser(username=username,ipaddress=request.remote_addr,logindatetime=datetime.now())
        db.session.add(online_user)
        db.session.commit()
        log(f"User {username} logged in successfully")
        return jsonify(success=True, message="User login successful", isAdmin=False)
    elif not user:
        log(f"Failed login attempt: User '{username}' does not exist")
        return jsonify(success=False, message="Login failed", error="User does not exist", isAdmin=False)
    else:
        log(f"Failed login attempt: Incorrect password for user '{username}'")
        return jsonify(success=False, message="Login failed", error="Incorrect password", isAdmin=False)


@app.route("/user/update/",methods=['GET', "POST", "PUT"])
def update_user():
    data = request.get_json()
    user = User.query.filter_by(username=session['user_name']).first()
    online_user = OnlineUser.query.filter_by(username=session['user_name']).first()
    errors = find_errors(data)

    if data["password"] and not user.check_password(data["password"]):
        errors["password"] = "Incorrect password."

    update_password = data["new_password"] or data["confirm_password"]
    if update_password:
        errors["new_password"] = password_error_message(data["new_password"])
        if data["new_password"] != data["confirm_password"]:
            errors["new_password"] = "Passwords do not match:"

    errors = {k: v for k, v in errors.items() if v}

    if errors:
        log(f"Failed update attempt for user {session['user_name']} with errors: {errors}")
        return jsonify(success=False, message="Update failed", errors=errors)

    user.username = data['username']
    session['user_name'] = data['username']
    online_user.username = data['username']
    user.firstname = data['firstname']
    user.middlename = data['middlename']
    user.lastname = data['lastname']
    user.birthdate = datetime.strptime(data['birthdate'], '%Y-%m-%d')
    user.email = data['email']
    if update_password:
        user.password = data["new_password"]

    db.session.commit()
    log(f"User {session['user_name']} updated successfully")
    return jsonify(success=True, message="User updated successfully", errors=errors)


@app.route("/user/delete/", methods=["DELETE"])
def delete_user():
    if 'user_name' not in session:
        return jsonify(success=False, message="User not logged in")
    user = User.query.filter_by(username=session['user_name']).first()
    online_user = OnlineUser.query.filter_by(username=session['user_name']).first()
    db.session.delete(user)
    db.session.delete(online_user)
    db.session.commit()
    session.pop('user_name', None)
    log(f"User {user.username} deleted successfully")
    return jsonify(success=True, message="User deleted successfully")


@app.route("/logout", methods=["DELETE"])
def logout():
    if 'admin' in session:
        session.pop('admin', None)
        return jsonify({'success': True})
    if 'user_name' not in session:
        return jsonify({'success': False})
    online_user = OnlineUser.query.filter_by(username=session['user_name']).first()
    db.session.delete(online_user)
    db.session.commit()
    log(f"User {session['user_name']} logged out successfully")
    session.pop('user_name', None)
    return jsonify(success=True, message="User logged out successfully")

@app.route("/show_logs", methods=["GET"])
def show_logs():
    logs = []
    log("Logs retrieved")
    try:
        with open("logs/log.txt", "r") as file:
            logs = file.readlines()
    except FileNotFoundError:
        logs = ["Log file not found."]
    return jsonify(success=True, message="Logs retrieved", logs=logs)

@app.route("/admin_page")
def admin_page():
    if 'admin' not in session:
        return redirect("/login_page")
    log("Admin page accessed")
    return render_template("admin.html")


@app.route("/update_page/<int:user_id>", methods=["GET"])
def update_page(user_id):
    if 'user_name' not in session:
        return redirect("/login_page")
    user = User.query.filter_by(username=session['user_name']).first()
    log(f"Update page accessed by {user.username}")
    return render_template("update.html", user=user)


@app.route("/account_page")
def account_page():
    if 'user_name' not in session:
        return redirect("/login_page")
    user = User.query.filter_by(username=session['user_name']).first()
    log(f"Account page accessed by {user.username}")
    return render_template('account.html', user=user)


@app.route("/signup")
def signup_page():
    log("Signup page accessed")
    return render_template("signup.html")


@app.route("/login_page")
def login_page():
    log("Login page accessed")
    return render_template("login.html")


@app.route("/")
def home():
    log("Home route accessed")
    return redirect("/login_page")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")
