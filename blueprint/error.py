from flask import Blueprint, render_template
from flask_babel import gettext

err_bp = Blueprint(
    name = 'Error Handler',
    import_name = __name__
)

@err_bp.app_errorhandler(401)
def _401_handler(exc):
    return render_template(
        'error.html',
        code = 401,
        message = gettext('Unauthorized users prohibited')
    )

@err_bp.app_errorhandler(404)
def _404_handler(exc):
    return render_template(
        'error.html',
        code = 404,
        message = gettext('The resource you we\'re looking for does not exist.')
    ), 404
