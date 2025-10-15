from flask import Blueprint, Response
from magic import from_buffer

from api import get_post

thumbnail_bp = Blueprint(
    name = 'Thumbnail',
    import_name = __name__
)

@thumbnail_bp.route('/thumbnail/<int:post_id>')
def thumbnail_route(post_id: int):
    post = get_post(post_id)
    thumb = post.thumbnail

    mime = from_buffer(thumb.data)
    return Response(response = thumb.data, mimetype = mime)
