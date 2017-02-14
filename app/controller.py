from .config import app, login_manager, db
from flask import redirect, url_for, request, render_template, flash
from flask_login import login_user, current_user, logout_user, session
from .model_user import User

"""
This module implements Front-controller.
"""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@app.route('/index')
def index():
    print()
    return render_template('layout.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = User(login=request.form['login'], password=request.form['login'])
        user, flag = user.authentication()
        if user is None:
            message = "Error:" + User.flags[flag]
            return render_template('layout.html', message=message)
        if login_user(user):
            return render_template('layout.html', user_id=current_user.nick)
    else:
        return render_template('layout.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user = User(login=request.form['login'],
                    password=request.form['password'],
                    nick=request.form['nick'],
                    email=request.form['email'])
        collisions = user.register()
        empties = user.check_empties()
        result = dict()
        if collisions is not None:
            for item in collisions:
                result[item + "_message"] = "- je již použito"
        if empties is not None:
            for item in empties:
                result[item + "_message"] = "- políčko nesmí být prázdné"
        if len(result) == 0:
            return render_template('success_register.html')
        for name in request.form:
            if not name == "password":
                result[name] = request.form[name]

        return render_template('register.html', **result)
    else:
        return render_template('register.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'POST':
        logout_user()
        return render_template('layout.html')


@app.route('/personal_profile')
def personal_profile():
    return render_template('personal_profile.html')


# ----------------------------------------------------------------------------------------------------------------------
# ERROR PAGES
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_pages/404.html'), 404

