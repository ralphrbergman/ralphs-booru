from apiflask import APIBlueprint
from flask_login import current_user

from api import browse_tag, create_snapshot, create_tag, get_tag, get_post
from api.decorators import post_protect, perm_required
from api_auth import auth
from db import db
from db.schemas import TagBulkIn, TagBulkOut

tags_bp = APIBlueprint(
    name = 'Tags API',
    import_name = __name__,
    url_prefix = '/tags'
)

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
        tag = get_tag(tag_name)

        if not tag:
            tag = create_tag(tag_name)

        tags.append(tag)

        for post in posts:
            if tag not in post.tags:
                post.tags.append(tag)
                create_snapshot(post, current_user)

    db.session.commit()
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

        if not tag:
            continue

        tags.append(tag)

        for post in posts:
            if tag in post.tags:
                post.tags.remove(tag)
                create_snapshot(post, current_user)

    db.session.commit()
    return {
        'post_ids': [ post.id for post in posts ],
        'tags': tags
    }
