from os import getenv

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

from api import get_user
from blueprint import account_bp, index_bp, post_bp
from db import db, User
from encryption import bcrypt

load_dotenv()

def create_app() -> Flask:
    app = Flask(
        import_name = __name__,
        template_folder = 'template'
    )

    app.config['SECRET_KEY'] = getenv('SECRET_KEY')
    # Initialize database
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Initialize encrypting
    bcrypt.init_app(app)

    # Initialize session management
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> User:
        return get_user(int(user_id))

    app.register_blueprint(account_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(post_bp)

    return app
