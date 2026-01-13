from apiflask import Schema
from apiflask.fields import Integer, List, Nested, String
from apiflask.validators import OneOf

from .post import PostOut

class PostsIn(Schema):
    posts = List(Integer, required = True)

    caption = String(required = False)
    directory = String(required = False)
    op = String(required = False)
    source = String(attribute = 'src', required = False)

    add_tags = List(String(), required = False)
    rem_tags = List(String(), required = False)
    tags = List(String(), required = False)

class PostsOut(Schema):
    posts = Nested(PostOut, many = True)

class BrowseIn(Schema):
    page = Integer()
    limit = Integer()
    sort = String(validate = OneOf(('asc', 'desc')))
    terms = String(load_default = '-nsfw')

class BrowseOut(PostsOut):
    pages = Integer()

class CountOut(Schema):
    count = Integer()
