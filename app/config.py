"""
This module provides creating and configuring base object.

app     ...     flask instance
db      ...     flask-sqlalchemy instance
"""

from flask import Flask
from flask_sqlalchemy import *
from os import path
from flask_login import LoginManager


db_schema = 'sqlite:///'
db_dir = 'db_repo'
db_name = 'database.db'

# Create flask instance
app = Flask(__name__)

# flask instance config
app.static_folder = 'static'
app.template_folder = 'templates'
app.secret_key = 'bflm456'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = path.join(db_schema, db_dir, db_name)
app.config['SQLALCHEMY_MIGRATE_REPO'] = 'db_repo'

# Create database instance with flask context
db = SQLAlchemy(app)

# Create login manager instance

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
