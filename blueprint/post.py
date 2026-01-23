from os import getenv
from shutil import copy

from flask import Blueprint, request, abort, flash, redirect, render_template, send_file, url_for
from flask_babel import gettext
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from api import DEFAULT_LIMIT, DEFAULT_TERMS, DEFAULT_SORT, DEFAULT_SORT_DIR, add_tags, browse_post, create_post, create_snapshot, delete_post, get_post, move_post, replace_post, save_file
from api.decorators import post_protect, perm_required
from db import db
from form import PostForm, UploadForm
from .utils import create_pagination_bar, flash_errors

DEFAULT_BLUR = getenv('DEFAULT_BLUR') == 'on'

post_bp = Blueprint(
    name = 'Post',
    import_name = __name__
)

@post_bp.route('/browse')
def browse_page():
    return redirect(url_for('Root.Post.browse_paged', page = 1))

@post_bp.route('/browse/<int:page>')
def browse_paged(page: int):
    args = request.args

    blur = args.get('blur', default = DEFAULT_BLUR)
    limit = args.get('limit', default = DEFAULT_LIMIT, type = int)
    terms = args.get('terms', default = DEFAULT_TERMS)
    sort = args.get('sort', default = DEFAULT_SORT)
    sort_direction = args.get('sort_direction', default = DEFAULT_SORT_DIR)

    # Ensure all URI arguments are passed in the address.
    if len(args) < 2:
        return redirect(
            url_for(
                'Root.Post.browse_paged',
                blur = blur,
                limit = limit,
                page = page,
                terms = terms,
                sort = sort,
                sort_direction = sort_direction
            )
        )

    posts = browse_post(
        direction = sort_direction,
        limit = limit,
        page = page,
        terms = terms,
        sort = sort
    )

    bar = create_pagination_bar(
        page,
        posts.pages,
        'Root.Post.browse_paged',
        **request.args
    )

    return render_template(
        'browse.html',
        bar = bar,
        blur = blur,
        current_page = page,
        posts = posts
    )

@post_bp.route('/edit/<int:post_id>', methods = ['GET', 'POST'])
@login_required
@post_protect
@perm_required('post:edit')
def edit_page(post_id: int):
    form = PostForm()
    post = get_post(post_id)

    if not post:
        return abort(404)

    if form.validate_on_submit():
        if current_user.is_authenticated:
            if (current_user == post.author or current_user.is_moderator):
                if form.deleted.data:
                    delete_post(post)

                    db.session.commit()
                    flash(gettext('Permanently deleted post #%(post_id)s', post_id = post.id))
                    return redirect(url_for('Root.Post.browse_page'))

                file = form.new_file.data

                if file:
                    post = replace_post(post, file)

                    if post:
                        flash(gettext('Successfully exchanged post #%(post_id)s for a new file!', post_id = post.id))
                    else:
                        flash(gettext('Failed to exchange post.'))

                        return redirect(url_for('Root.Post.edit_page', post_id = post_id))

            db.session.commit()
            original_tags = post.tags

            post.op = form.op.data.strip()
            post.src = form.src.data.strip()
            post.caption = form.caption.data.strip()

            try:
                post.tags = add_tags(form.tags.data.split(' '))
            except AttributeError as exc:
                # Form tags is None, likely because the user can't manage tags.
                pass

            if post.tags != original_tags:
                hist = create_snapshot(post, current_user)

            move_post(post, form.directory.data.strip())

            db.session.commit()

            return redirect(url_for('Root.Post.view_page', post_id = post_id))

    flash_errors(form)

    return render_template('edit.html', form = form, post = post)

@post_bp.route('/view/<int:post_id>')
def view_page(post_id: int):
    post = get_post(post_id)

    if not post:
        return abort(404)

    return render_template('view.html', post = post)

@post_bp.route('/view_f/<int:post_id>')
def view_file_resource(post_id: int):
    post = get_post(post_id)

    try:
        return send_file(post.path)
    except FileNotFoundError as exc:
        return b''

@post_bp.route('/upload', methods = ['GET', 'POST'])
@login_required
@post_protect
@perm_required('post:upload')
def upload_page():
    form = UploadForm()

    if form.validate_on_submit():
        for file in form.files.data:
            temp_path = save_file(file)

            post = create_post(
                author = current_user,
                path = temp_path,
                op = form.op.data.strip(),
                src = form.src.data.strip(),
                directory = form.directory.data.strip(),
                caption = form.caption.data.strip(),
                tags = form.tags.data
            )

            posted = False
            create_snapshot(post, current_user)

            try:
                db.session.commit()
                posted = True
            except IntegrityError as exc:
                # Error likely of post that already exists.
                db.session.rollback()

                # Move back the file.
                copy(post.path, temp_path)
                post.path.unlink(missing_ok = True)

            if posted:
                flash(gettext('Successfully uploaded post #%(post_id)s', post_id = post.id))
            else:
                flash(gettext('Uploading file %(filename)s failed', filename = file.filename))

        return redirect(url_for('Root.Post.browse_page'))

    flash_errors(form)

    return render_template('upload.html', form = form)
