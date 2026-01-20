from os import getenv

from flask import Blueprint, request, abort, flash, redirect, render_template, url_for
from flask_babel import gettext
from flask_login import current_user, login_required

from api import browse_tag, browse_snapshots, delete_tag, get_tag, get_snapshot, revert_snapshot
from api.decorators import level_required, post_protect
from db import db
from form import SnapshotForm, TagForm
from .utils import create_pagination_bar

TAGGING_LEVEL = int(getenv('TAGGING_LEVEL'))

tag_bp = Blueprint(
    name = 'Tag',
    import_name = __name__,
    url_prefix = '/tag'
)

TAG_TYPES = ('artist', 'character', 'copyright', 'general', 'meta')

@tag_bp.route('/edit/<int:tag_id>', methods = ['GET', 'POST'])
@login_required
@post_protect
@level_required(TAGGING_LEVEL)
def edit_page(tag_id: int):
    form = TagForm()
    tag = get_tag(tag_id)

    if not tag:
        return abort(404)

    if request.method == 'GET':
        return render_template('edit_tag.html', form = form, tag = tag, tag_types = TAG_TYPES)
    else:
        if form.deleted.data and current_user.is_authenticated and current_user.is_moderator:
            delete_tag(tag)

            flash(gettext('Permanently deleted tag #%(tag_name)s', tag_name = tag.name))
            return redirect(url_for('Root.Tag.tag_page'))

        tag.name = form.name.data
        tag.type = form.type.data
        tag.desc = form.desc.data

        db.session.commit()

        flash(gettext('Updated tag %(tag_name)s successfully!', tag_name = tag.name))
        return redirect(url_for('Root.Tag.edit_page', tag_id = tag_id))

@tag_bp.route('/history')
def history_page():
    form = SnapshotForm()

    post_id = form.post_id.data or request.args.get('post_id')

    snapshots = browse_snapshots(post_id = post_id)

    return render_template('snapshot.html', form = form, snapshots = snapshots)

@tag_bp.route('/revert/<int:snapshot_id>')
def revert_page(snapshot_id: int):
    snapshot = get_snapshot(snapshot_id)

    if not snapshot:
        return abort(404)

    snapshot = revert_snapshot(snapshot, current_user)

    return redirect(url_for('Root.Tag.history_page', post_id = snapshot.post_id))

@tag_bp.route('')
def tag_page():
    return redirect(url_for('Root.Tag.tag_paged', page = 1))

@tag_bp.route('<int:page>')
def tag_paged(page: int):
    tags = browse_tag(page = page)

    bar = create_pagination_bar(
        tags.page,
        tags.pages,
        'Root.Tag.tag_paged'
    )

    return render_template(
        'tag.html',
        bar = bar,
        current_page = tags.page,
        tags = tags
    )
