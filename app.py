from apiflask import APIFlask
from flask import g, request, redirect
from flask.cli import with_appcontext
from flask_migrate import Migrate

from api import get_user
from brand import brand
from blueprint import api_bp, root_bp
from config import (
    DATABASE_URI,
    SECRET_KEY,
    SSL_ENABLED,
    SUPPORTED_TRANSLATIONS
)
from commands import reindex_command, setup_roles_command
from db import db, User
from encryption import bcrypt
from login import login_manager
from logger import setup_logging
from translation import babel

def create_app() -> APIFlask:
    url = brand['url']
    app = APIFlask(
        import_name = __name__,
        template_folder = 'template',
        title = 'Ralphs Booru'
    )

    # Setup logging.
    setup_logging()

    if url:
        app.config['SERVERS'] = [
            {'url': url, 'description': 'Production server'}
        ]

    app.jinja_env.globals['brand'] = brand
    app.config['SECRET_KEY'] = SECRET_KEY
    # Initialize database
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    db.init_app(app)

    # Register command-line commands.
    app.cli.command('reindex')(with_appcontext(reindex_command))
    app.cli.command('setup-roles')(with_appcontext(setup_roles_command))

    # Elevate standard HTTP links to HTTPS for consumption
    # within Jinja2 templates.
    def secure_url(url: str) -> str:
        if url and url.startswith('http://') and SSL_ENABLED:
            return url.replace('http://', 'https://')

        return url

    # Initialize translations
    def get_locale() -> str:
        return g.get('lang_code', request.accept_languages.best_match(SUPPORTED_TRANSLATIONS))
    
    @app.before_request
    def ensure_lang_prefix():
        """ Redirect users to /en URL prefix if there's no languages prefixed. """
        if request.path.startswith(
            (
                '/static',
                '/api',
                '/docs',
                '/openapi.json'
            )
        ):
            return

        path_parts = request.path.split('/')
        first_segment = path_parts[1] if len(path_parts) > 1 else None

        if first_segment in SUPPORTED_TRANSLATIONS:
            g.lang_code = first_segment
            return 

        lang = request.cookies.get('lang_code') or request.accept_languages.best_match(SUPPORTED_TRANSLATIONS) or 'en'
        return redirect(f'/{lang}{request.full_path}', code=302)

    babel.init_app(app, locale_selector = get_locale)

    # Initialize encrypting
    bcrypt.init_app(app)

    # Initialize session management
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> User:
        return get_user(int(user_id))

    # Initialize database migration interface
    migrate = Migrate(app, db)

    app.jinja_env.filters['secure'] = secure_url
    app.register_blueprint(api_bp)
    app.register_blueprint(root_bp)

    return app
