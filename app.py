from os import getenv

from apiflask import APIFlask
from flask import g, request, redirect
from flask.cli import with_appcontext
from dotenv import load_dotenv
from flask_migrate import Migrate

from api import get_user
from brand import brand
from blueprint import api_bp, root_bp
from db import db, Permission, Role, User
from encryption import bcrypt
from login import login_manager
from translation import SUPPORTED_TRANSLATIONS, babel

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

    @app.cli.command('setup-roles')
    @with_appcontext
    def setup_roles_command():
        perms = {
            'comment': Permission(slug='post:comment'),
            'upload': Permission(slug='post:upload'),
            'edit': Permission(slug = 'post:edit'),
            'delete': Permission(slug='post:delete'),
            'tag_edit': Permission(slug='tag:edit'),
            'user_ban': Permission(slug='user:ban'),
        }

        admin = Role(name = 'Admin', priority = 10)
        mod = Role(name = 'Moderator', priority = 8)
        janitor = Role(name = 'Janitor', priority = 2)
        user = Role(name = 'User', priority = 1)

        # Admins get everything
        admin.permissions = list(perms.values())

        # Moderators get most things
        mod.permissions = [perms['comment'], perms['upload'], perms['delete'], perms['tag_edit'], perms['user_ban']]

        # Janitors only help with content
        janitor.permissions = [perms['comment'], perms['delete'], perms['tag_edit']]

        # Normal users can only upload
        user.permissions = [perms['comment'], perms['upload']]

        db.session.add_all([admin, mod, user, janitor])
        db.session.commit()

    # Initialize translations
    def get_locale() -> str:
        return g.get('lang_code', request.accept_languages.best_match(SUPPORTED_TRANSLATIONS))
    
    @app.before_request
    def ensure_lang_prefix():
        """ Redirect users to /en URL prefix if there's no languages prefixed. """
        if request.path.startswith('/static') or request.endpoint == 'static':
            return

        if request.path.startswith('/api'):
            return

        if request.path.startswith('/docs') or request.path.startswith('/openapi.json'):
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

    app.register_blueprint(api_bp)
    app.register_blueprint(root_bp)

    return app
