from functools import wraps

from flask import abort
from flask_login import current_user

def anonymous_only(callback):
    """
    Restricts view for anonymous users only.

    Args:
        callback: Route to restrict
    """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            return callback(*args, **kwargs)
        else:
            return abort(401)

    return wrapper

def moderator_only(callback):
    """
    Restricts view for users marked as moderator and up.

    Args:
        callback: Route to restrict
    """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        if current_user.is_moderator:
            return callback(*args, **kwargs)
        else:
            return abort(401)

    return wrapper
