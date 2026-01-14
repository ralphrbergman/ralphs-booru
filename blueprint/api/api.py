from flask import Blueprint

from .comment import comment_bp
from .post import post_bp
from .posts import posts_bp
from .score import score_bp

api_bp = Blueprint(
    name = 'REST API',
    import_name = __name__,
    url_prefix = '/api'
)

@api_bp.errorhandler(404)
def _404_handler(exc):
    return {'message': 'You are at the wrong place', 'code': 404}, 404

api_bp.register_blueprint(comment_bp)
api_bp.register_blueprint(post_bp)
api_bp.register_blueprint(posts_bp)
api_bp.register_blueprint(score_bp)
