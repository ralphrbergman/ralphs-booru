from shutil import copy

from apiflask import APIBlueprint, abort
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import FileStorage

from api import browse_post, create_post, create_snapshot, delete_post, get_post, save_file
from api.decorators import owner_or_perm_required, post_protect, perm_required
from api_auth import auth
from db import Post, db
from db.schemas import BrowseIn, PostBrowse, PostFormIn, PostIn, PostDeleteIn, PostOut

post_bp = APIBlueprint(
    name = 'Post API',
    import_name = __name__
)

@post_bp.get('/posts')
@post_bp.input(BrowseIn, arg_name = 'data', location = 'query')
@post_bp.output(PostBrowse)
def get_posts(data: BrowseIn):
    """
    Browse multiple posts.
    """
    pagination = browse_post(
        direction = data['sort_by'],
        limit = data['limit'],
        page = data['page'],
        sort = data['sort'],
        terms = data['terms']
    )

    return {
        'pages': pagination.pages,
        'posts': pagination.items
    }

@post_bp.get('/post/<post_id>')
@post_bp.output(PostOut)
def obtain_post(post_id: str):
    """
    Returns a specified post by its ID or MD5 hash sum.
    """
    if post_id.isdecimal():
        post_id = int(post_id)

    return get_post(post_id)

@post_bp.delete('/post/<int:post_id>')
@post_bp.input(PostDeleteIn, arg_name = 'data', location = 'query')
@post_bp.output({}, status_code = 204)
@post_bp.auth_required(auth)
@owner_or_perm_required(Post, 'post:delete')
def remove_post(data: PostDeleteIn, post_id: int, post: Post):
    """
    Marks post as removed.
    Only the author of the post can do this,
    as well as people with post:delete permission.
    """
    if not post:
        abort(404, message = 'Post not found.')

    delete_post(post, current_user, data['reason'])
    db.session.commit()

    return {}

@post_bp.patch('/post/<int:post_id>')
@post_bp.input(
    PostIn(partial = True),
    arg_name = 'data',
    schema_name = 'PostUpdate'
)
@post_bp.output(PostOut)
@post_bp.auth_required(auth)
@post_protect
@owner_or_perm_required(Post, 'post:edit')
def update_post(post_id: int, data: PostIn, post: Post):
    """
    Update post.
    Author or people with post:edit permission can do this.
    """
    if not post:
        abort(404, message = 'Post not found.')

    for key, value in data.items():
        setattr(post, key, value)

    db.session.commit()
    return post

@post_bp.post('/post')
@post_bp.input(PostFormIn, arg_name = 'data', location = 'form_and_files')
@post_bp.output(PostOut(many = True))
@post_bp.auth_required(auth)
@post_protect
@perm_required('post:upload')
def upload_post(data: PostFormIn):
    """
    Upload a new post to the system.
    You must have the post:upload permission to do this.
    """
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
        create_snapshot(post, current_user)

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
