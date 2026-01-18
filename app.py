from os import getenv

from apiflask import APIFlask
from dotenv import load_dotenv
from flask_migrate import Migrate

from api import get_user
from brand import brand
from blueprint import api_bp, root_bp
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
    app.config['SERVERS'] = [
        {'url': brand['url'], 'description': 'Production server'}
    ]

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
    app.register_blueprint(root_bp)

    return app
