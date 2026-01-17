from functools import wraps
from os import getenv

from apiflask import abort
from flask import request
from flask_login import current_user
from sqlalchemy import select

from db import db

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

def owner_only(model_class):
    """
    Restricts view for users that own a resource or are moderators.

    Args:
        callback: Route to restrict
    """
    def decorator(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            v_args = request.view_args

            entity_id = list(v_args.values())[-1]
            entity_name = list(v_args.keys())[-1].strip('_id')

            entity = db.session.scalars(
                select(model_class)
                .where(model_class.id == entity_id)
            ).first()
            kwargs[entity_name] = entity

            try:
                if entity.author == current_user:
                    return callback(*args, **kwargs)
            except AttributeError as exc:
                # Entity doesn't have 'author'.
                if entity.user_id == current_user.id:
                    return callback(*args, **kwargs)

            return abort(401)

        return wrapper
    return decorator

def key_required(callback):
    """
    Restricts view to only be accessed by an API key.
    """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not current_user.is_authenticated or not auth_header:
            abort(401, message = 'Valid API key is necessary. Pass it to Authorization header.')

        return callback(*args, **kwargs)

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
