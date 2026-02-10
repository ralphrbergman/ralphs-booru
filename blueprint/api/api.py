from flask import (
    Blueprint,
    Request,
    request,
    jsonify,
    make_response,
    redirect,
    url_for
)
from login import login_manager

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

@login_manager.unauthorized_handler
def unauthorized_callback():
    """
    Function that runs whenever unauthorized access happens.
    This points the user in a direction depending if it's an API call seeking
    JSON or a frontend user needing to see the beautiful HTML document.
    """
    if request.path.startswith('/api'):
        response = make_response(jsonify({
            'message': 'Authentication is required.',
            'status': 401
        }), 401)

        return response
    else:
        return redirect(url_for(login_manager.login_view, next = request.url))

@api_bp.errorhandler(404)
def _404_handler(exc):
    """
    Function ran whenever an invalid endpoint is visited.
    """
    return {
        'message': 'You are at the wrong place',
        'code': 404
    }, 404

@login_manager.request_loader
def load_user_from_request(request: Request):
    """
    Function that runs before a request processing
    to validate a user's API key.
    It returns the appropriate user from passed API key.
    """
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
