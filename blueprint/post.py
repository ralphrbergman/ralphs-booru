from math import floor
from pathlib import Path
from typing import Optional

from flask import Blueprint, request, flash, redirect, render_template, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy import select

from api import create_post, get_post
from db import db, Post
from form import UploadForm

post_bp = Blueprint(
    name = 'Post',
    import_name = __name__
)

DEFAULT_LIMIT = 20
PAGINATION_DEPTH = 5

def create_pagination_bar(current_page: int, limit: int, total_pages: int) -> list[dict]:
    bar = list()

    def add_item(page: int, display_value: Optional[str] = None) -> None:
        bar.append({
            'page': display_value or page,
            'url': url_for('Post.browse_paged', page = page, limit = limit)
        })

    if current_page > 1:
        if current_page - 1 > PAGINATION_DEPTH:
            add_item(1, '<<')

        add_item(current_page - 1, '<')

        # Count pages backwards.
        for index, page in enumerate(range(max(current_page - PAGINATION_DEPTH, 1), current_page)):
            if index == PAGINATION_DEPTH:
                break

            add_item(page)

    add_item(current_page)

    if current_page < total_pages:
        # Now forwards.
        for index, page in enumerate(range(current_page + 1, total_pages + 1)):
            if index == PAGINATION_DEPTH:
                break

            add_item(page)

        add_item(current_page + 1, '>')

        if current_page < total_pages - floor(PAGINATION_DEPTH):
            add_item(total_pages, '>>')

    return bar

@post_bp.route('/browse')
def browse_page():
    return redirect(url_for('Post.browse_paged', page = 1))

@post_bp.route('/browse/<int:page>')
def browse_paged(page: int):
    args = request.args

    limit = args.get('limit', DEFAULT_LIMIT, type = int)

    posts = db.paginate(
        select(Post).order_by(
            Post.id.desc()
        ),
        page = page,
        per_page = limit
    )

    bar = create_pagination_bar(page, limit, posts.pages)

    return render_template(
        'browse.html',
        bar = bar,
        current_page = page,
        posts = posts
    )

@post_bp.route('/view/<int:post_id>')
def view_page(post_id: int):
    return render_template('view.html', post = get_post(post_id))

@post_bp.route('/view_f/<int:post_id>')
def view_file_resource(post_id: int):
    post = get_post(post_id)

    return send_file(post.path)

@post_bp.route('/upload', methods = ['GET', 'POST'])
@login_required
def upload_page():
    form = UploadForm()

    if request.method == 'GET':
        return render_template('upload.html', form = form)
    else:
        if form.validate_on_submit():
            for file in form.files.data:
                temp_path = Path('temp') / file.filename
                file.save(temp_path)

                post = create_post(
                    author = current_user,
                    path = temp_path,
                    directory = form.directory.data,
                    caption = form.caption.data,
                    tags = form.tags.data
                )

                flash(f'Successfully uploaded post #{post.id}')

            return redirect(url_for('Post.browse_page'))
        else:
            for field in form.errors.values():
                for error in field:
                    flash(error)

        return redirect(url_for('Post.upload_page'))
