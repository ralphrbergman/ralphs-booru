from apiflask import Schema
from apiflask.fields import Integer, List, Nested, String
from apiflask.validators import OneOf

from .base import BaseSchema

class TagIn(Schema):
    """ Represents an inbound tag object. """
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
    """ Represents an inbound multiple tag object. """
    post_id = Integer(required = True)
    tags = List(String(), required = True)

class TagOut(BaseSchema, TagIn):
    """ Represents an outbound tag object. """
    posts = List(Nested('PostOut', exclude = ('tags',)))

class TagsOut(Schema):
    """ Represents an outbound multiple tag object. """
    post_id = Integer(required = True)
    tags = List(Nested(TagOut, exclude = ('posts',)))

class TagBulkIn(Schema):
    """ Represents an inbound bulk tag as string object. """
    post_ids = List(Integer, required = True)
    tags = List(String(), required = True)

class TagBulkOut(Schema):
    """ Represents an outbound bulk tag object. """
    post_ids = List(Integer, required = True)
    tags = List(Nested(TagOut, exclude = ('posts',)))
