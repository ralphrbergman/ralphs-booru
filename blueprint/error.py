from flask import Blueprint, render_template

err_bp = Blueprint(
    name = 'Error Handler',
    import_name = __name__
)

@err_bp.app_errorhandler(404)
def _404_handler(exc):
    return render_template(
        'error.html',
        code = 404,
        message = 'The resource you we\'re looking for does not exist.'
    ), 404
