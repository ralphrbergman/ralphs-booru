from flask import Blueprint, request, abort, flash, redirect, render_template, send_file, url_for
from flask_login import current_user, login_required

from api import DEFAULT_LIMIT, DEFAULT_TERMS, DEFAULT_SORT, add_tags, browse_post, create_post, delete_post, get_post, move_post, replace_post, save_file
from api.decorators import post_protect
from db import db
from form import PostForm, UploadForm
from .utils import create_pagination_bar, flash_errors

DEFAULT_BLUR = 'true'

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
    sort_str = args.get('sort', default = DEFAULT_SORT)

    # Ensure all URI arguments are passed in the address.
    if len(args) < 2:
        return redirect(
            url_for(
                'Root.Post.browse_paged',
                blur = blur,
                limit = limit,
                page = page,
                terms = terms,
                sort = sort_str
            )
        )

    posts = browse_post(limit = limit, page = page, terms = terms, sort_str = sort_str)

    bar = create_pagination_bar(
        page,
        posts.pages,
        'Root.Post.browse_paged',
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

    if not post:
        return abort(404)

    if form.validate_on_submit():
        if current_user.is_authenticated:
            if (current_user == post.author or current_user.is_moderator):
                if form.deleted.data:
                    delete_post(post)

                    flash(f'Permanently deleted post #{post.id}')
                    return redirect(url_for('Root.Post.browse_page'))

                file = form.new_file.data

                if file:
                    post = replace_post(post, file)

                    if post:
                        flash(f'Successfully exchanged post #{post.id} for a new file!')
                    else:
                        flash('Failed to exchange post.')
                        return redirect(url_for('Root.Post.edit_page', post_id = post_id))

            post.op = form.op.data.strip()
            post.src = form.src.data.strip()
            post.caption = form.caption.data.strip()

            post.tags = add_tags(form.tags.data.split(' '))
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

            if post is not None:
                flash(f'Successfully uploaded post #{post.id}')
            else:
                flash(f'Uploading file {file.filename} failed')

        return redirect(url_for('Root.Post.browse_page'))

    flash_errors(form)

    return render_template('upload.html', form = form)
