from apiflask import Schema
from apiflask.fields import Integer, List, Nested, String
from apiflask.validators import OneOf

from .base import BaseSchema

class TagIn(Schema):
    name = String(required = True)
    type = String(
        required = True,
        validate = OneOf(
            ('general', 'artist', 'character', 'copyright', 'meta')
        )
    )
    desc = String(required = True)
    post_ids = List(Integer, load_only = True)

class TagOut(BaseSchema, TagIn):
    posts = List(Nested('PostOut', exclude = ('tags',)))
