from functools import wraps
from os import getenv
from typing import Callable

from apiflask import abort as api_abort
from flask import request, abort
from flask_babel import gettext
from flask_login import current_user
from sqlalchemy import select

from db import db

ALLOW_USERS = getenv('ALLOW_USERS') == 'true'
ALLOW_POSTS = getenv('ALLOW_POSTS') == 'true'

def _get_entity(model_class):
    v_args = request.view_args

    try:
        entity_id = list(v_args.values())[-1]
        entity_name = list(v_args.keys())[-1].strip('_id')
    except IndexError as exc:
        return

    entity = db.session.scalars(
        select(model_class)
        .where(model_class.id == entity_id)
    ).first()

    return entity, entity_name

def _level_required(LEVEL: int, model_class, abort_fn: Callable, *abort_args):
    def decorator(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            if current_user.level >= LEVEL or current_user.is_moderator or _get_entity(model_class):
                return callback(*args, **kwargs)
            
            return abort_fn(*abort_args)

        return wrapper

    return decorator

def api_level_required(LEVEL: int, model_class):
    return _level_required(LEVEL, model_class, api_abort, 401, gettext('Can\'t access this party yet boss.'))

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

def level_required(LEVEL: int, model_class):
    return _level_required(LEVEL, model_class, abort, 401)

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

def owner_only(model_class):
    """
    Restricts view for users that own a resource or are moderators.

    Args:
        callback: Route to restrict
    """
    def decorator(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            entity, entity_name = _get_entity(model_class)
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
