from math import floor
from os import getenv
from pathlib import Path
from shutil import copy
from typing import Optional

from flask import Blueprint, request, flash, redirect, render_template, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_, select

from api import create_post, create_tag, delete_post, get_post, get_tag
from api.decorators import post_protect
from db import db, Post, Tag
from form import PostForm, UploadForm

CONTENT_PATH = Path(getenv('CONTENT_PATH'))
TEMP = Path(getenv('TEMP'))

post_bp = Blueprint(
    name = 'Post',
    import_name = __name__
)

DEFAULT_LIMIT = 20
PAGINATION_DEPTH = 5

def create_pagination_bar(current_page: int, total_pages: int, **kwargs) -> list[dict]:
    bar = list()

    def add_item(page: int, display_value: Optional[str] = None) -> None:
        bar.append({
            'page': display_value or page,
            'url': url_for('Post.browse_paged', page = page, **kwargs)
        })

    if current_page > 1:
        if current_page - 1 > PAGINATION_DEPTH:
            add_item(1, '<<')

        add_item(current_page - 1, '<')

        # Count pages backwards.
        for index, page in enumerate(range(max(current_page - PAGINATION_DEPTH, 1), current_page)):
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
    terms = args.get('terms', '-nsfw')

    stmt = select(Post).order_by(
        Post.id.desc()
    )

    for term in terms.split():
        try:
            # It's an attribute

            name, value = term.split(':', 1)
            col = getattr(Post, name)

            if not len(value):
                # Look for posts that don't have the column set.
                where = or_(col == None, col == '')
            else:
                where = col == value
        except ValueError:
            # It's a tag

            if term[0] != '-':
                where = Post.tags.any(Tag.name == term)
            else:
                where = ~Post.tags.any(Tag.name == term[1:])

        stmt = stmt.where(where)

    posts = db.paginate(
        stmt,
        page = page,
        per_page = limit
    )

    bar = create_pagination_bar(page, posts.pages, limit = limit, terms = terms)

    return render_template(
        'browse.html',
        bar = bar,
        current_page = page,
        posts = posts
    )

@post_bp.route('/edit/<int:post_id>', methods = ['GET', 'POST'])
@login_required
@post_protect
def edit_page(post_id: int):
    form = PostForm()
    post = get_post(post_id)

    if request.method == 'GET':
        return render_template('edit.html', form = form, post = post)
    else:
        if form.validate_on_submit():
            if form.deleted.data and current_user.is_authenticated and current_user.is_moderator:
                delete_post(post)

                flash(f'Permanently deleted post #{post.id}')
                return redirect(url_for('Post.browse_page'))

            directory = form.directory.data
            original_path = post.path

            post.directory = directory
            post.op = form.op.data
            post.src = form.src.data
            post.caption = form.caption.data

            new_tags = list()

            for tag_name in form.tags.data.split(' '):
                if len(tag_name) == 0:
                    break

                tag = get_tag(tag_name)

                if not tag:
                    tag = create_tag(tag_name)

                new_tags.append(tag)

            post.tags = new_tags

            # Move file to new directory.
            new_dir = CONTENT_PATH / Path(directory)
            new_dir.mkdir(exist_ok = True, parents = True)
            new_path = new_dir / post.name

            if new_path != original_path:
                copy(original_path, new_path)
                original_path.unlink(missing_ok = True)

            db.session.commit()

            return redirect(url_for('Post.view_page', post_id = post_id))

        # So far there isn't anything that will invalidate the form.
        # So I guess there's no point in displaying errors?

@post_bp.route('/view/<int:post_id>')
def view_page(post_id: int):
    return render_template('view.html', post = get_post(post_id))

@post_bp.route('/view_f/<int:post_id>')
def view_file_resource(post_id: int):
    post = get_post(post_id)

    return send_file(post.path)

@post_bp.route('/upload', methods = ['GET', 'POST'])
@login_required
@post_protect
def upload_page():
    form = UploadForm()

    if request.method == 'GET':
        return render_template('upload.html', form = form)
    else:
        if form.validate_on_submit():
            for file in form.files.data:
                temp_path = TEMP / file.filename
                file.save(temp_path)

                post = create_post(
                    author = current_user,
                    path = temp_path,
                    op = form.op.data,
                    src = form.src.data,
                    directory = form.directory.data,
                    caption = form.caption.data,
                    tags = form.tags.data
                )

                if post is not None:
                    flash(f'Successfully uploaded post #{post.id}')
                else:
                    flash(f'Uploading file {file.filename} failed')

            return redirect(url_for('Post.browse_page'))
        else:
            for field in form.errors.values():
                for error in field:
                    flash(error)

        return redirect(url_for('Post.upload_page'))
