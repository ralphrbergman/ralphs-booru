from flask import Blueprint, render_template

index_bp = Blueprint(
    name = 'Index',
    import_name = __name__
)

@index_bp.route('/')
def index_page():
    return render_template('index.html')
