from typing import Any

from flask import Blueprint, g
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
    g.lang_code = values.pop('lang_code', None)

@root_bp.url_defaults
def add_lang_code(endpoint: str | None, values: dict[str, Any]):
    if 'lang_code' in values:
        return

    if g.lang_code:
        values.setdefault('lang_code', g.lang_code)

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
