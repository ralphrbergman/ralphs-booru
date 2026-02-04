from apiflask import Schema
from apiflask.fields import List, Nested, String

from .post import PostIn, PostOut

class _BulkPostIn(PostIn):
    """ Represents an inbound post ID object. """
    post_id = String(required = True)

class BulkPostIn(Schema):
    """ Represents an inbound post ID list object. """
    # List of mixed strings and integers.
    posts = List(Nested(_BulkPostIn), required = True)

class BulkPostOut(Schema):
    """ Represents an outbound post list object. """
    posts = List(Nested(PostOut))
