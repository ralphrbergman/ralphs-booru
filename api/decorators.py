from functools import wraps
from os import getenv
from typing import Any, Callable

from apiflask import abort as api_abort
from flask import request, abort
from flask_babel import gettext
from flask_login import current_user
from sqlalchemy import select

from db import db

ALLOW_USERS = getenv('ALLOW_USERS') == 'true'
ALLOW_POSTS = getenv('ALLOW_POSTS') == 'true'

def _get_entity(model_class: Any):
    """
    Gets entity from given class and ID passed in request arguments.
    """
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

def _level_required(LEVEL: int, model_class: Any, abort_fn: Callable, *abort_args):
    """
    Restricts callback from users below a given level or 
    who aren't moderators, or who aren't the author of a given entity.
    """
    def decorator(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            if (current_user.level >= LEVEL
            or
            current_user.is_moderator
            or
            _get_entity(model_class)):
                return callback(*args, **kwargs)
            
            return abort_fn(*abort_args)

        return wrapper

    return decorator

def admin_only(callback):
    """
    Restricts callback from users who aren't an admin.
    """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.is_admin:
            return callback(*args, **kwargs)
        else:
            return abort(403)

    return wrapper

def api_level_required(LEVEL: int, model_class: Any):
    """
    Restricts API endpoint from people who are below the level,
    or who aren't moderators and don't own the resource.

    Args:
        LEVEL: Minimum level required
        model_class: Model to query for ownership attainment
    """
    return _level_required(
        LEVEL,
        model_class,
        api_abort,
        401,
        gettext('Can\'t access this party yet boss.')
    )

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
            return abort(403)

    return wrapper

def level_required(LEVEL: int, model_class: Any):
    """
    Restricts frontend endpoint from users who aren't of level,
    or who don't own the resource nor aren't moderators.

    Args:
        LEVEL: Minimum required level
        model_class: Model to query for ownership attainment
    """
    return _level_required(LEVEL, model_class, abort, 403)

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
            return abort(403)

    return wrapper

def owner_only(model_class: Any):
    """
    Restricts view for users that own a resource or are moderators.

    Args:
        model_class: Model to query for ownership attainment
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
                # "Entity" doesn't have 'author'.
                if entity.user_id == current_user.id:
                    return callback(*args, **kwargs)

            return abort(403)

        return wrapper
    return decorator

def owner_or_perm_required(model_class: Any, slug: str):
    """
    Restricts view to users owning the resource or
    having a permission slip.

    Args:
        model_class: Model to query for ownership attainment
        slug: Permission name
    """
    def decorator(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            entity, entity_name = _get_entity(model_class)
            if current_user.is_authenticated:
                uid = current_user.id

            kwargs[entity_name] = entity

            if (
                hasattr(current_user, 'id')
                and
                (hasattr(entity, 'user_id') and entity.user_id == uid
                or
                hasattr(entity, 'author_id') and entity.author_id == uid
                or
                current_user.has_permission(slug)
                or
                current_user.is_moderator)
                ):
                return callback(*args, **kwargs)

            return abort(403)

        return wrapper

    return decorator

def post_protect(callback):
    """
    Restricts view if post management is not possible at the moment.

    Args:
        callback: Route to restrict
    """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        if (ALLOW_POSTS or
            current_user.is_authenticated and current_user.is_moderator):
            return callback(*args, **kwargs)
        else:
            abort(403)

    return wrapper

def perm_required(slug: str):
    """
    Restricts view to users who have specified permission.

    Args:
        slug: Permission name
    """
    def decorator(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            if (current_user.is_authenticated and
            current_user.has_permission(slug)):
                return callback(*args, **kwargs)
            else:
                return abort(403)

        return wrapper

    return decorator

def user_protect(callback):
    """
    Restricts view if user account management is not possible at the moment.

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
