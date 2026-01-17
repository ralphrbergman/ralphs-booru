from apiflask.fields import Boolean, List, Nested, String

from .base import BaseSchema

class UserOut(BaseSchema):
    """ Represents an outside User schema. """
    avatar_name = String()
    name = String(required = True)
    comments = List(Nested('CommentIn'))
    posts = List(Nested('PostOut', exclude = ('author',)))
    role = String(required = True)

    # @properties.
    avatar = String(required = True)
    is_moderator = Boolean(required = True)
    profile_url = String(required = True)
    role_name = String(required = True)
    username = String(required = True)
