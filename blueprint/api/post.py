from os import getenv
from pathlib import Path

from apiflask import APIBlueprint
from flask_login import current_user, login_required
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from api import create_post, create_tag, delete_post, get_post, get_tag
from api.decorators import moderator_only, post_protect
from db import db
from db.schemas import FileIn, PostIn, PostsIn, PostOut, PostsOut

TEMP = Path(getenv('TEMP'))

post_bp = APIBlueprint(
    name = 'Post API',
    import_name = __name__,
    url_prefix = '/post'
)

@post_bp.delete('')
@post_bp.input(PostIn, arg_name = 'data')
@post_bp.output(PostOut)
@login_required
@moderator_only
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
@post_protect
def post_modify_route(data: PostsIn):
    posts = list()

    attrs = {
        'caption': data['caption'],
        'directory': data['directory'],
        'op': data['op'],
        'src': data['src'],
        'tags': data['tags']
    }

    for post_id in data['posts']:
        post = get_post(post_id)

        if not post:
            continue

        for attr, value in attrs.items():
            if attr != 'tags':
                setattr(post, attr, value)
            else:
                tags = list()

                try:
                    for tag_name in value:
                        tag = get_tag(tag_name) or create_tag(tag_name, [post])

                        tags.append(tag)
                except TypeError as exc:
                    pass

                setattr(post, attr, tags)

        db.session.commit()
        posts.append(post)

    return { 'posts': posts }
