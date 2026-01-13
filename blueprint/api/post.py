from os import getenv
from pathlib import Path

from apiflask import APIBlueprint
from flask_login import current_user, login_required
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from api import create_post, create_tag, delete_post, get_post, get_tag
from api.decorators import appropriate_user_only, post_protect
from db import Tag, db
from db.schemas import FileIn, PostIn, PostsIn, PostOut, PostsOut

TEMP = Path(getenv('TEMP_PATH'))

post_bp = APIBlueprint(
    name = 'Post API',
    import_name = __name__,
    url_prefix = '/post'
)

@post_bp.delete('')
@post_bp.input(PostIn, arg_name = 'data')
@post_bp.output(PostOut)
@login_required
@appropriate_user_only
@post_protect
def post_del_route(data: PostIn):
    post = get_post(data['post_id'])

    if post:
        delete_post(post)

    return post

@post_bp.get('')
@post_bp.input(PostIn, arg_name = 'data')
@post_bp.output(PostOut)
def post_get_route(data: PostIn):
    post = get_post(data['post_id'])

    return post

@post_bp.post('')
@post_bp.input(FileIn, arg_name = 'data', location = 'files')
@post_bp.output(PostsOut)
@login_required
@post_protect
def post_upload_route(data: FileIn):
    files: list[FileStorage] = data['files']

    posts = list()

    for file in files:
        temp_path = TEMP / secure_filename(file.filename)
        file.save(temp_path)

        post = create_post(author = current_user, path = temp_path)
        posts.append(post)

    return { 'posts': posts }

@post_bp.patch('')
@post_bp.input(PostsIn, arg_name = 'data')
@post_bp.output(PostsOut)
@login_required
@appropriate_user_only
@post_protect
def post_modify_route(data: PostsIn):
    attrs = {
        'caption': data.get('caption'),
        'directory': data.get('directory'),
        'op': data.get('op'),
        'src': data.get('src'),
        'tags': data.get('tags')
    }
    add_tags = data.get('add_tags')
    rem_tags = data.get('rem_tags')

    posts = list()

    def query_tags(tag_names: list[str]) -> list[Tag]:
        tags = list()

        for tag_name in tag_names:
            tag = get_tag(tag_name) or create_tag(tag_name)

            tags.append(tag)

        return tags

    for post_id in data['posts']:
        post = get_post(post_id)
        if not post: continue

        for attr, value in attrs.items():
            if value is None: continue

            if attr != 'tags':
                # Handle basic attributes of post.
                setattr(post, attr, value)
            else:
                # Handle overriding tags.
                tags = query_tags(value)
                post.tags = tags

        if add_tags:
            # Handle adding tags.
            tags = query_tags(add_tags)

            post.tags = post.tags + tags

        if rem_tags:
            # Handle removing tags.
            tags = query_tags(rem_tags)

            for tag in tags:
                post.tags.remove(tag)

        db.session.commit()
        posts.append(post)

    return {'posts': posts}
