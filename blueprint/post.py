from os import getenv
from pathlib import Path
from shutil import copy

from flask import Blueprint, request, flash, redirect, render_template, send_file, url_for
from flask_login import current_user, login_required

from api import DEFAULT_LIMIT, DEFAULT_TERMS, DEFAULT_SORT, browse_post, create_post, create_tag, delete_post, get_post, get_tag, replace_post
from api.decorators import post_protect
from db import db
from form import PostForm, UploadForm
from .utils import create_pagination_bar

CONTENT_PATH = Path(getenv('CONTENT_PATH'))
DEFAULT_BLUR = 'true'
TEMP = Path(getenv('TEMP'))

post_bp = Blueprint(
    name = 'Post',
    import_name = __name__
)

@post_bp.route('/browse')
def browse_page():
    return redirect(url_for('Post.browse_paged', page = 1))

@post_bp.route('/browse/<int:page>')
def browse_paged(page: int):
    args = request.args

    blur = args.get('blur', default = DEFAULT_BLUR)
    limit = args.get('limit', default = DEFAULT_LIMIT, type = int)
    terms = args.get('terms', default = DEFAULT_TERMS)
    sort_str = args.get('sort', default = DEFAULT_SORT)

    # Ensure all URI arguments are passed in the address.
    if len(args) < 2:
        return redirect(
            url_for(
                'Post.browse_paged',
                blur = blur,
                limit = limit,
                page = page,
                terms = terms,
                sort = sort_str
            )
        )

    posts = browse_post(limit, page, terms, sort_str)

    bar = create_pagination_bar(
        page,
        posts.pages,
        'Post.browse_paged',
        blur = blur,
        limit = limit,
        terms = terms,
        sort = sort_str
    )

    return render_template(
        'browse.html',
        bar = bar,
        blur = blur.lower() == 'true',
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
            if current_user.is_authenticated and current_user.is_moderator:
                file = form.new_file.data

                if form.deleted.data:
                    delete_post(post)

                    flash(f'Permanently deleted post #{post.id}')
                    return redirect(url_for('Post.browse_page'))

                if file:
                    temp_path = TEMP / file.filename
                    file.save(temp_path)

                    post = replace_post(post, temp_path)

                    if post:
                        flash(f'Successfully exchanged post #{post.id} for a new file!')

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
