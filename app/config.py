"""
This module provides creating and configuring base object.

app     ...     flask instance
db      ...     flask-sqlalchemy instance
"""

from flask import Flask
from flask_sqlalchemy import *
from os import path
from flask_login import LoginManager

global_config = dict()
global_config['database_name'] = 'database.db'
global_config['database_repository'] = 'db_repo'
global_config['database_schema'] = 'sqlite:///'
global_config['site_url'] = 'http://127.0.0.1:5000/'
global_config['error_pages'] = 'error_pages'
# Create flask instance
app = Flask(__name__)

# flask instance config
app.static_folder = 'static'
app.template_folder = 'templates'
app.secret_key = 'bflm456'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = path.join(global_config['database_schema'],
                                                  global_config['database_repository'],
                                                  global_config['database_name'])
app.config['SQLALCHEMY_MIGRATE_REPO'] = 'db_repo'

# Create database instance with flask context
db = SQLAlchemy(app)

# Create login manager instance

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
