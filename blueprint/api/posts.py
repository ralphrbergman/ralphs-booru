from apiflask import APIBlueprint

from api import browse_post, count_all_posts
from db.schemas import BrowseIn, BrowseOut, CountOut

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

    posts = browse_post(
        limit = limit,
        page = page,
        terms = terms,
        sort_str = sort_str
    )

    return {
        'pages': posts.pages,
        'posts': posts.items
    }

@posts_bp.route('/count')
@posts_bp.output(CountOut)
def count_route():
    return {'count': count_all_posts()}
