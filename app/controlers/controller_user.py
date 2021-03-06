from flask import request, render_template, jsonify
from flask_login import login_user, current_user, logout_user

from app.models.model_exceptions import ErrorIncorrectPassword, ErrorRecordNotExists
from app.models.model_user import User, Login
from app.models.model_exceptions import ErrorRecordExists

from app.config import app, login_manager




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['POST', 'GET'])
def login_method():
    if request.method == 'POST':
        login = Login(login_name=request.form['login_name'], password=request.form['password'])
        try:
            login = login.authentication()
        except ErrorRecordNotExists:
            return render_template('layout.html', login_message="Neexistující uživatelské jméno.")
        except ErrorIncorrectPassword:
            return render_template('layout.html', login_message="Špatné heslo")
        user = User.query.get(login.user_id)
        login_user(user)
        return render_template('contents/index.html')
    else:
        return render_template('contents/index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        messages = dict()
        # Validation
        user = User(nick_name=request.form['nick_name'])
        if user.exists():
            messages['nick_name_message'] = "Uživatel s daným jménem již existuje."
        login = Login(login_name=request.form['login_name'], password=request.form['password'])
        if login.exists():
            messages['login_name_message'] = "Přihlašovací jméno již někdo používá."
        # Not valid
        if len(messages) != 0:
            return render_template('contents/users/register.html', **messages)
        # Valid
        else:
            user.add_user()
            user = User.query.filter_by(nick_name=user.nick_name).first()
            login.add_login(user.id)
            return render_template('contents/users/success_register.html')
    else:
        return render_template('contents/users/register.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'POST':
        logout_user()
        return render_template('contents/index.html')


@app.route('/user_profile/<int:user_id>', methods=['POST', 'GET'])
def personal_profile(user_id):
    if request.method == 'GET':
        user = User.query.get(user_id)

        return render_template('contents/users/user_profile.html', user=user)
    return render_template('contents/users/user_profile.html')


@app.route('/add_users', methods=['POST', 'GET'])
def add_users():
    if request.method == 'GET':
        return render_template('contents/users/add_users.html')
    if request.method == 'POST':
        unregistered_users = request.form['new_users'].split()
        for user in unregistered_users:
            new_user = User(nick_name=user)
            try:
                new_user.add_user()
            except ErrorRecordExists:
                pass
        all_users = User.query.filter( User.nick_name!="superadmin").all()

        return render_template('contents/users/list_of_users.html', users=all_users)


@app.route('/list_of_users', methods=['POST', 'GET'])
def list_of_users():
    all_users = User.query.filter(User.nick_name != "superadmin").all()
    return render_template('contents/users/list_of_users.html', users=all_users)