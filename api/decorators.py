from functools import wraps
from os import getenv

from flask import request, abort
from flask_login import current_user

from .post import get_post

ALLOW_USERS = getenv('ALLOW_USERS') == 'true'
ALLOW_POSTS = getenv('ALLOW_POSTS') == 'true'

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

def appropriate_user_only(callback):
    """
    Restricts view for users that own a resource or are moderators.

    Args:
        callback: Route to restrict
    """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        json = request.get_json(silent = True)

        if not json or 'post_id' not in json:
            return abort(400)

        post = get_post(json.get('post_id'))

        if post and current_user.is_authenticated and current_user.is_moderator or post.author == current_user:
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
        if current_user.is_authenticated and current_user.is_moderator:
            return callback(*args, **kwargs)
        else:
            return abort(401)

    return wrapper

def post_protect(callback):
    """
    Restricts view if post management is
    not possible at the moment.

    Args:
        callback: Route to restrict
    """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        if ALLOW_POSTS or current_user.is_authenticated and current_user.is_moderator:
            return callback(*args, **kwargs)
        else:
            abort(403)

    return wrapper

def user_protect(callback):
    """
    Restricts view if user account management is
    not possible at the moment.

    Args:
        callback: Route to restrict
    """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        if ALLOW_USERS:
            return callback(*args, **kwargs)
        else:
            return abort(403)

    return wrapper
