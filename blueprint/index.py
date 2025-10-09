from flask import Blueprint, request, redirect, render_template, url_for

from api import count_all_posts
from form import SearchForm

index_bp = Blueprint(
    name = 'Index',
    import_name = __name__
)

@index_bp.route('/', methods = ['GET', 'POST'])
def index_page():
    form = SearchForm()

    if request.method == 'GET':
        count = count_all_posts()

        return render_template('index.html', count = str(count), form = form)
    else:
        return redirect(url_for('Post.browse_paged', page = 1, tags = form.search.data))
