from os import getenv
from shutil import copy

from apiflask import APIBlueprint, abort
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage

from api import create_post, create_snapshot, delete_post, get_post, save_file
from api.decorators import api_level_required, owner_only, post_protect
from api_auth import auth
from db import Post, db
from db.schemas import PostFormIn, PostIn, PostOut

POSTING_LEVEL = int(getenv('POSTING_LEVEL'))

post_bp = APIBlueprint(
    name = 'Post API',
    import_name = __name__,
    url_prefix = '/post'
)

@post_bp.get('/<int:post_id>')
@post_bp.output(PostOut)
def obtain_post(post_id: int):
    return get_post(post_id)

@post_bp.delete('/<int:post_id>')
@post_bp.output({}, status_code = 204)
@post_bp.auth_required(auth)
@owner_only(Post)
def remove_post(post_id: int, post: Post):
    if not post:
        abort(404, message = 'Post not found.')

    delete_post(post)
    db.session.commit()

    return {}

@post_bp.patch('/<int:post_id>')
@post_bp.input(PostIn(partial = True), arg_name = 'data', schema_name = 'PostUpdate')
@post_bp.output(PostOut)
@post_bp.auth_required(auth)
@post_protect
@api_level_required(POSTING_LEVEL, Post)
def update_post(post_id: int, data: PostIn, post: Post):
    if not post:
        abort(404, message = 'Post not found.')

    for key, value in data.items():
        setattr(post, key, value)

    db.session.commit()
    return post

@post_bp.post('')
@post_bp.input(PostFormIn, arg_name = 'data', location = 'form_and_files')
@post_bp.output(PostOut(many = True))
@post_bp.auth_required(auth)
@post_protect
@api_level_required(POSTING_LEVEL, Post)
def upload_post(data: PostFormIn):
    files: list[FileStorage] = data['files']
    posts = list()

    for file in files:
        temp_path = save_file(file)
        post = create_post(
            current_user,
            temp_path,
            data.get('directory'),
            data.get('op'),
            data.get('src'),
            data.get('caption')
        )

        posted = False
        snapshot = create_snapshot(post, current_user)

        try:
            db.session.commit()
            posted = True
        except IntegrityError as exc:
            # Error likely of post that already exists.
            db.session.rollback()

            # Move back the file.
            copy(post.path, temp_path)
            post.path.unlink(missing_ok = True)

        if posted:
            posts.append(post)

    return posts
