from apiflask import Schema
from apiflask.fields import Integer, List, Nested, String
from apiflask.validators import OneOf

from .base import BaseSchema

class BareTagIn(Schema):
    name = String(required = True)

class TagIn(BareTagIn):
    name = String(required = True)
    type = String(
        required = True,
        validate = OneOf(
            ('general', 'artist', 'character', 'copyright', 'meta')
        )
    )
    desc = String(required = True)
    post_ids = List(Integer, load_only = True)

class TagsIn(Schema):
    post_id = Integer(required = True)
    tags = List(String(), required = True)

class TagOut(BaseSchema, TagIn):
    posts = List(Nested('PostOut', exclude = ('tags',)))

class TagsOut(Schema):
    post_id = Integer(required = True)
    tags = List(Nested(TagOut, exclude = ('posts',)))

class TagBulkIn(Schema):
    post_ids = List(Integer, required = True)
    tags = List(String(), required = True)

class TagBulkOut(Schema):
    post_ids = List(Integer, required = True)
    tags = List(Nested(TagOut, exclude = ('posts',)))
