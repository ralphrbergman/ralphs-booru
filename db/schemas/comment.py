from apiflask import Schema
from apiflask.fields import Integer, String

from .base import AuthorSchema, PostMixin, ScoreMixin

class CommentIn(Schema):
    content = String(required = True)
    post_id = Integer()

class CommentOut(AuthorSchema, CommentIn, PostMixin, ScoreMixin):
    pass
