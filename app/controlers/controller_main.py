from flask import request, render_template, jsonify
from flask_login import login_user, current_user, logout_user

from app.models.model_exceptions import ErrorIncorrectPassword, ErrorRecordExists, ErrorRecordNotExists
from app.models.model_user import User, Login
from app.models.model_turnament import Tournament, Player
from app.models.model_mtg import MtgSet

from app.config import app, login_manager

from datetime import datetime

"""
This module implements Front-controller.
"""





@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


# ----------------------------------------------------------------------------------------------------------------------
# ERROR PAGES
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_pages/404.html'), 404

