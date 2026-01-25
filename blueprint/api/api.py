from flask import Blueprint, Request

from db.models.user import find_user_by_key
from login import login_manager
from .comment import comment_bp
from .post import post_bp
from .post_bulk import post_bulk_bp
from .score import score_bp
from .tag import tag_bp
from .tags import tags_bp
from .user import user_bp

api_bp = Blueprint(
    name = 'REST API',
    import_name = __name__,
    url_prefix = '/api'
)

@api_bp.errorhandler(404)
def _404_handler(exc):
    return {'message': 'You are at the wrong place', 'code': 404}, 404

@login_manager.request_loader
def load_user_from_request(request: Request):
    # Ignore API key usage beyond non-API requests.
    if not request.path.startswith('/api'):
        return

    auth_header = request.headers.get('Authorization')

    if auth_header and auth_header.startswith('Bearer '):
        api_key = auth_header.replace('Bearer ', '', 1)

        user = find_user_by_key(api_key)

        return user

api_bp.register_blueprint(comment_bp)
api_bp.register_blueprint(post_bp)
api_bp.register_blueprint(post_bulk_bp)
api_bp.register_blueprint(score_bp)
api_bp.register_blueprint(tag_bp)
api_bp.register_blueprint(tags_bp)
api_bp.register_blueprint(user_bp)
