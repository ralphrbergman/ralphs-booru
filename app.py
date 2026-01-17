from os import getenv

from apiflask import APIFlask
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_migrate import Migrate

from api import get_user
from brand import brand
from blueprint import api_bp, account_bp, contact_bp, comment_bp, err_bp, help_bp, index_bp, manage_user_bp, post_bp, tag_bp, thumbnail_bp
from db import db, User
from encryption import bcrypt
from login import login_manager

load_dotenv()

def create_app() -> APIFlask:
    app = APIFlask(
        import_name = __name__,
        template_folder = 'template',
        title = 'Ralphs Booru'
    )

    app.jinja_env.globals['brand'] = brand
    app.config['SECRET_KEY'] = getenv('SECRET_KEY')
    # Initialize database
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI')

    db.init_app(app)

    # Initialize encrypting
    bcrypt.init_app(app)

    # Initialize session management
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> User:
        return get_user(int(user_id))

    # Initialize database migration interface
    migrate = Migrate(app, db)

    app.register_blueprint(api_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(err_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(manage_user_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(thumbnail_bp)

    return app
