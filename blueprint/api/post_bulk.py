from apiflask import APIBlueprint

from api import get_post
from api.decorators import moderator_only
from db import db
from db.schemas import BulkPostIn, BulkPostOut

post_bulk_bp = APIBlueprint(
    name = 'Bulk Post API',
    import_name = __name__,
    url_prefix = '/bulk'
)

@post_bulk_bp.patch('')
@post_bulk_bp.input(BulkPostIn, arg_name = 'data')
@post_bulk_bp.output(BulkPostOut)
@moderator_only
def update_bulk_post(data: BulkPostIn):
    posts = []

    for post_data in data['posts']:
        post = get_post(post_data['post_id'])

        del post_data['post_id']

        for key, value in post_data.items():
            setattr(post, key, value)

        posts.append(post)

    db.session.commit()
    return {
        'posts': posts
    }
