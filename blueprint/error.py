from logging import getLogger

from flask import Blueprint, render_template
from flask_babel import gettext
from werkzeug.exceptions import HTTPException

from .utils import log_anon_activity

err_bp = Blueprint(
    name = 'Error Handler',
    import_name = __name__
)
logger = getLogger('app_logger')

def handle_error(code: int, message: str) -> None:
    return render_template(
        'error.html',
        code = code,
        message = message
    ), code

@err_bp.app_errorhandler(401)
def _401_handler(exception: HTTPException):
    log_anon_activity(logger.error, f'Unauthenticated access: {exception}')
    return handle_error(401, gettext('You need to login'))

@err_bp.app_errorhandler(403)
def _403_handler(exception: HTTPException):
    log_anon_activity(logger.error, f'Unauthorized access: {exception}')
    return handle_error(403, gettext('Unauthorized users prohibited'))

@err_bp.app_errorhandler(404)
def _404_handler(exception: HTTPException):
    log_anon_activity(logger.error, f'Invalid page: {exception}')
    return handle_error(
        404,
        gettext('The resource you we\'re looking for does not exist.')
    )
