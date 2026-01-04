from flask import Blueprint, request, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from api import browse_tag, delete_tag, get_tag
from api.decorators import post_protect
from db import db
from form import TagForm
from .utils import create_pagination_bar

tag_bp = Blueprint(
    name = 'Tag',
    import_name = __name__,
    url_prefix = '/tag'
)

TAG_TYPES = ('artist', 'character', 'copyright', 'general', 'meta')

@tag_bp.route('/edit/<int:tag_id>', methods = ['GET', 'POST'])
@login_required
@post_protect
def edit_page(tag_id: int):
    form = TagForm()
    tag = get_tag(tag_id)

    if not tag:
        return abort(404)

    if request.method == 'GET':
        return render_template('edit_tag.html', form = form, tag = tag, tag_types = TAG_TYPES)
    else:
        if form.deleted.data and current_user.is_authenticated and current_user.is_moderator:
            delete_tag(tag.id)

            flash(f'Permanently deleted tag #{tag.id}')
            return redirect(url_for('Tag.tag_page'))

        tag.name = form.name.data
        tag.type = form.type.data
        tag.desc = form.desc.data

        db.session.commit()

        flash(f'Updated tag {tag.id} successfully!')
        return redirect(url_for('Tag.edit_page', tag_id = tag_id))

@tag_bp.route('')
def tag_page():
    return redirect(url_for('Tag.tag_paged', page = 1))

@tag_bp.route('<int:page>')
def tag_paged(page: int):
    tags = browse_tag(page = page)

    bar = create_pagination_bar(
        tags.page,
        tags.pages,
        'Tag.tag_paged'
    )

    return render_template(
        'tag.html',
        bar = bar,
        current_page = tags.page,
        tags = tags
    )
