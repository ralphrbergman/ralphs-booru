from flask import Blueprint, Response, abort
from magic import from_buffer

from api import get_post

thumbnail_bp = Blueprint(
    name = 'Thumbnail',
    import_name = __name__
)

@thumbnail_bp.route('/thumbnail/<int:post_id>')
def thumbnail_route(post_id: int):
    post = get_post(post_id)

    try:
        thumb = post.thumbnail
    except AttributeError as exc:
        return abort(404)

    mime = from_buffer(thumb.data)
    return Response(response = thumb.data, mimetype = mime)
