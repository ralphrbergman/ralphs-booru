from apiflask import APIBlueprint, abort
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from api import browse_tag, create_snapshot, create_tag, get_tag, get_post
from api.decorators import post_protect, perm_required
from api_auth import auth
from db import db
from db.schemas import BrowseIn, TagBulkIn, TagBulkOut, TagBrowse

tags_bp = APIBlueprint(
    name = 'Tags API',
    import_name = __name__,
    url_prefix = '/tags'
)

@tags_bp.get('')
@tags_bp.input(BrowseIn, arg_name = 'data', location = 'query')
@tags_bp.output(TagBrowse)
def get_tags(data: BrowseIn):
    """
    Browse multiple tags.
    """
    pagination = browse_tag(
        direction = data['sort_by'],
        limit = data['limit'],
        page = data['page'],
        sort = data['sort'],
        terms = data['terms']
    )

    return {
        'pages': pagination.pages,
        'tags': pagination.items
    }

@tags_bp.patch('/add')
@tags_bp.input(TagBulkIn, arg_name = 'data')
@tags_bp.output(TagBulkOut)
@tags_bp.auth_required(auth)
@post_protect
@perm_required('tag:edit')
def add_tags(data: TagBulkIn):
    """
    Add tags to multiple posts at once.
    You need tag:edit permission.
    """
    posts = []
    tags = []

    # Obtain posts.
    for post_id in data['post_ids']:
        post = get_post(post_id)

        if post:
            posts.append(post)

    # Obtain/Create tags and append to post tags.
    for tag_name in data['tags']:
        tag = get_tag(tag_name) or create_tag(tag_name)

        if tag:
            tags.append(tag)

    for post in posts:
        changed = False

        for tag in tags:
            if tag and tag not in post.tags:
                post.tags.append(tag)
                changed = True

        if changed:
            db.session.flush()
            create_snapshot(post, current_user)

    try:
        db.session.commit()
    except IntegrityError as exc:
        abort(500, message = f'Bulk operation failed: {exc}')

    return {
        'post_ids': [ post.id for post in posts ],
        'tags': tags
    }

@tags_bp.patch('/remove')
@tags_bp.input(TagBulkIn, arg_name = 'data')
@tags_bp.output(TagBulkOut)
@tags_bp.auth_required(auth)
@post_protect
@perm_required('tag:edit')
def remove_tags(data: TagBulkIn):
    """
    Remove multiple tags from multiple posts.
    You need tag:edit permission.
    """
    posts = []
    tags = []

    for post_id in data['post_ids']:
        post = get_post(post_id)

        if post:
            posts.append(post)

    for tag_name in data['tags']:
        tag = get_tag(tag_name)

        if tag:
            tags.append(tag)

    for post in posts:
        changed = False

        for tag in tags:
            if tag in post.tags:
                post.tags.remove(tag)
                changed = True

        if changed:
            db.session.flush()
            create_snapshot(post, current_user)

    try:
        db.session.commit()
    except IntegrityError as exc:
        abort(500, message = f'Bulk operation failed: {exc}')

    return {
        'post_ids': [ post.id for post in posts ],
        'tags': tags
    }
