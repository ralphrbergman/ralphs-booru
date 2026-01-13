from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import OneOf

from .post import PostsOut

class BrowseIn(Schema):
    page = Integer()
    limit = Integer()
    sort = String(validate = OneOf(('asc', 'desc')))
    terms = String(load_default = '-nsfw')

class BrowseOut(PostsOut):
    pages = Integer()

class CountOut(Schema):
    count = Integer()
