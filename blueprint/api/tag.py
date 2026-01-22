from apiflask import APIBlueprint, abort

from api import browse_tag, create_tag, delete_tag, get_tag, get_post
from api.decorators import post_protect, perm_required
from api_auth import auth
from db import Tag, db
from db.schemas import TagIn, TagOut

tag_bp = APIBlueprint(
    name = 'Tag API',
    import_name = __name__,
    url_prefix = '/tag'
)

@tag_bp.get('/<int:tag_id>')
@tag_bp.output(TagOut)
def obtain_tag(tag_id: int):
    tag = get_tag(tag_id)

    if not tag:
        abort(404, message = 'No tag found.')

    return tag

@tag_bp.delete('/<int:tag_id>')
@tag_bp.output({}, status_code = 204)
@tag_bp.auth_required(auth)
def remove_tag(tag_id: int):
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
@perm_required('tag:upload')
def upload_tag(data: TagIn):
    tag = create_tag(data['name'])

    tag.name = data['name']
    tag.type = data['type']
    tag.desc = data['desc']

    for post_id in data.get('post_ids'):
        post = get_post(post_id)
        if not post: continue

        tag.posts.append(post)

    db.session.commit()
    return tag

@tag_bp.patch('')
@tag_bp.input(TagIn(partial = True), arg_name = 'data', schema_name = 'TagUpdate')
@tag_bp.output(TagOut)
@tag_bp.auth_required(auth)
@post_protect
@perm_required('tag:edit')
def update_tag(data: TagIn):
    tag = get_tag(data['name'])

    if not tag:
        abort(404, message = 'Tag not found.')

    data.pop('post_ids', None)

    for key, value in data.items():
        setattr(tag, key, value)

    db.session.commit()
    return tag
