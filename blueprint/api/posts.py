from apiflask import APIBlueprint

from api import browse_post
from db.schemas import BrowseIn, BrowseOut

posts_bp = APIBlueprint(
    name = 'Posts API',
    import_name = __name__,
    url_prefix = '/posts'
)

@posts_bp.route('')
@posts_bp.input(BrowseIn, arg_name = 'data', location = 'query')
@posts_bp.output(BrowseOut)
def posts_route(data: BrowseIn):
    limit = data['limit']
    page = data['page']
    sort_str = data['sort']
    terms = data['terms']

    posts = browse_post(limit, page, terms, sort_str)

    return {
        'pages': posts.pages,
        'posts': posts.items
    }
