from apiflask import Schema
from apiflask.fields import List, Nested, String

from .post import PostIn, PostOut

class _BulkPostIn(PostIn):
    post_id = String(required = True)

class BulkPostIn(Schema):
    # List of mixed strings and integers.
    posts = List(Nested(_BulkPostIn), required = True)

class BulkPostOut(Schema):
    posts = List(Nested(PostOut))
