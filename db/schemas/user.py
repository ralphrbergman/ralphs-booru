from apiflask.fields import Boolean, Integer, List, Nested, String

from .base import BaseSchema

class UserOut(BaseSchema):
    """ Represents an outside User schema. """
    avatar_name = String()
    name = String(required = True)
    comments = List(Nested('CommentIn'))
    posts = List(Nested(
        'PostOut',
        exclude = ('author',)),
        attribute = 'recent_posts'
    )
    role = String(required = True)

    # @properties.
    avatar = String(required = True)
    is_moderator = Boolean(required = True)
    profile_url = String(required = True)
    role_name = String(required = True)
    username = String(required = True)

    # @hybrid properties.
    level = Integer(required = True)
    points_until_levelup = Integer(required = True)
    score = Integer(required = True)
