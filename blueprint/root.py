from typing import Any

from flask import Blueprint, Response, current_app, g, request
from flask_login import current_user

from .account import account_bp
from .contact import contact_bp
from .comment import comment_bp
from .error import err_bp
from .help import help_bp
from .index import index_bp
from .manage_user import manage_user_bp
from .post import post_bp
from .tag import tag_bp
from .thumbnail import thumbnail_bp

root_bp = Blueprint(
    name = 'Root',
    import_name = __name__,
    url_prefix = '/<lang_code>'
)

@root_bp.url_value_preprocessor
def pull_lang_code(endpoint: str | None, values: dict[str, Any] | None):
    lang_code = values.pop('lang_code') if values else None

    if not lang_code:
        lang_code = request.cookies.get('lang_code')

    if lang_code not in ['en', 'lv']:
        lang_code = 'en'

    g.lang_code = lang_code

@root_bp.url_defaults
def add_lang_code(endpoint: str, values: dict[str, Any]) -> None:
    if 'lang_code' in values:
        return

    lang_code = g.get('lang_code')
    if not lang_code:
        path_parts = request.path.split('/')
        if len(path_parts) > 1 and path_parts[1] in ['en', 'lv']:
            lang_code = path_parts[1]
        else:
            lang_code = 'en'

    if current_app.url_map.is_endpoint_expecting(endpoint, 'lang_code'):
        values.setdefault('lang_code', lang_code)

@root_bp.after_request
def set_lang_cookie(response: Response):
    lang_code = g.get('lang_code')

    if lang_code:
        response.set_cookie(
            'lang_code', 
            lang_code, 
            max_age=60*60*24*30,
            path='/',
            samesite='Lax'
        )
    
    return response

# Injects currently logged in user to the template.
# This is so we can access the API key for JavaScript within the template.
@root_bp.context_processor
def inject_user():
    return {
        'user': current_user
    }

root_bp.register_blueprint(account_bp)
root_bp.register_blueprint(contact_bp)
root_bp.register_blueprint(comment_bp)
root_bp.register_blueprint(err_bp)
root_bp.register_blueprint(help_bp)
root_bp.register_blueprint(index_bp)
root_bp.register_blueprint(manage_user_bp)
root_bp.register_blueprint(post_bp)
root_bp.register_blueprint(tag_bp)
root_bp.register_blueprint(thumbnail_bp)
