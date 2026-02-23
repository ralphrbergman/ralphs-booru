from logging import getLogger
from pathlib import Path
from shutil import copy

from flask import (
    Blueprint,
    request,
    abort,
    flash,
    redirect,
    render_template,
    send_file,
    url_for
)
from flask_babel import gettext
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from api import (
    DEFAULT_LIMIT,
    DEFAULT_TERMS,
    DEFAULT_SORT,
    DEFAULT_SORT_DIR,
    add_tags,
    browse_post,
    create_post,
    create_snapshot,
    delete_log,
    delete_post,
    get_post,
    move_post,
    perma_delete_post,
    replace_post,
    save_file
)
from api.decorators import (
    owner_or_perm_required,
    post_protect,
    perm_required
)
from db import Post, db
from form import PostForm, PostRemovalForm, UploadForm
from .utils import create_pagination_bar, flash_errors, log_user_activity

DEFAULT_BLUR = 'true'

post_bp = Blueprint(
    name = 'Post',
    import_name = __name__
)
logger = getLogger('app_logger')

@post_bp.route('/browse')
def browse_page():
    return redirect(url_for('Root.Post.browse_paged', page = 1))

@post_bp.route('/browse/<int:page>')
def browse_paged(page: int):
    args = request.args

    blur = args.get('blur', default = DEFAULT_BLUR)
    limit = args.get('limit', default = DEFAULT_LIMIT, type = int)
    search = args.get('search', default = DEFAULT_TERMS)
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
                search = search,
                sort = sort,
                sort_direction = sort_direction
            )
        )

    pagination = browse_post(
        direction = sort_direction,
        limit = limit,
        page = page,
        terms = search,
        sort = sort
    )

    bar = create_pagination_bar(
        page,
        pagination.pages,
        'Root.Post.browse_paged',
        **request.args
    )

    return render_template(
        'browse.html',
        bar = bar,
        blur = blur == 'true',
        current_page = page,
        posts = pagination,
        search = search
    )

@post_bp.route('/edit/<int:post_id>', methods = ['GET', 'POST'])
@login_required
@post_protect
@owner_or_perm_required(Post, 'post:edit')
def edit_page(post_id: int, post: Post):
    form = PostForm()

    if not post:
        return abort(404)

    if form.validate_on_submit() and current_user.is_authenticated and\
    (current_user == post.author or current_user.is_moderator):
        mod_paths: set[Path] = set()

        if form.deleted.data:
            log_user_activity(logger.info, 'wants to delete post.')
            return redirect(
                url_for('Root.Post.remove_page', post_id = post_id)
            )
        elif post.removed:
            log_user_activity(logger.info, 'wants to revert deleted post.')
            return redirect(
                url_for('Root.Post.revert_page', post_id = post_id)
            )

        file = form.new_file.data

        if file:
            # new_path refers to the uploaded file.
            # whilst old_path refers to the post file before exchange.
            post, new_path, old_path = replace_post(post, file)
            mod_paths.add(new_path)
            mod_paths.add(old_path)

            if post:
                log_user_activity(logger.info, f'exchanged post #{post.id}')
                flash(
                    gettext(
                        'Successfully exchanged post #%(post_id)s'
                        ' for a new file!',
                        post_id = post.id
                    )
                )
            else:
                log_user_activity(
                    logger.error,
                    f'wanted to but failed post exchange #{post.id}'
                )
                flash(gettext('Failed to exchange post.'))

                return redirect(
                    url_for('Root.Post.edit_page', post_id = post_id)
                )

        try:
            db.session.commit()
        except IntegrityError as exception:
            db.session.rollback()
            return
        except Exception as exception:
            log_user_activity(logger.error, f'exception: {exception}')
            db.session.rollback()
            return

        # Take care of temporary files.
        for path in mod_paths:
            path.unlink(missing_ok = True)

        original_tags = post.tags

        post.op = form.op.data.strip()
        post.src = form.src.data.strip()
        post.caption = form.caption.data.strip()

        try:
            post.tags = add_tags(form.tags.data.split())
        except AttributeError as exception:
            # Form tags is None, likely because the user can't manage tags.
            pass

        if post.tags != original_tags:
            db.session.flush()
            create_snapshot(post, current_user)

        move_post(post, form.directory.data.strip())

        db.session.commit()

        log_user_activity(
            logger.info,
            f'successfully modified post #{post.id}.'
        )
        return redirect(url_for('Root.Post.view_page', post_id = post_id))

    flash_errors(form)

    return render_template('edit.html', form = form, post = post)

@post_bp.route('/view/<int:post_id>')
def view_page(post_id: int):
    post = get_post(post_id)

    if not post:
        return abort(404)

    if post.removed:
        flash(
            f'This post has been marked deleted.<br>Reason: {post.log.reason}'
        )

    return render_template('view.html', post = post)

@post_bp.route('/view_f/<int:post_id>')
def view_file_resource(post_id: int):
    post = get_post(post_id)

    try:
        return send_file(post.path)
    except FileNotFoundError as exception:
        return abort(404)

@post_bp.route('/remove/<int:post_id>', methods = ['GET', 'POST'])
@login_required
@owner_or_perm_required(Post, 'post:delete')
def remove_page(post_id: int, post: Post):
    if not post:
        return abort(404)

    form = PostRemovalForm()

    if form.validate_on_submit():
        if form.perma.data:
            perma_delete_post(post)
            log_user_activity(
                logger.info,
                f'permanently deleted post #{post.id}.'
            )
        else:
            delete_post(post, current_user, form.reason.data)
            log_user_activity(
                logger.info,
                f'marked post #{post.id} as deleted.'
            )

        db.session.commit()

        if form.perma.data:
            flash(gettext('Permanently deleted post #%(post_id)s.', post_id = post.id))
        else:
            flash(
                gettext(
                    'Marked post #%(post_id)s as deleted.',
                    post_id = post.id
                )
            )

        return redirect(url_for('Root.Post.browse_page'))

    flash_errors(form)

    return render_template('delete_form.html', form = form)

@post_bp.route('/revert/<int:post_id>', methods = ['GET', 'POST'])
@login_required
@owner_or_perm_required(Post, 'post:delete')
def revert_page(post_id: int, post: Post):
    if post.removed:
        delete_log(post)

    db.session.commit()
    log_user_activity(logger.info, f'restored post #{post.id}.')
    return redirect(url_for('Root.Post.view_page', post_id = post_id))

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
            db.session.flush()
            create_snapshot(post, current_user)

            try:
                db.session.commit()
                posted = True
            except IntegrityError as exception:
                # Error likely of post that already exists.
                db.session.rollback()

                # Move back the file.
                copy(post.path, temp_path)
                post.path.unlink(missing_ok = True)

                log_user_activity(
                    logger.error,
                    f'failed upload, exception: {exception}'
                )

            if posted:
                flash(
                    gettext(
                        'Successfully uploaded post #%(post_id)s',
                        post_id = post.id
                    )
                )
                log_user_activity(
                    logger.debug,
                    f'successfully posted #{post.id}'
                )
            else:
                flash(
                    gettext(
                        'Uploading file %(filename)s failed',
                        filename = file.filename
                    )
                )

        return redirect(url_for('Root.Post.browse_page'))

    flash_errors(form)

    return render_template('upload.html', form = form)
