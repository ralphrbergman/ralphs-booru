from flask import Blueprint

from .post import post_bp

api_bp = Blueprint(
    name = 'REST API',
    import_name = __name__,
    url_prefix = '/api'
)

api_bp.register_blueprint(post_bp)
