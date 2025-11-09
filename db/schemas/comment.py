from apiflask.fields import Boolean, DateTime, Integer, String
from .post import PostIn

class CommentIn(PostIn):
    content = String()
    is_ui = Boolean(load_default = False)

class CommentOut(CommentIn):
    id = Integer()
    created = DateTime()
    author_id = Integer()
