from flask import Flask, session, g
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
from datetime import timedelta
import logging
import sys


# Set logger web-app

logger = logging.getLogger('web-app')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('./logs/web-app.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)


logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


# Set SQLAlchemy
db = SQLAlchemy()

# TODO: Switch to ORM
DB_NAME = "database.db"



def create_app():

    app = Flask(__name__)
    #TODO: Change SECRET KEY
    app.config['SECRET_KEY'] = '1234567'
    #TODO: Change DATABASE URI
    #app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # Manage sessions and timeout
    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=10)
        session.modified = True
        g.user = current_user

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    
    with app.app_context():
        try:
            db.create_all()
            logger.info('Database Created!')
        except Exception as e:
            logger.error(f'Failed to create database: {e}')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    logger.info('Login manager initialized')

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
