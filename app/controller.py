from flask import request, render_template, jsonify
from flask_login import login_user, current_user, logout_user


from app.models.model_exceptions import ErrorIncorrectPassword, ErrorRecordExists, ErrorRecordNotExists
from app.models.model_user import User, Login
from app.models.model_turnament import Tournament, Player, PlayingType

from .config import app, login_manager

from datetime import datetime

"""
This module implements Front-controller.
"""


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


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
        for x in current_user.list_of_privileges:
            print(x.type_of_privilege.name)
        return render_template('layout.html', user_id=current_user.nick_name)
    else:
        return render_template('index.html')


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
            return render_template('register.html', **messages)
        # Valid
        else:
            user.add_user()
            user = User.query.filter_by(nick_name=user.nick_name).first()
            login.add_login(user.id)
            return render_template('success_register.html')
    else:
        return render_template('register.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'POST':
        logout_user()
        return render_template('index.html')


@app.route('/user_profile')
def personal_profile():
    return render_template('user_profile.html')


@app.route('/create_tournament',  methods=['POST', 'GET'])
def create_tournament():
    if request.method == 'POST':
        if request.form['type'] == 'booster_draft':
            count_of_boosters = int(request.form['count_of_boosters'])
            return render_template('create_tournament.html', count_of_boosters=count_of_boosters)
        return render_template('create_tournament.html')
    else:
        return render_template('create_tournament.html')


@app.route('/choice_tournament',  methods=['POST', 'GET'])
def choice_tournament():
    if request.method == 'POST':
        return render_template('choice_tournament.html')
    else:
        return render_template('choice_tournament.html')


@app.route('/get_user_list')
def get_user_list():
    users = User.query.filter().all()

    result = dict()
    for user in users:
        result[user.nick] = user.id
    print(result)
    return jsonify(result)


# ----------------------------------------------------------------------------------------------------------------------
# ERROR PAGES
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_pages/404.html'), 404

