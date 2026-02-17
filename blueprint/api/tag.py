from apiflask import APIBlueprint, abort
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from api import create_snapshot, create_tag, delete_tag, get_tag, get_post
from api.decorators import post_protect, perm_required
from api_auth import auth
from db import db
from db.schemas import TagIn, TagsIn, TagOut, TagsOut

tag_bp = APIBlueprint(
    name = 'Tag API',
    import_name = __name__,
    url_prefix = '/tag'
)

@tag_bp.get('/<int:tag_id>')
@tag_bp.output(TagOut)
def obtain_tag(tag_id: int):
    """
    Get information about a tag.
    """
    tag = get_tag(tag_id)

    if not tag:
        abort(404, message = 'No tag found.')

    return tag

@tag_bp.delete('/<int:tag_id>')
@tag_bp.output({}, status_code = 204)
@tag_bp.auth_required(auth)
@perm_required('tag:edit')
def remove_tag(tag_id: int):
    """
    Deletes a tag.
    You need a tag:edit permission for this.
    """
    tag = get_tag(tag_id)

    if not tag:
        abort(404, message = 'Tag not found.')

    delete_tag(tag)

    return {}

@tag_bp.post('')
@tag_bp.input(TagIn, arg_name = 'data')
@tag_bp.output(TagOut)
@tag_bp.auth_required(auth)
@post_protect
@perm_required('tag:edit')
def upload_tag(data: TagIn):
    """
    Creates new tag.
    You must have the tag:edit permission to do this.
    """
    posts = []

    for post_id in data.get('post_ids'):
        post = get_post(post_id)
        if not post: continue

        posts.append(post)

    tag = get_tag(data['name']) or create_tag(data['name'], posts)

    if not tag:
        return abort(400, message = 'Invalid tag name.')

    tag.type = data['type']
    tag.desc = data['desc']

    # Create tag snapshots for the posts.
    for post in posts:
        db.session.flush()
        create_snapshot(post, current_user)

    try:
        db.session.commit()
        return tag
    except IntegrityError as exception:
        db.session.rollback()
        return

@tag_bp.patch('')
@tag_bp.input(
    TagIn(partial = True),
    arg_name = 'data',
    schema_name = 'TagUpdate'
)
@tag_bp.output(TagOut)
@tag_bp.auth_required(auth)
@post_protect
@perm_required('tag:edit')
def update_tag(data: TagIn):
    """
    Updates given tag.
    You must have the tag:edit permission.
    """
    tag = get_tag(data['name'])

    if not tag:
        abort(404, message = 'Tag not found.')

    data.pop('post_ids', None)

    for key, value in data.items():
        setattr(tag, key, value)

    db.session.commit()
    return tag

@tag_bp.patch('/add')
@tag_bp.input(TagsIn, arg_name = 'data')
@tag_bp.output(TagsOut)
@tag_bp.auth_required(auth)
@post_protect
@perm_required('tag:edit')
def add_tags(data: TagsIn):
    """
    Add tags to post.
    You need tag:edit permission for this API call.
    """
    post = get_post(data['post_id'])

    for tag_name in data['tags']:
        tag = get_tag(tag_name) or create_tag(tag_name)

        if tag and tag not in post.tags:
            post.tags.append(tag)

    db.session.flush()
    create_snapshot(post, current_user)
    db.session.commit()

    return {
        'post_id': post.id,
        'tags': post.tags
    }

@tag_bp.patch('/remove')
@tag_bp.input(TagsIn, arg_name = 'data')
@tag_bp.output(TagsOut)
@tag_bp.auth_required(auth)
@post_protect
@perm_required('tag:edit')
def remove_tags(data: TagsIn):
    """
    Remove tags from post.
    You need tag:edit permission for this API call.
    """
    post = get_post(data['post_id'])

    for tag_name in data['tags']:
        tag = get_tag(tag_name)

        if tag and tag in post.tags:
            post.tags.remove(tag)

    db.session.flush()
    create_snapshot(post, current_user)
    db.session.commit()

    return {
        'post_id': post.id,
        'tags': post.tags
    }
