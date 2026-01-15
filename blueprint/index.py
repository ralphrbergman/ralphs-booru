from flask import Blueprint, redirect, render_template, url_for

from api import count_all_posts
from form import SearchForm

index_bp = Blueprint(
    name = 'Index',
    import_name = __name__
)

@index_bp.route('/', methods = ['GET', 'POST'])
def index_page():
    form = SearchForm()

    if form.validate_on_submit():
        raw_query = form.search.data.strip()

        if 'nsfw' not in raw_query:
            raw_query = f'{raw_query} -nsfw' if len(raw_query) > 0 else '-nsfw'

        return redirect(url_for('Post.browse_paged', page = 1, terms = raw_query))

    count = count_all_posts()
    return render_template('index.html', count = str(count), form = form)
