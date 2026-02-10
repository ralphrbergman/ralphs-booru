from apiflask import Schema
from apiflask.fields import Integer, List, Nested, String

from api import DEFAULT_LIMIT, DEFAULT_SORT, DEFAULT_SORT_DIR
from .comment import CommentOut
from .post import PostOut
from .tag import TagOut

class BrowseIn(Schema):
    """ Represents inbound post browsing parameters object. """
    limit = Integer(load_default = DEFAULT_LIMIT)
    page = Integer(required = True)
    sort = String(load_default = DEFAULT_SORT)
    sort_by = String(load_default = DEFAULT_SORT_DIR)
    terms = String(load_default = None)

class BrowseOut(Schema):
    pages = Integer(required = True)

class CommentBrowse(BrowseOut):
    comments = List(Nested(CommentOut))

class PostBrowse(BrowseOut):
    posts = List(Nested(PostOut))

class TagBrowse(BrowseOut):
    tags = List(Nested(TagOut))
