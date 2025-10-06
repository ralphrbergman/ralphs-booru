from flask import Blueprint, render_template

from api import count_all_posts

index_bp = Blueprint(
    name = 'Index',
    import_name = __name__
)

@index_bp.route('/')
def index_page():
    count = count_all_posts()

    return render_template('index.html', count = str(count))
